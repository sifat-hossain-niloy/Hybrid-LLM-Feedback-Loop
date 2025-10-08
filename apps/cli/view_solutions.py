#!/usr/bin/env python3
"""
View and manage saved solutions.
"""

import argparse
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from core.solution_saver import get_solution_summary, list_all_solved_problems

def view_problem_solutions(problem_id: str):
    """View all solutions for a specific problem."""
    summary = get_solution_summary(problem_id)
    
    if summary["total_attempts"] == 0:
        print(f"❌ No solutions found for problem {problem_id}")
        return
    
    print(f"📋 **Problem {problem_id}** - {summary['total_attempts']} solutions")
    print("=" * 60)
    
    for i, solution in enumerate(summary["solutions"]):
        print(f"\n🔄 **Iteration {solution['iteration']}** ({solution['timestamp'][:19]})")
        print(f"   Model: {solution['model']}")
        
        if solution.get('verdict'):
            print(f"   Previous Verdict: {solution['verdict']}")
        
        if solution.get('analysis'):
            print(f"   Analysis: {solution['analysis'][:100]}...")
        
        print(f"   Code Length: {solution['code_length']} characters")
        print(f"   File: {solution['filename']}")
        
        # Ask if user wants to see the code
        if i < 3:  # Show first few automatically
            show_code = input(f"   👀 View code? (y/n): ").lower().strip()
            if show_code in ['y', 'yes']:
                show_solution_code(problem_id, solution['iteration'])

def show_solution_code(problem_id: str, iteration: int):
    """Show the actual code for a solution."""
    solution_file = f"solutions/{problem_id}/solution_{iteration}.cpp"
    
    if os.path.exists(solution_file):
        print("\n" + "="*50)
        print(f"📄 **Solution {iteration} Code:**")
        print("="*50)
        
        with open(solution_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)
        
        print("="*50 + "\n")
    else:
        print(f"❌ Solution file not found: {solution_file}")

def list_all_solutions():
    """List all problems with solutions."""
    problems = list_all_solved_problems()
    
    if not problems:
        print("📭 No solutions found. Generate some solutions first!")
        print("Try: python apps/cli/demo_solve.py --contest-id 2051 --letter E")
        return
    
    print(f"📚 **All Solved Problems** ({len(problems)} problems)")
    print("=" * 60)
    
    for problem in problems:
        print(f"🎯 {problem['problem_id']} - {problem['total_attempts']} attempts")
        
        if problem['solutions']:
            latest = problem['solutions'][-1]
            print(f"   Latest: {latest['timestamp'][:19]} ({latest['model']})")
            
            if latest.get('verdict'):
                verdict_emoji = "🎉" if "accept" in latest['verdict'].lower() else "❌" 
                print(f"   {verdict_emoji} Last Verdict: {latest['verdict']}")
        print()

def show_statistics():
    """Show overall statistics."""
    problems = list_all_solved_problems()
    
    if not problems:
        print("📊 No statistics available yet.")
        return
    
    total_problems = len(problems)
    total_attempts = sum(p['total_attempts'] for p in problems)
    
    # Count by verdict (if available)
    accepted = 0
    failed = 0
    
    for problem in problems:
        if problem['solutions']:
            latest = problem['solutions'][-1]
            if latest.get('verdict'):
                if 'accept' in latest['verdict'].lower():
                    accepted += 1
                else:
                    failed += 1
    
    print(f"📊 **Solution Statistics**")
    print("=" * 30)
    print(f"Problems attempted: {total_problems}")
    print(f"Total solutions generated: {total_attempts}")
    print(f"Average attempts per problem: {total_attempts/total_problems:.1f}")
    
    if accepted + failed > 0:
        print(f"Success rate: {accepted}/{accepted+failed} ({100*accepted/(accepted+failed):.1f}%)")
    
    print(f"\n📁 Solutions stored in: solutions/")

def main():
    parser = argparse.ArgumentParser(description="View and manage saved solutions")
    parser.add_argument("--problem", "-p", help="View solutions for specific problem (e.g., 2051_E)")
    parser.add_argument("--list", "-l", action="store_true", help="List all problems with solutions")
    parser.add_argument("--stats", "-s", action="store_true", help="Show statistics")
    parser.add_argument("--show-code", help="Show code for specific problem and iteration (e.g., 2051_E:1)")
    
    args = parser.parse_args()
    
    if args.problem:
        view_problem_solutions(args.problem)
    elif args.list:
        list_all_solutions()
    elif args.stats:
        show_statistics()
    elif args.show_code:
        try:
            problem_id, iteration = args.show_code.split(':')
            show_solution_code(problem_id, int(iteration))
        except ValueError:
            print("❌ Invalid format. Use: problem_id:iteration (e.g., 2051_E:1)")
    else:
        # Default: show overview
        show_statistics()
        print()
        list_all_solutions()

if __name__ == "__main__":
    main()
