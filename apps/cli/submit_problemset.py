#!/usr/bin/env python3
"""
Submit solution to Codeforces problemset.
"""

import argparse
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from core.problemset_client import get_problemset_client
from core.config import CF_DEFAULT_LANG_ID

def submit_solution_file(solution_file: str, contest_id: int, problem_letter: str, language_id: int = None):
    """Submit a solution file to Codeforces problemset."""
    
    # Read the solution file
    if not os.path.exists(solution_file):
        print(f"❌ Solution file not found: {solution_file}")
        return False
    
    with open(solution_file, 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    # Remove the header comment if present
    lines = source_code.split('\n')
    if lines[0].strip().startswith('/*'):
        # Find the end of the comment block
        for i, line in enumerate(lines):
            if '*/' in line:
                source_code = '\n'.join(lines[i+1:]).strip()
                break
    
    print(f"📋 Submitting solution from: {solution_file}")
    print(f"🎯 Target: https://codeforces.com/problemset/problem/{contest_id}/{problem_letter}")
    print(f"📏 Code length: {len(source_code)} characters")
    print()
    
    try:
        # Get the problemset client
        client = get_problemset_client()
        
        # Submit the solution
        submission_id, submission_url = client.submit_problemset_solution(
            contest_id=contest_id,
            problem_letter=problem_letter,
            source_code=source_code,
            language_id=language_id
        )
        
        if submission_id:
            print(f"🎉 Submission successful!")
            print(f"   Submission ID: {submission_id}")
            print(f"   URL: {submission_url}")
            print()
            
            # Poll for result
            print("⏳ Waiting for verdict...")
            result = client.get_problemset_submission_result(contest_id, submission_id)
            
            if result:
                print(f"🔍 Final Result:")
                print(f"   Verdict: {result['verdict']}")
                if result.get('test_number'):
                    print(f"   Failed on test: {result['test_number']}")
                if result.get('time_ms'):
                    print(f"   Time: {result['time_ms']} ms")
                if result.get('memory_kb'):
                    print(f"   Memory: {result['memory_kb']} KB")
                
                # Save result to metadata if it's a solution file
                if 'solutions/' in solution_file:
                    try:
                        update_solution_metadata(solution_file, result, submission_id, submission_url)
                    except Exception as e:
                        print(f"⚠️  Could not update metadata: {e}")
            
            return True
        else:
            print("❌ Submission failed")
            return False
            
    except Exception as e:
        print(f"❌ Submission error: {e}")
        return False

def update_solution_metadata(solution_file: str, result: dict, submission_id: int, submission_url: str):
    """Update solution metadata with submission results."""
    import json
    
    # Find corresponding metadata file
    meta_file = solution_file.replace('.cpp', '_meta.json')
    
    if os.path.exists(meta_file):
        with open(meta_file, 'r') as f:
            metadata = json.load(f)
        
        # Update with submission info
        metadata['cf_submission_id'] = submission_id
        metadata['cf_submission_url'] = submission_url
        metadata['verdict'] = result.get('verdict')
        metadata['test_number'] = result.get('test_number')
        metadata['time_ms'] = result.get('time_ms')
        metadata['memory_kb'] = result.get('memory_kb')
        
        with open(meta_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Updated metadata: {meta_file}")

def main():
    parser = argparse.ArgumentParser(description="Submit solution to Codeforces problemset")
    parser.add_argument("solution_file", help="Path to C++ solution file")
    parser.add_argument("--contest-id", type=int, help="Contest ID (e.g., 2045)")
    parser.add_argument("--problem", help="Problem letter (e.g., A)")
    parser.add_argument("--language", type=int, default=CF_DEFAULT_LANG_ID, help=f"Language ID (default: {CF_DEFAULT_LANG_ID})")
    
    args = parser.parse_args()
    
    # Try to auto-detect contest and problem from filename if not provided
    contest_id = args.contest_id
    problem_letter = args.problem
    
    if not contest_id or not problem_letter:
        # Try to extract from solution file path (e.g., solutions/2045_A/solution_1.cpp)
        if 'solutions/' in args.solution_file:
            path_parts = args.solution_file.split('/')
            for part in path_parts:
                if '_' in part and part.replace('_', '').replace('-', '').replace('.', '').isalnum():
                    # This looks like a problem ID
                    if '_' in part:
                        try:
                            auto_contest_id, auto_letter = part.split('_', 1)
                            if auto_contest_id.isdigit():
                                contest_id = contest_id or int(auto_contest_id)
                                problem_letter = problem_letter or auto_letter
                                break
                        except:
                            pass
    
    if not contest_id or not problem_letter:
        print("❌ Could not determine contest ID and problem letter")
        print("   Please provide --contest-id and --problem arguments")
        print("   Example: --contest-id 2045 --problem A")
        return
    
    print("🚀 **Codeforces Problemset Submission**")
    print("=" * 40)
    print()
    
    success = submit_solution_file(
        args.solution_file,
        contest_id,
        problem_letter.upper(),
        args.language
    )
    
    if success:
        print("\n🎉 **Submission Complete!**")
    else:
        print("\n❌ **Submission Failed!**")
        print("   Check your credentials and try again")

if __name__ == "__main__":
    main()
