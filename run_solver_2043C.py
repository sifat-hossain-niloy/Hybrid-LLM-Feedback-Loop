#!/usr/bin/env python3
"""
Run automated solver for problem 2043-C with GPT-4+Mistral workflow
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
    print("🚀 AUTOMATED PROBLEM SOLVER")
    print("="*70)
    print(f"Problem: 2043-C")
    print(f"Workflow: GPT-4 + Codestral-2508 (Mistral)")
    print(f"Max Attempts: 3")
    print(f"Mode: Interactive (Chrome visible)")
    print("="*70)
    print()
    
    # Create solver with GPT-4+Mistral workflow in interactive mode
    solver = AutomatedProblemSolver(
        base_dir="problems_solved",
        workflow_type=WorkflowType.GPT_MISTRAL,
        interactive=True  # Show Chrome window and allow manual interaction
    )
    
    # Solve the problem
    result = solver.solve_problem(
        problem_id="2043_C",
        max_attempts=3,
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
        print("\n❌ Problem NOT solved after 3 attempts")
        sys.exit(1)

if __name__ == "__main__":
    main()

