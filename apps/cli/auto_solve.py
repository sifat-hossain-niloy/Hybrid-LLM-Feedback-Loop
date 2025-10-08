#!/usr/bin/env python3
"""
Automated Problem Solver CLI

This script takes a problem ID like "2045_A" and automatically:
1. Loads the problem from the database
2. Generates a solution using GPT
3. Submits it to Codeforces
4. If not accepted, analyzes the failure and tries again
5. Repeats up to 3 times until accepted
6. Saves everything with proper folder structure

Usage:
    python3 apps/cli/auto_solve.py 2045_A
    python3 apps/cli/auto_solve.py 2045_A --max-attempts 5 --profile MyProfile
"""

import argparse
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.automated_solver import AutomatedProblemSolver


def main():
    parser = argparse.ArgumentParser(
        description="Automatically solve competitive programming problems using LLM feedback loop",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 apps/cli/auto_solve.py 2045_A
  python3 apps/cli/auto_solve.py 2072_F --max-attempts 5
  python3 apps/cli/auto_solve.py 1234_B --profile Sifat --verbose
        """
    )
    
    parser.add_argument(
        "problem_id",
        help="Problem identifier in format CONTEST_ID_LETTER (e.g., 2045_A)"
    )
    
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=3,
        help="Maximum number of solution attempts (default: 3)"
    )
    
    parser.add_argument(
        "--profile",
        default="Sifat",
        help="Chromium profile to use for Codeforces submission (default: Sifat)"
    )
    
    parser.add_argument(
        "--base-dir",
        default="problems_solved",
        help="Base directory for storing results (default: problems_solved)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Print header
    print("🤖 AUTOMATED PROBLEM SOLVER")
    print("=" * 50)
    print(f"📋 Problem ID: {args.problem_id}")
    print(f"🎯 Max Attempts: {args.max_attempts}")
    print(f"👤 Chromium Profile: {args.profile}")
    print(f"📁 Output Directory: {args.base_dir}")
    print("=" * 50)
    
    # Initialize solver
    solver = AutomatedProblemSolver(base_dir=args.base_dir)
    
    try:
        # Start solving
        result = solver.solve_problem(
            problem_id=args.problem_id,
            max_attempts=args.max_attempts,
            chromium_profile=args.profile
        )
        
        # Print results
        print("\n" + "🏆 FINAL RESULT" + "\n" + "=" * 60)
        
        if result.get("accepted", False):
            print("🎉 SUCCESS! Problem solved!")
            print(f"✅ Status: {result['status'].upper()}")
            print(f"🔄 Attempts: {result['successful_attempt']}/{result['total_attempts']}")
            print(f"⏱️  Duration: {result.get('total_duration_minutes', 0):.1f} minutes")
        else:
            print("💔 FAILED! Problem not solved")
            print(f"❌ Status: {result['status'].upper()}")
            print(f"🔄 Attempts: {result['total_attempts']}/{result['total_attempts']}")
            print(f"⏱️  Duration: {result.get('total_duration_minutes', 0):.1f} minutes")
        
        # Print statistics
        if result.get("statistics"):
            stats = result["statistics"]
            print(f"\n📊 STATISTICS:")
            print(f"   🔨 Compilation Errors: {stats['compilation_errors']}")
            print(f"   🐛 Runtime Errors: {stats['runtime_errors']}")
            print(f"   ❌ Wrong Answers: {stats['wrong_answers']}")
            print(f"   ⏰ Time Limit Exceeded: {stats['time_limit_exceeded']}")
            print(f"   💾 Memory Limit Exceeded: {stats['memory_limit_exceeded']}")
        
        # Print file locations
        problem_dir = Path(args.base_dir) / args.problem_id
        print(f"\n📁 FILES SAVED TO:")
        print(f"   📂 Main Directory: {problem_dir}")
        print(f"   💻 Solutions: {problem_dir}/solutions/")
        print(f"   📊 API Responses: {problem_dir}/api_responses/")
        print(f"   📋 Problem Info: {problem_dir}/problem_info.json")
        print(f"   📝 Solving Log: {problem_dir}/solving_log.json")
        print(f"   🎯 Final Result: {problem_dir}/final_result.json")
        
        if args.verbose:
            print(f"\n🔍 DETAILED RESULT:")
            print(json.dumps(result, indent=2))
        
        # Exit with appropriate code
        sys.exit(0 if result.get("accepted", False) else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(3)


if __name__ == "__main__":
    main()
