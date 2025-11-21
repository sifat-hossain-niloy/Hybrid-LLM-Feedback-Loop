import os
import re
from typing import Optional
import httpx
from core.config import OPENAI_API_KEY, DEEPSEEK_API_KEY

def load_prompt_template(filename: str) -> str:
    """Load a prompt template from the prompts directory."""
    prompt_path = os.path.join(os.path.dirname(__file__), 'prompts', filename)
    with open(prompt_path, 'r') as f:
        return f.read()

def clean_code_response(code: str) -> str:
    """Clean GPT response to remove markdown code blocks and extra formatting."""
    # Remove markdown code blocks
    code = re.sub(r'^```(?:cpp|c\+\+)?\n?', '', code, flags=re.MULTILINE)
    code = re.sub(r'\n?```\s*$', '', code, flags=re.MULTILINE)
    
    # Remove extra leading/trailing whitespace but preserve code formatting
    lines = code.split('\n')
    
    # Remove empty lines at the beginning and end
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    
    return '\n'.join(lines)

def gpt_generate_solution(problem_md: str, samples: str, hints: Optional[str] = None, previous_context: Optional[list] = None) -> str:
    """
    Generate C++ solution using OpenAI GPT with optional feedback from previous attempts
    
    Args:
        problem_md: Problem statement in markdown
        samples: Sample test cases
        hints: Optional hints from DeepSeek analysis
        previous_context: Previous failed attempts with verdicts and test results
    """
    if not OPENAI_API_KEY:
        return "// ERROR: OPENAI_API_KEY not configured"
    
    try:
        # Choose template based on context
        if previous_context and len(previous_context) > 0:
            template = load_prompt_template('gpt_fix_solution.txt')
        else:
            template = load_prompt_template('gpt_solution.txt')
        
        # Prepare hints text
        hints_text = f"\n\nPrevious Analysis:\n{hints}" if hints else ""
        
        # Prepare previous attempts context if available
        previous_attempts_text = ""
        if previous_context:
            previous_attempts_text = "\n\nPREVIOUS FAILED ATTEMPTS:\n"
            previous_attempts_text += "=" * 50 + "\n"
            
            for attempt in previous_context:
                previous_attempts_text += f"\nAttempt {attempt.get('attempt', 'N/A')}:\n"
                previous_attempts_text += f"Verdict: {attempt.get('verdict', 'Unknown')}\n"
                
                # Add test results if available
                if attempt.get('test_results'):
                    previous_attempts_text += "Failed Test Details:\n"
                    for i, test_result in enumerate(attempt['test_results'], 1):
                        if not test_result.get('passed', True):  # Only show failed tests
                            previous_attempts_text += f"  Test {i}:\n"
                            previous_attempts_text += f"    Input: {test_result.get('input', 'N/A')}\n"
                            previous_attempts_text += f"    Expected: {test_result.get('expected', 'N/A')}\n"
                            previous_attempts_text += f"    Got: {test_result.get('output', 'N/A')}\n"
                            if test_result.get('checker_message'):
                                previous_attempts_text += f"    Error: {test_result['checker_message']}\n"
                
                previous_attempts_text += f"\nPrevious Solution Code:\n```cpp\n{attempt.get('solution_code', 'N/A')}\n```\n"
                previous_attempts_text += "\n" + "-" * 40 + "\n"
        
        # Format the prompt
        if previous_context:
            prompt = template.format(
                problem_md=problem_md,
                samples=samples,
                hints=hints_text,
                previous_attempts=previous_attempts_text
            )
        else:
            prompt = template.format(
                problem_md=problem_md,
                samples=samples, 
                hints=hints_text
            )
        
        # Enhanced system message for feedback loop
        system_message = """You are an expert competitive programmer. Your task is to solve programming problems and learn from previous mistakes.

IMPORTANT INSTRUCTIONS:
1. If previous attempts are provided, carefully analyze what went wrong
2. Pay special attention to failed test cases and error messages
3. Fix the specific issues identified in previous attempts
4. Generate clean, efficient C++ code
5. Handle edge cases and constraints properly
6. Use appropriate data types and algorithms
7. Return ONLY the C++ code, no explanations or markdown

COMMON ISSUES TO AVOID:
- Off-by-one errors in loops and arrays
- Integer overflow (use long long when needed)
- Wrong algorithm complexity
- Missing edge cases
- Incorrect input/output format
- Logic errors in conditions"""
        
        # Call OpenAI API
        with httpx.Client() as client:
            response = client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4",
                    "messages": [
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 2000,
                    "temperature": 0.1  # Lower temp for fixes
                },
                timeout=60.0
            )
            
            if response.status_code == 200:
                result = response.json()
                code = result["choices"][0]["message"]["content"].strip()
                
                # Clean markdown code blocks if present
                code = clean_code_response(code)
                
                return code
            else:
                print(f"OpenAI API error: {response.status_code} - {response.text}")
                return f"// ERROR: OpenAI API call failed with status {response.status_code}"
                
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return f"// ERROR: {str(e)}"

def deepseek_diagnose(problem_md: str, code_cpp: str, cf_verdict: str, local_failures: str) -> str:
    """Analyze failed solution using DeepSeek."""
    if not DEEPSEEK_API_KEY:
        return "- ERROR: DEEPSEEK_API_KEY not configured"
    
    try:
        # Load and format prompt template
        template = load_prompt_template('deepseek_diagnose.txt')
        
        prompt = template.format(
            problem_md=problem_md,
            code_cpp=code_cpp,
            cf_verdict=cf_verdict,
            local_failures=local_failures
        )
        
        # Call DeepSeek API
        with httpx.Client() as client:
            response = client.post(
                "https://api.deepseek.com/chat/completions",
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.1
                },
                timeout=60.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                print(f"DeepSeek API error: {response.status_code} - {response.text}")
                return f"- ERROR: DeepSeek API call failed with status {response.status_code}"
                
    except Exception as e:
        print(f"Error calling DeepSeek API: {e}")
        return f"- ERROR: {str(e)}"
