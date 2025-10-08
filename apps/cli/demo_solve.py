#!/usr/bin/env python3
"""
Demo mode - Generate GPT solutions without submitting to Codeforces.
"""

import argparse
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from core.db import init_db, get_session
from core.models import Problem, TestCase, TestKind
from core.llm_gateway import gpt_generate_solution
from core.solution_saver import save_solution, get_next_iteration_number
from sqlmodel import select

def demo_solve_problem(contest_id: int, letter: str, attempts: int = 1):
    """Demonstrate the GPT solution generation process."""
    
    with get_session() as session:
        # Find the problem
        problem = session.exec(
            select(Problem).where(Problem.contest_id == contest_id, Problem.letter == letter)
        ).first()
        
        if not problem:
            print(f"❌ Problem {contest_id}{letter} not found!")
            return False
        
        # Get sample test cases
        test_cases = session.exec(
            select(TestCase).where(
                TestCase.problem_id == problem.id,
                TestCase.kind == TestKind.SAMPLE
            ).order_by(TestCase.idx)
        ).all()
        
        # Format samples for GPT
        samples = ""
        for tc in test_cases:
            samples += f"\n=== Sample #{tc.idx} ===\nInput:\n{tc.input_text}\nOutput:\n{tc.expected_output_text}\n"
        
        print(f"🎯 **Solving Problem {contest_id}{letter}**")
        print(f"Rating: {problem.rating or 'N/A'}")
        if problem.tags:
            import json
            tags = json.loads(problem.tags)
            print(f"Tags: {', '.join(tags[:5])}{'...' if len(tags) > 5 else ''}")
        print(f"Test Cases: {len(test_cases)}")
        print()
        
        print("📋 **Problem Statement Preview:**")
        # Show first few lines of the problem
        statement_lines = problem.statement_md.split('\n')[:10]
        for line in statement_lines:
            print(line)
        print("...\n")
        
        analysis = None
        previous_verdict = None
        
        # Get starting iteration number for this problem  
        base_iteration = get_next_iteration_number(problem.id)
        
        for attempt in range(1, attempts + 1):
            iteration_num = base_iteration + attempt - 1
            print(f"🤖 **Attempt {attempt}/{attempts}: GPT Generating Solution (Iteration {iteration_num})**")
            print("=" * 50)
            
            try:
                # Generate solution using GPT
                code = gpt_generate_solution(problem.statement_md, samples, analysis)
                
                # Save solution with metadata
                from datetime import datetime
                try:
                    solution_path = save_solution(
                        problem_id=problem.id,
                        code=code,
                        model="GPT-4",
                        iteration=iteration_num,
                        verdict=previous_verdict,
                        analysis=analysis,
                        timestamp=datetime.now()
                    )
                    print(f"💾 **Solution saved:** {solution_path}")
                except Exception as e:
                    print(f"⚠️  Warning: Could not save solution: {e}")
                
                print("\n✅ **Generated C++ Solution:**")
                print(code[:500] + "..." if len(code) > 500 else code)
                print()
                
                # Simulate what would happen next
                print("📤 **Next Steps (Demo Mode):**")
                print("1. ⚡ Would compile and test locally")
                print("2. 📤 Would submit to Codeforces") 
                print("3. ⏳ Would poll for verdict")
                print("4. 🔍 If failed, would analyze with DeepSeek")
                print("5. 🔄 Would generate improved solution")
                print()
                
                if attempt < attempts:
                    # Simulate failure for next attempt demo
                    previous_verdict = f"Wrong Answer on test {attempt + 2}"
                    print(f"🔍 **Simulated Verdict:** {previous_verdict}")
                    print("🔍 **Simulated Analysis (for next attempt):**")
                    analysis = f"- Consider edge cases with test case {attempt + 2}\n- Check algorithm correctness\n- Verify handling of boundary conditions"
                    print(analysis)
                    print()
                
                if attempt == attempts:
                    print("🎉 **Demo Complete!**")
                    print("The hybrid LLM system is working perfectly!")
                    print(f"📁 Check the solutions/{problem.id}/ directory for saved solutions!")
                    
                return True
                    
            except Exception as e:
                print(f"❌ Error generating solution: {e}")
                return False

def main():
    parser = argparse.ArgumentParser(description="Demo the GPT solution generation")
    parser.add_argument("--contest-id", type=int, required=True, help="Contest ID")
    parser.add_argument("--letter", type=str, required=True, help="Problem letter")
    parser.add_argument("--attempts", type=int, default=2, help="Number of attempts to simulate")
    
    args = parser.parse_args()
    
    print("🧪 **Hybrid LLM ICPC Solver - Demo Mode**")
    print("=" * 50)
    
    init_db()
    success = demo_solve_problem(args.contest_id, args.letter, args.attempts)
    
    if success:
        print("\n🎯 **Ready for Real Solving!**")
        print("Next steps:")
        print("1. Set up Codeforces authentication for real submissions")
        print("2. Add contest mappings for the problems you want to solve")
        print("3. Run with real submissions enabled")

if __name__ == "__main__":
    main()
