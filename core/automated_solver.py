"""
Automated Problem Solver Core Module

This module handles the complete automated feedback loop for competitive programming:
1. Load problem from database
2. Generate solution using GPT
3. Submit to Codeforces 
4. Analyze results and iterate if needed
5. Manage complete folder structure and audit trail
"""

import os
import json
import re
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from sqlmodel import Session, select
from core.db import engine
from core.models import Problem, TestCase
from core.workflow_manager import WorkflowManager, WorkflowType


class AutomatedProblemSolver:
    """Complete automated problem solving system with feedback loop"""
    
    def __init__(self, base_dir: str = "problems_solved", workflow_type: WorkflowType = WorkflowType.GPT_MISTRAL, interactive: bool = True):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        self.workflow_manager = WorkflowManager()
        self.workflow_type = workflow_type
        self.interactive = interactive
        
    def solve_problem(self, problem_id: str, max_attempts: int = 3, chromium_profile: str = "Sifat") -> Dict:
        """
        Main solving function - orchestrates the complete feedback loop
        
        Args:
            problem_id: Problem identifier like "2045_A"
            max_attempts: Maximum number of solution attempts (default: 3)
            chromium_profile: Chromium profile for Codeforces submission
            
        Returns:
            Dict with complete solving results and statistics
        """
        print(f"🚀 Starting automated solving for problem {problem_id}")
        
        # Setup problem directory structure
        problem_dir = self._setup_problem_directory(problem_id)
        
        # Load problem from database
        problem_data = self._load_problem_data(problem_id)
        if not problem_data:
            return {"error": f"Problem {problem_id} not found in database"}
        
        # Save problem info
        self._save_problem_info(problem_dir, problem_data)
        
        # Create workflow session
        workflow_session = self.workflow_manager.create_session(self.workflow_type, problem_id)
        
        # Initialize solving log
        solving_log = {
            "problem_id": problem_id,
            "workflow_type": self.workflow_type.value,
            "workflow_session": workflow_session,
            "start_time": datetime.now().isoformat(),
            "max_attempts": max_attempts,
            "attempts": [],
            "final_status": "in_progress"
        }
        
        # Solving loop
        for attempt in range(1, max_attempts + 1):
            print(f"\n🔄 Attempt {attempt}/{max_attempts}")
            
            attempt_result = self._solve_attempt(
                problem_dir=problem_dir,
                problem_data=problem_data,
                attempt_number=attempt,
                previous_attempts=solving_log["attempts"],
                chromium_profile=chromium_profile,
                workflow_session=solving_log["workflow_session"]
            )
            
            solving_log["attempts"].append(attempt_result)
            
            # Save progress
            self._save_solving_log(problem_dir, solving_log)
            
            # Check if accepted
            if attempt_result.get("accepted", False):
                print(f"🎉 Problem {problem_id} ACCEPTED on attempt {attempt}!")
                solving_log["final_status"] = "accepted"
                solving_log["end_time"] = datetime.now().isoformat()
                break
            
            print(f"❌ Attempt {attempt} failed: {attempt_result.get('verdict', 'Unknown error')}")
            
            # Don't generate next solution if this was the last attempt
            if attempt < max_attempts:
                print(f"🔄 Preparing for attempt {attempt + 1}...")
                
                # Generate hint for next attempt using the configured hint provider
                if attempt_result.get("solution_code") and attempt_result.get("verdict"):
                    print(f"💡 Generating debugging hint...")
                    try:
                        hint = self._generate_hint(
                            problem_data, 
                            attempt_result, 
                            solving_log["workflow_session"],
                            problem_dir,
                            attempt
                        )
                        attempt_result["hint"] = hint
                        print(f"💡 Hint: {hint[:200]}..." if len(hint) > 200 else f"💡 Hint: {hint}")
                    except Exception as e:
                        print(f"⚠️ Failed to generate hint: {str(e)}")
                        attempt_result["hint_error"] = str(e)
        
        else:
            # All attempts failed
            print(f"💔 Problem {problem_id} NOT SOLVED after {max_attempts} attempts")
            solving_log["final_status"] = "failed"
            solving_log["end_time"] = datetime.now().isoformat()
        
        # Save final result
        final_result = self._create_final_result(solving_log)
        self._save_final_result(problem_dir, final_result)
        
        return final_result
    
    def _setup_problem_directory(self, problem_id: str) -> Path:
        """Create and return problem directory structure with workflow subfolder"""
        # Get workflow name for folder structure
        workflow_config = self.workflow_manager.WORKFLOWS[self.workflow_type]
        
        # Create sanitized workflow folder name (e.g., "gpt4_codestral", "gpt5_deepseek")
        workflow_folder = workflow_config.name.lower()\
            .replace(" + ", "_")\
            .replace("-", "")\
            .replace(" ", "_")\
            .replace("gpt_4", "gpt4")\
            .replace("gpt_5", "gpt5")
        
        # Create directory structure: problems_solved/2046_B/gpt4_codestral/
        problem_dir = self.base_dir / problem_id / workflow_folder
        
        # Create subdirectories
        (problem_dir / "solutions").mkdir(parents=True, exist_ok=True)
        (problem_dir / "api_responses").mkdir(parents=True, exist_ok=True)
        (problem_dir / "llm_responses").mkdir(parents=True, exist_ok=True)
        
        return problem_dir
    
    def _load_problem_data(self, problem_id: str) -> Optional[Dict]:
        """Load problem data from JSON file"""
        try:
            # Parse problem_id (e.g., "2135_A" -> contest_id=2135, letter="A")
            if "_" not in problem_id:
                print(f"❌ Invalid problem ID format: {problem_id}. Expected format: contest_id_letter (e.g., 2135_A)")
                return None
            
            contest_id_str, letter = problem_id.split("_", 1)
            try:
                contest_id = int(contest_id_str)
            except ValueError:
                print(f"❌ Invalid contest ID: {contest_id_str}")
                return None
            
            # Load from JSON file (e.g., problems/2135-A.json)
            json_filename = f"{contest_id}-{letter}.json"
            json_path = Path("problems") / json_filename
            
            if not json_path.exists():
                print(f"❌ Problem file not found: {json_path}")
                return None
            
            with open(json_path, 'r', encoding='utf-8') as f:
                problem_json = json.load(f)
            
            # Create a simple problem object from JSON
            class SimpleProblem:
                def __init__(self, data, contest_id, letter):
                    self.id = f"{contest_id}_{letter}"
                    self.contest_id = str(contest_id)
                    self.letter = letter
                    self.title = data.get("note", "Unknown").split('\n')[0][:50] if data.get("note") else f"Problem {letter}"
                    self.statement_md = data.get("statement", "")
                    self.rating = data.get("rating")
                    self.tags = json.dumps(data.get("tags", []))
                    self.input_spec = data.get("input_specification", "")
                    self.output_spec = data.get("output_specification", "")
            
            problem = SimpleProblem(problem_json, contest_id, letter)
            
            # Extract test cases from sample_tests
            test_cases = []
            for sample in problem_json.get("sample_tests", []):
                class SimpleTestCase:
                    def __init__(self, input_text, output_text):
                        self.input_text = input_text
                        self.expected_output_text = output_text
                        self.kind = type('Kind', (), {'value': 'sample'})()
                
                test_cases.append(SimpleTestCase(
                    sample.get("input", ""),
                    sample.get("output", "")
                ))
            
            print(f"✅ Loaded problem {problem_id} from JSON file")
            
            return {
                "problem": problem,
                "test_cases": test_cases,
                "contest_id": contest_id,
                "letter": letter
            }
                
        except Exception as e:
            print(f"❌ Error loading problem data: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _save_problem_info(self, problem_dir: Path, problem_data: Dict):
        """Save problem information to JSON file"""
        problem = problem_data["problem"]
        test_cases = problem_data["test_cases"]
        
        problem_info = {
            "problem_id": problem.id,
            "contest_id": problem.contest_id,
            "letter": problem.letter,
            "title": problem.title,
            "statement": problem.statement_md,
            "rating": problem.rating,
            "tags": json.loads(problem.tags) if isinstance(problem.tags, str) else problem.tags,
            "sample_tests": [
                {
                    "input": tc.input_text,
                    "output": tc.expected_output_text,
                    "kind": tc.kind.value if hasattr(tc.kind, 'value') else 'sample'
                }
                for tc in test_cases
            ],
            "created_at": datetime.now().isoformat()
        }
        
        with open(problem_dir / "problem_info.json", "w", encoding="utf-8") as f:
            json.dump(problem_info, f, indent=2, ensure_ascii=False)
    
    def _solve_attempt(self, problem_dir: Path, problem_data: Dict, attempt_number: int, 
                       previous_attempts: List[Dict], chromium_profile: str, workflow_session: str) -> Dict:
        """Execute a single solving attempt"""
        
        attempt_start = datetime.now()
        problem = problem_data["problem"]
        
        # Step 1: Generate solution
        print(f"🧠 Generating solution with GPT...")
        solution_result = self._generate_solution(problem_data, previous_attempts, workflow_session, problem_dir, attempt_number)
        
        if "error" in solution_result:
            print(f"❌ Error generating solution: {solution_result['error']}")
            return {
                "attempt": attempt_number,
                "timestamp": attempt_start.isoformat(),
                "duration_seconds": (datetime.now() - attempt_start).total_seconds(),
                "error": solution_result["error"],
                "accepted": False
            }
        
        # Step 2: Save solution file
        solution_filename = f"{problem.contest_id}_{problem.letter}_Solution_{attempt_number}.cpp"
        solution_path = problem_dir / "solutions" / solution_filename
        
        with open(solution_path, "w", encoding="utf-8") as f:
            f.write(solution_result["solution"])
        
        print(f"💾 Solution saved: {solution_path}")
        
        # Step 3: Submit to Codeforces
        print(f"📤 Submitting to Codeforces...")
        submission_result = self._submit_solution(solution_path, chromium_profile)
        
        if "error" in submission_result:
            return {
                "attempt": attempt_number,
                "timestamp": attempt_start.isoformat(),
                "duration_seconds": (datetime.now() - attempt_start).total_seconds(),
                "solution_file": solution_filename,
                "solution_code": solution_result["solution"],
                "submission_error": submission_result["error"],
                "accepted": False
            }
        
        # Step 4: Move API response to problem directory
        if "api_response_file" in submission_result:
            self._move_api_response(submission_result["api_response_file"], problem_dir / "api_responses")
        
        # Step 5: Analyze result
        verdict = submission_result.get("verdict", "Unknown")
        accepted = "accepted" in verdict.lower() or verdict == "OK"
        
        return {
            "attempt": attempt_number,
            "timestamp": attempt_start.isoformat(),
            "duration_seconds": (datetime.now() - attempt_start).total_seconds(),
            "solution_file": solution_filename,
            "solution_code": solution_result["solution"],
            "submission_id": submission_result.get("submission_id"),
            "verdict": verdict,
            "accepted": accepted,
            "api_response": submission_result.get("api_response"),
            "detailed_api_response": submission_result.get("detailed_api_response"),  # Facebox data
            "test_results": submission_result.get("test_results", [])
        }
    
    def _generate_solution(self, problem_data: Dict, previous_attempts: List[Dict], workflow_session: str, problem_dir: Path, attempt_number: int) -> Dict:
        """Generate solution using GPT with context from previous attempts"""
        
        problem = problem_data["problem"]
        test_cases = problem_data["test_cases"]
        
        # Prepare sample tests text
        sample_tests_text = ""
        sample_tests = []
        for i, tc in enumerate([tc for tc in test_cases if tc.kind.value == "sample"], 1):
            sample_tests_text += f"Sample Input {i}:\n{tc.input_text}\n\n"
            sample_tests_text += f"Sample Output {i}:\n{tc.expected_output_text}\n\n"
            sample_tests.append({"input": tc.input_text, "output": tc.expected_output_text})
        
        # Prepare previous attempt context if available (ONLY THE MOST RECENT)
        previous_context = []
        if previous_attempts:
            # Only use the most recent failed attempt
            most_recent = previous_attempts[-1]
            if not most_recent.get("accepted", False):
                # Parse API response for detailed test results
                test_results = self._extract_test_results_from_api(most_recent.get("api_response"))
                
                previous_context.append({
                    "attempt": most_recent["attempt"],
                    "solution_code": most_recent.get("solution_code", ""),
                    "verdict": most_recent.get("verdict", "Unknown"),
                    "test_results": test_results,
                    "hint": most_recent.get("hint", "")  # Include the debugging hint!
                })
        
        try:
            # Build complete problem statement (statement_md already contains formatted problem)
            problem_statement = f"""{problem.statement_md}

Sample Tests:
{sample_tests_text}"""
            
            # Save the FULL prompt being sent
            prompt_file = problem_dir / "llm_responses" / f"solution_attempt_{attempt_number}_PROMPT.txt"
            with open(prompt_file, "w", encoding="utf-8") as f:
                f.write(f"=== PROMPT SENT TO LLM (Solution Generation) ===\n")
                f.write(f"Attempt: {attempt_number}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"Model: {self.workflow_manager.WORKFLOWS[self.workflow_type].solution_model}\n")
                f.write(f"Has Previous Context: {bool(previous_context)}\n")
                f.write(f"\n{'='*70}\n")
                f.write(f"PROBLEM STATEMENT:\n")
                f.write(f"{'='*70}\n\n")
                f.write(problem_statement)
                if previous_context:
                    ctx = previous_context[0]  # Only one context (most recent)
                    f.write(f"\n\n{'='*70}\n")
                    f.write(f"PREVIOUS ATTEMPT (Attempt {ctx['attempt']}):\n")
                    f.write(f"{'='*70}\n\n")
                    f.write(f"Verdict: {ctx['verdict']}\n")
                    f.write(f"\nPrevious Code:\n{ctx['solution_code']}\n")
                    if ctx.get('test_results'):
                        f.write(f"\n📊 Test Results ({len(ctx['test_results'])} tests shown):\n")
                        for tr in ctx['test_results'][:3]:  # Show first 3 tests
                            f.write(f"  - Verdict: {tr.get('verdict', 'N/A')}\n")
                    if ctx.get('hint'):
                        f.write(f"\n🔍 DEBUGGING HINT:\n{ctx['hint']}\n")
                f.write(f"\n\n{'='*70}\n")
            print(f"💾 Prompt saved: {prompt_file}")
            
            # Use workflow manager to generate solution
            raw_solution = self.workflow_manager.generate_solution(
                workflow_session,
                problem_statement,
                previous_context if previous_context else None
            )
            
            # Save raw LLM response
            llm_response_file = problem_dir / "llm_responses" / f"solution_attempt_{attempt_number}_RESPONSE.txt"
            with open(llm_response_file, "w", encoding="utf-8") as f:
                f.write(f"=== RAW LLM RESPONSE (Solution Generation) ===\n")
                f.write(f"Attempt: {attempt_number}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"Model: {self.workflow_manager.WORKFLOWS[self.workflow_type].solution_model}\n")
                f.write(f"Has Previous Context: {bool(previous_context)}\n")
                f.write(f"\n{'='*70}\n\n")
                f.write(raw_solution)
            print(f"💾 Response saved: {llm_response_file}")
            
            # Add header comment to solution
            header_comment = self._generate_solution_header(problem, len(previous_attempts) + 1)
            final_solution = header_comment + "\n\n" + raw_solution
            
            return {"solution": final_solution, "raw_response": raw_solution}
            
        except Exception as e:
            return {"error": f"Solution generation failed: {str(e)}"}
    
    def _generate_hint(self, problem_data: Dict, failed_attempt: Dict, workflow_session: str, problem_dir: Path, attempt_number: int) -> str:
        """Generate debugging hint using the configured hint provider"""
        
        problem = problem_data["problem"]
        test_cases = problem_data["test_cases"]
        
        # Prepare sample tests text
        sample_tests_text = ""
        for i, tc in enumerate([tc for tc in test_cases if tc.kind.value == "sample"], 1):
            sample_tests_text += f"Sample Input {i}:\n{tc.input_text}\n\n"
            sample_tests_text += f"Sample Output {i}:\n{tc.expected_output_text}\n\n"
        
        # Build complete problem statement (statement_md already contains formatted problem)
        problem_statement = f"""{problem.statement_md}

Sample Tests:
{sample_tests_text}"""
        
        # Extract error details from API response or facebox
        error_details = ""
        
        # First try parsed_api_response (from API interception - most reliable)
        # Check both "api_response" (from file load) and "detailed_api_response" (from stdout capture)
        api_data = failed_attempt.get("api_response") or failed_attempt.get("detailed_api_response")
        
        if api_data and api_data.get("parsed_api_response"):
            parsed_api = api_data["parsed_api_response"]
            test_count = int(parsed_api.get("testCount", 0))
            
            if test_count > 0:
                error_details += "Detailed Test Results from Codeforces API:\n\n"
                
                for i in range(1, min(test_count + 1, 11)):  # Limit to first 10 tests
                    error_details += f"{'='*50}\n"
                    error_details += f"Test #{i}:\n"
                    
                    verdict = parsed_api.get(f"verdict#{i}", "Unknown")
                    error_details += f"Verdict: {verdict}\n"
                    
                    input_data = parsed_api.get(f"input#{i}", "")
                    if input_data:
                        error_details += f"\nInput:\n{input_data}\n"
                    
                    output_data = parsed_api.get(f"output#{i}", "")
                    if output_data:
                        error_details += f"\nYour Output:\n{output_data}\n"
                    
                    answer_data = parsed_api.get(f"answer#{i}", "")
                    if answer_data:
                        error_details += f"\nExpected Answer:\n{answer_data}\n"
                    
                    checker_log = parsed_api.get(f"checkerStdoutAndStderr#{i}", "")
                    if checker_log:
                        error_details += f"\nChecker Comment:\n{checker_log}\n"
                    
                    time_consumed = parsed_api.get(f"timeConsumed#{i}", "")
                    memory_consumed = parsed_api.get(f"memoryConsumed#{i}", "")
                    if time_consumed:
                        error_details += f"\nTime: {time_consumed} ms\n"
                    if memory_consumed:
                        error_details += f"Memory: {memory_consumed} KB\n"
                    
                    error_details += f"{'='*50}\n\n"
                
                if test_count > 10:
                    error_details += f"\n(... and {test_count - 10} more tests)\n\n"
        
        # Fallback to facebox test_results (if API parsing didn't work)
        elif api_data and api_data.get("test_results"):
            error_details += "Detailed Test Results from Facebox:\n\n"
            test_results = api_data["test_results"]
            
            for i, test in enumerate(test_results[:10], 1):
                error_details += f"{'='*50}\n"
                error_details += f"Test {test.get('test_id', i)}:\n"
                error_details += f"Verdict: {test.get('verdict', 'Unknown')}\n"
                
                if test.get('input'):
                    error_details += f"\nInput:\n{test['input']}\n"
                if test.get('output'):
                    error_details += f"\nYour Output:\n{test['output']}\n"
                if test.get('answer'):
                    error_details += f"\nExpected Answer:\n{test['answer']}\n"
                if test.get('checker_log'):
                    error_details += f"\nChecker Comment:\n{test['checker_log']}\n"
                
                error_details += f"{'='*50}\n\n"
        
        # Fallback to old test_results format
        elif failed_attempt.get("test_results"):
            error_details += "Test Results:\n"
            for test in failed_attempt["test_results"]:
                error_details += f"Test {test.get('test_number', '?')}: {test.get('verdict', 'Unknown')}\n"
                if test.get('expected_output') and test.get('actual_output'):
                    error_details += f"  Expected: {test['expected_output']}\n"
                    error_details += f"  Got: {test['actual_output']}\n"
        
        if failed_attempt.get("submission_error"):
            error_details += f"\nSubmission Error: {failed_attempt['submission_error']}"
        
        if not error_details:
            error_details = "No detailed error information available"
        
        # Save the FULL hint prompt being sent
        hint_prompt_file = problem_dir / "llm_responses" / f"hint_after_attempt_{attempt_number}_PROMPT.txt"
        with open(hint_prompt_file, "w", encoding="utf-8") as f:
            f.write(f"=== FULL PROMPT SENT TO LLM (Hint Generation) ===\n")
            f.write(f"After Attempt: {attempt_number}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Model: {self.workflow_manager.WORKFLOWS[self.workflow_type].hint_model}\n")
            f.write(f"Verdict: {failed_attempt.get('verdict', 'Unknown')}\n")
            f.write(f"\n{'='*70}\n")
            f.write(f"SYSTEM MESSAGE:\n")
            f.write(f"{'='*70}\n\n")
            f.write("You are a code debugging assistant specializing in competitive programming.\n")
            f.write("Identify logical errors, edge cases, or inefficiencies.\n")
            f.write("Provide concise, targeted feedback.\n\n")
            f.write(f"{'='*70}\n")
            f.write(f"USER MESSAGE:\n")
            f.write(f"{'='*70}\n\n")
            f.write(f"Problem Statement:\n{problem_statement}\n\n")
            f.write(f"Failed Solution:\n{failed_attempt.get('solution_code', '')}\n\n")
            f.write(f"Verdict: {failed_attempt.get('verdict', 'Unknown')}\n\n")
            f.write(f"Error Details:\n{error_details}\n\n")
            f.write(f"{'='*70}\n")
        print(f"💾 Hint prompt saved: {hint_prompt_file}")
        
        # Use workflow manager to generate hint
        raw_hint = self.workflow_manager.generate_hint(
            workflow_session,
            problem_statement,
            failed_attempt.get("solution_code", ""),
            failed_attempt.get("verdict", "Unknown"),
            error_details
        )
        
        # Save raw LLM hint response
        llm_hint_file = problem_dir / "llm_responses" / f"hint_after_attempt_{attempt_number}_RESPONSE.txt"
        with open(llm_hint_file, "w", encoding="utf-8") as f:
            f.write(f"=== RAW LLM RESPONSE (Hint Generation) ===\n")
            f.write(f"After Attempt: {attempt_number}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Model: {self.workflow_manager.WORKFLOWS[self.workflow_type].hint_model}\n")
            f.write(f"Verdict: {failed_attempt.get('verdict', 'Unknown')}\n")
            f.write(f"\n{'='*70}\n\n")
            f.write(raw_hint)
        print(f"💾 Hint response saved: {llm_hint_file}")
        
        return raw_hint
    
    def _extract_test_results_from_api(self, api_response: Optional[Dict]) -> List[Dict]:
        """Extract detailed test results from API response"""
        
        if not api_response:
            return []
        
        # Try to get parsed API response
        parsed_api = api_response.get("parsed_api_response")
        if not parsed_api:
            return []
        
        test_results = []
        test_count = int(parsed_api.get("testCount", "0"))
        
        for i in range(1, test_count + 1):
            test_result = {
                "test_number": i,
                "input": parsed_api.get(f"input#{i}", "N/A"),
                "expected": parsed_api.get(f"answer#{i}", "N/A"),
                "output": parsed_api.get(f"output#{i}", "N/A"),
                "verdict": parsed_api.get(f"verdict#{i}", "Unknown"),
                "time_ms": parsed_api.get(f"timeConsumed#{i}", "N/A"),
                "memory_kb": parsed_api.get(f"memoryConsumed#{i}", "N/A"),
                "checker_message": parsed_api.get(f"checkerStdoutAndStderr#{i}", ""),
                "passed": parsed_api.get(f"accepted#{i}", "false") == "true"
            }
            test_results.append(test_result)
        
        return test_results
    
    def _generate_solution_header(self, problem: Problem, attempt_number: int) -> str:
        """Generate header comment for solution file"""
        
        workflow_config = self.workflow_manager.WORKFLOWS[self.workflow_type]
        return f"""/*
 * Problem: {problem.contest_id}_{problem.letter} - {problem.title}
 * Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
 * Workflow: {workflow_config.name}
 * Solution Model: {workflow_config.solution_model}
 * Debugging Critic: {workflow_config.hint_model}
 * Iteration: {attempt_number}
 * Rating: {problem.rating or "Unrated"}
 */"""
    
    def _submit_solution(self, solution_path: Path, chromium_profile: str) -> Dict:
        """Submit solution using existing Chromium-based submission system"""
        
        try:
            # Use the existing submit_existing_chromium.py script
            import sys
            python_executable = sys.executable  # Use the same Python that's running this script
            cmd = [
                python_executable, 
                "apps/cli/submit_existing_chromium.py",
                str(solution_path),
                "--profile", chromium_profile,
                "--no-interactive"  # Always use --no-interactive when running as subprocess
            ]
            
            # Note: self.interactive only controls whether we keep browser visible for manual review,
            # but we always use --no-interactive to avoid blocking on input() calls in subprocess
            
            print(f"🔧 Running: {' '.join(cmd)}")
            
            # Capture output
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                return {
                    "error": f"Submission failed with code {result.returncode}",
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            
            # Parse output to extract key information
            output_lines = result.stdout.strip().split('\n')
            submission_info = self._parse_submission_output(output_lines)
            
            return submission_info
            
        except subprocess.TimeoutExpired:
            return {"error": "Submission timed out after 5 minutes"}
        except Exception as e:
            return {"error": f"Submission error: {str(e)}"}
    
    def _parse_submission_output(self, output_lines: List[str]) -> Dict:
        """Parse submission script output to extract key information"""
        
        info = {}
        found_api_response = None
        capturing_detailed_response = False
        detailed_response_lines = []
        
        for line in output_lines:
            # Capture detailed API response between markers
            if "📦 DETAILED_API_RESPONSE_START" in line:
                capturing_detailed_response = True
                detailed_response_lines = []
                continue
            elif "📦 DETAILED_API_RESPONSE_END" in line:
                capturing_detailed_response = False
                if detailed_response_lines:
                    try:
                        detailed_json = '\n'.join(detailed_response_lines)
                        info["detailed_api_response"] = json.loads(detailed_json)
                        print(f"✅ Captured detailed facebox data with {info['detailed_api_response'].get('test_count', 0)} tests")
                    except Exception as e:
                        print(f"⚠️  Could not parse detailed API response: {e}")
                continue
            
            if capturing_detailed_response:
                detailed_response_lines.append(line)
                continue
            
            # Extract submission ID
            if "Submission ID:" in line or "submission ID:" in line:
                match = re.search(r'(?:S|s)ubmission ID:\s*(\d+)', line)
                if match:
                    info["submission_id"] = match.group(1)
            
            # Extract verdict
            if "Final verdict:" in line or "Verdict:" in line or "final verdict:" in line:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    verdict = parts[1].strip()
                    # Clean up verdict text
                    verdict = re.sub(r'[^\w\s]', ' ', verdict).strip()
                    info["verdict"] = verdict
            
            # Extract API response file
            if "saved to:" in line and ("api_responses/" in line or ".json" in line):
                match = re.search(r'saved to:\s*([^\s]+\.json)', line)
                if match:
                    info["api_response_file"] = match.group(1)
            
            # Look for comprehensive results data
            if "Comprehensive results saved to:" in line:
                match = re.search(r'saved to:\s*([^\s]+\.json)', line)
                if match:
                    info["api_response_file"] = match.group(1)
        
        # Try to load API response if file path was found
        if "api_response_file" in info:
            try:
                api_file = Path(info["api_response_file"])
                if api_file.exists():
                    with open(api_file, 'r', encoding='utf-8') as f:
                        api_data = json.load(f)
                        info["api_response"] = api_data
                        
                        # Extract verdict from API response if not found in output
                        if "verdict" not in info and "parsed_api_response" in api_data:
                            parsed = api_data["parsed_api_response"]
                            if "verdict" in parsed:
                                verdict_html = parsed["verdict"]
                                if "accepted" in verdict_html.lower():
                                    info["verdict"] = "ACCEPTED"
                                else:
                                    # Extract text from HTML
                                    clean_verdict = re.sub(r'<[^>]+>', ' ', verdict_html).strip()
                                    info["verdict"] = clean_verdict
            except Exception as e:
                print(f"⚠️  Could not load API response file: {e}")
        
        return info
    
    def _move_api_response(self, source_file: str, target_dir: Path):
        """Move API response file to problem directory"""
        
        source_path = Path(source_file)
        if source_path.exists():
            target_path = target_dir / source_path.name
            source_path.rename(target_path)
            print(f"📁 Moved API response: {target_path}")
    
    def _save_solving_log(self, problem_dir: Path, solving_log: Dict):
        """Save current solving progress"""
        
        with open(problem_dir / "solving_log.json", "w", encoding="utf-8") as f:
            json.dump(solving_log, f, indent=2, ensure_ascii=False)
    
    def _create_final_result(self, solving_log: Dict) -> Dict:
        """Create final result summary"""
        
        total_attempts = len(solving_log["attempts"])
        accepted = solving_log["final_status"] == "accepted"
        
        final_result = {
            "problem_id": solving_log["problem_id"],
            "status": solving_log["final_status"],
            "accepted": accepted,
            "total_attempts": total_attempts,
            "start_time": solving_log["start_time"],
            "end_time": solving_log.get("end_time"),
            "total_duration_minutes": 0,
            "successful_attempt": None,
            "best_verdict": None,
            "statistics": {
                "compilation_errors": 0,
                "runtime_errors": 0,
                "wrong_answers": 0,
                "time_limit_exceeded": 0,
                "memory_limit_exceeded": 0
            }
        }
        
        # Calculate duration
        if solving_log.get("end_time"):
            start = datetime.fromisoformat(solving_log["start_time"])
            end = datetime.fromisoformat(solving_log["end_time"])
            final_result["total_duration_minutes"] = (end - start).total_seconds() / 60
        
        # Analyze attempts
        for attempt in solving_log["attempts"]:
            verdict = attempt.get("verdict", "").lower()
            
            if attempt.get("accepted"):
                final_result["successful_attempt"] = attempt["attempt"]
                final_result["best_verdict"] = "ACCEPTED"
            
            # Count error types
            if "compilation error" in verdict:
                final_result["statistics"]["compilation_errors"] += 1
            elif "runtime error" in verdict:
                final_result["statistics"]["runtime_errors"] += 1
            elif "wrong answer" in verdict:
                final_result["statistics"]["wrong_answers"] += 1
            elif "time limit" in verdict:
                final_result["statistics"]["time_limit_exceeded"] += 1
            elif "memory limit" in verdict:
                final_result["statistics"]["memory_limit_exceeded"] += 1
        
        return final_result
    
    def _save_final_result(self, problem_dir: Path, final_result: Dict):
        """Save final solving result"""
        
        with open(problem_dir / "final_result.json", "w", encoding="utf-8") as f:
            json.dump(final_result, f, indent=2, ensure_ascii=False)


def main():
    """Example usage"""
    solver = AutomatedProblemSolver()
    
    # Example: Solve problem 2045_A
    result = solver.solve_problem(
        problem_id="2045_A",
        max_attempts=3,
        chromium_profile="Sifat"
    )
    
    print("\n" + "="*60)
    print("🎯 FINAL RESULT:")
    print("="*60)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
