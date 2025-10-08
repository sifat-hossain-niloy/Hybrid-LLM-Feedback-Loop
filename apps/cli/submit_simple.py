#!/usr/bin/env python3
"""
Simple submission helper - just copies code and opens browser.
"""

import argparse
import sys
import os
import webbrowser
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pyperclip

def simple_submit(solution_file: str, contest_id: int, problem_letter: str):
    """Simple submission - copy code and open browser."""
    
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
    
    print("🚀 **Simple Codeforces Submission Helper**")
    print("=" * 45)
    print()
    print(f"📋 Solution file: {solution_file}")
    print(f"🎯 Target: https://codeforces.com/problemset/problem/{contest_id}/{problem_letter}")
    print(f"📏 Code length: {len(source_code)} characters")
    print()
    
    # Copy code to clipboard
    try:
        pyperclip.copy(source_code)
        print("✅ **Solution code copied to clipboard!**")
    except Exception as e:
        print(f"⚠️  Could not copy to clipboard: {e}")
    
    print()
    print("📝 **Your Solution Code:**")
    print("-" * 40)
    print(source_code)
    print("-" * 40)
    print()
    
    # Open browser to problem page
    problem_url = f"https://codeforces.com/problemset/problem/{contest_id}/{problem_letter}"
    
    print("🌐 **Opening browser to problem page...**")
    print(f"   URL: {problem_url}")
    print()
    
    try:
        webbrowser.open(problem_url)
        print("✅ Browser opened!")
    except Exception as e:
        print(f"⚠️  Could not open browser: {e}")
        print(f"   Please manually open: {problem_url}")
    
    print()
    print("📋 **Manual Submission Steps:**")
    print("1. 🔐 Login to Codeforces if needed")
    print("2. 🔗 Click the 'Submit' button on the problem page")
    print("3. 📝 Paste the code (Ctrl+V or Cmd+V) in the editor")
    print("4. 🚀 Click 'Submit' to submit your solution")
    print("5. ⏳ Wait for the verdict")
    print()
    print("✨ **Code is ready in your clipboard - just paste and submit!**")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Simple submission helper")
    parser.add_argument("solution_file", help="Path to C++ solution file")
    parser.add_argument("--contest-id", type=int, help="Contest ID (e.g., 2045)")
    parser.add_argument("--problem", help="Problem letter (e.g., A)")
    
    args = parser.parse_args()
    
    # Try to auto-detect contest and problem from filename
    contest_id = args.contest_id
    problem_letter = args.problem
    
    if not contest_id or not problem_letter:
        if 'solutions/' in args.solution_file:
            path_parts = args.solution_file.split('/')
            for part in path_parts:
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
        return
    
    success = simple_submit(
        args.solution_file,
        contest_id,
        problem_letter.upper()
    )
    
    if success:
        print("\n🎉 **Helper completed! Your browser should be open with code in clipboard.**")

if __name__ == "__main__":
    main()
