"""
OpenAI GPT Provider
"""
import os
from typing import List, Dict, Optional
import openai
from .base import BaseLLMProvider

class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider with persistent context"""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gpt-4"):
        api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        super().__init__(api_key, model_name)
        self.client = openai.OpenAI(api_key=api_key)
    
    def _make_api_call(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Make OpenAI API call"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 2000),
                **{k: v for k, v in kwargs.items() if k not in ["temperature", "max_tokens"]}
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def clean_code_response(self, response: str) -> str:
        """Extract only C++ code from response, removing explanations"""
        import re
        
        # Remove markdown code block markers
        response = re.sub(r'^```(?:cpp|c\+\+)?\s*\n', '', response, flags=re.MULTILINE)
        response = re.sub(r'\n```\s*$', '', response, flags=re.MULTILINE)
        
        # Find the last closing brace (end of main or last function)
        # This removes any explanatory text after the code
        lines = response.split('\n')
        last_brace_index = -1
        for i in range(len(lines) - 1, -1, -1):
            if '}' in lines[i]:
                last_brace_index = i
                break
        
        if last_brace_index != -1:
            # Keep only lines up to and including the last brace
            response = '\n'.join(lines[:last_brace_index + 1])
        
        return response.strip()
    
    def generate_solution(self, session_id: str, problem_statement: str, 
                         previous_attempts: Optional[List[Dict]] = None, **kwargs) -> str:
        """Generate C++ solution with context"""
        
        # Create context if it doesn't exist
        if not self.get_context(session_id):
            system_message = """You are an expert competitive programmer specializing in C++ solutions for ICPC problems.

Your task is to analyze problem statements and generate efficient, correct C++ solutions.

Guidelines:
1. Write clean, efficient C++ code
2. Use appropriate algorithms and data structures
3. Handle edge cases properly
4. Include necessary headers (#include<bits/stdc++.h>)
5. Use 'using namespace std;'
6. Implement main() function with proper I/O
7. Return ONLY the C++ code - NO explanations, NO markdown, NO comments after the code
8. End your response with the closing brace of main()

If this is a retry attempt, analyze the previous failure and fix the issues."""
            
            self.create_context(session_id, system_message)
        
        # Build user message
        user_message = f"Problem Statement:\n{problem_statement}\n\n"
        
        if previous_attempts:
            user_message += "Previous attempts and their failures:\n"
            for i, attempt in enumerate(previous_attempts, 1):
                user_message += f"\nAttempt {i}:\n"
                user_message += f"Code: {attempt.get('code', 'N/A')}\n"
                user_message += f"Verdict: {attempt.get('verdict', 'N/A')}\n"
                if attempt.get('error_details'):
                    user_message += f"Error Details: {attempt['error_details']}\n"
            user_message += "\nPlease fix the issues and provide an improved solution."
        else:
            user_message += "Please provide a C++ solution for this problem."
        
        # Get response and clean it
        response = self.chat(session_id, user_message, **kwargs)
        return self.clean_code_response(response)
