#!/usr/bin/env python3
"""
View Automated Problem Solving Results

Utility to view results from the automated problem solver.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime


def format_duration(minutes):
    """Format duration in minutes to human readable format"""
    if minutes < 1:
        return f"{minutes * 60:.0f} seconds"
    elif minutes < 60:
        return f"{minutes:.1f} minutes"
    else:
        hours = minutes / 60
        return f"{hours:.1f} hours"


def view_problem_results(problem_dir: Path):
    """View results for a single problem"""
    
    # Load final result
    final_result_path = problem_dir / "final_result.json"
    if not final_result_path.exists():
        print(f"❌ No results found for {problem_dir.name}")
        return
    
    with open(final_result_path, 'r', encoding='utf-8') as f:
        result = json.load(f)
    
    # Load problem info
    problem_info_path = problem_dir / "problem_info.json"
    problem_info = {}
    if problem_info_path.exists():
        with open(problem_info_path, 'r', encoding='utf-8') as f:
            problem_info = json.load(f)
    
    # Print header
    print(f"\n🎯 PROBLEM: {result['problem_id']}")
    if problem_info.get('title'):
        print(f"📋 Title: {problem_info['title']}")
    if problem_info.get('rating'):
        print(f"⭐ Rating: {problem_info['rating']}")
    print("=" * 60)
    
    # Status
    status = result['status']
    if result.get('accepted', False):
        print(f"✅ STATUS: {status.upper()} 🎉")
        print(f"🏆 Solved in attempt {result['successful_attempt']}/{result['total_attempts']}")
    else:
        print(f"❌ STATUS: {status.upper()}")
        print(f"💔 Failed after {result['total_attempts']} attempts")
    
    # Timing
    if result.get('total_duration_minutes'):
        duration = format_duration(result['total_duration_minutes'])
        print(f"⏱️  Duration: {duration}")
    
    # Statistics
    if result.get('statistics'):
        stats = result['statistics']
        total_errors = sum(stats.values())
        if total_errors > 0:
            print(f"\n📊 ERROR BREAKDOWN:")
            if stats['compilation_errors'] > 0:
                print(f"   🔨 Compilation Errors: {stats['compilation_errors']}")
            if stats['runtime_errors'] > 0:
                print(f"   🐛 Runtime Errors: {stats['runtime_errors']}")
            if stats['wrong_answers'] > 0:
                print(f"   ❌ Wrong Answers: {stats['wrong_answers']}")
            if stats['time_limit_exceeded'] > 0:
                print(f"   ⏰ Time Limit Exceeded: {stats['time_limit_exceeded']}")
            if stats['memory_limit_exceeded'] > 0:
                print(f"   💾 Memory Limit Exceeded: {stats['memory_limit_exceeded']}")
    
    # Files
    solutions_dir = problem_dir / "solutions"
    api_dir = problem_dir / "api_responses"
    
    if solutions_dir.exists():
        solutions = list(solutions_dir.glob("*.cpp"))
        print(f"\n💻 SOLUTIONS: {len(solutions)} files")
        for solution in sorted(solutions):
            print(f"   📄 {solution.name}")
    
    if api_dir.exists():
        responses = list(api_dir.glob("*.json"))
        print(f"\n📊 API RESPONSES: {len(responses)} files")
        for response in sorted(responses):
            print(f"   📄 {response.name}")


def list_all_problems(base_dir: Path):
    """List all solved problems"""
    
    if not base_dir.exists():
        print(f"❌ Directory {base_dir} does not exist")
        return
    
    # Find all problem directories
    problem_dirs = []
    for item in base_dir.iterdir():
        if item.is_dir() and (item / "final_result.json").exists():
            problem_dirs.append(item)
    
    if not problem_dirs:
        print(f"📂 No solved problems found in {base_dir}")
        return
    
    print(f"📂 SOLVED PROBLEMS ({len(problem_dirs)} total):")
    print("=" * 80)
    
    # Sort by modification time (most recent first)
    problem_dirs.sort(key=lambda x: (x / "final_result.json").stat().st_mtime, reverse=True)
    
    for problem_dir in problem_dirs:
        try:
            # Load result
            with open(problem_dir / "final_result.json", 'r', encoding='utf-8') as f:
                result = json.load(f)
            
            # Load problem info
            problem_info = {}
            if (problem_dir / "problem_info.json").exists():
                with open(problem_dir / "problem_info.json", 'r', encoding='utf-8') as f:
                    problem_info = json.load(f)
            
            # Format output
            status_icon = "✅" if result.get('accepted', False) else "❌"
            problem_id = result['problem_id']
            title = problem_info.get('title', 'Unknown Title')[:40]
            attempts = f"{result['successful_attempt'] if result.get('accepted') else result['total_attempts']}/{result['total_attempts']}"
            duration = format_duration(result.get('total_duration_minutes', 0))
            
            print(f"{status_icon} {problem_id:<10} | {title:<40} | {attempts:<5} | {duration}")
            
        except Exception as e:
            print(f"⚠️  Error reading {problem_dir.name}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="View automated problem solving results",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all solved problems"
    )
    
    parser.add_argument(
        "--problem", "-p",
        help="View detailed results for specific problem (e.g., 2045_A)"
    )
    
    parser.add_argument(
        "--base-dir",
        default="problems_solved",
        help="Base directory containing results (default: problems_solved)"
    )
    
    args = parser.parse_args()
    
    base_dir = Path(args.base_dir)
    
    if args.list:
        list_all_problems(base_dir)
    elif args.problem:
        problem_dir = base_dir / args.problem
        view_problem_results(problem_dir)
    else:
        # Default: list all problems
        list_all_problems(base_dir)


if __name__ == "__main__":
    main()
