#!/usr/bin/env python3
"""
Run automated solver with GPT-5 + DeepSeek-R1 workflow
"""

import sys
import json
from dotenv import load_dotenv
from core.automated_solver import AutomatedProblemSolver
from core.workflow_manager import WorkflowType

# Load environment variables from .env file
load_dotenv()

def main():
    print("="*70)
    print("🚀 AUTOMATED PROBLEM SOLVER - GPT-5 + DEEPSEEK-R1")
    print("="*70)
    print(f"Solution Generator: GPT-5")
    print(f"Debugging Critic: DeepSeek-R1-0528 (DeepSeek)")
    print(f"Max Attempts: 4")
    print(f"Mode: Automated (non-interactive)")
    print("="*70)
    print()
    
    # Get problem ID from command line or use default
    if len(sys.argv) > 1:
        problem_id = sys.argv[1]
    else:
        print("❌ Error: Problem ID required")
        print("Usage: python run_solver_gpt5_deepseek.py <problem_id>")
        print("Example: python run_solver_gpt5_deepseek.py 2046_B")
        sys.exit(1)
    
    print(f"📝 Problem: {problem_id}")
    print()
    
    # Create solver with GPT-5+DeepSeek workflow
    solver = AutomatedProblemSolver(
        base_dir="problems_solved",
        workflow_type=WorkflowType.GPT5_DEEPSEEK,
        interactive=True  # Keep browser visible for debugging
    )
    
    # Solve the problem
    result = solver.solve_problem(
        problem_id=problem_id,
        max_attempts=4,
        chromium_profile="Sifat"
    )
    
    print("\n" + "="*70)
    print("🎯 FINAL RESULT:")
    print("="*70)
    print(json.dumps(result, indent=2))
    print("="*70)
    
    # Exit with appropriate code
    if result.get("accepted"):
        print("\n✅ Problem SOLVED!")
        sys.exit(0)
    else:
        print("\n❌ Problem NOT solved after 4 attempts")
        sys.exit(1)

if __name__ == "__main__":
    main()
