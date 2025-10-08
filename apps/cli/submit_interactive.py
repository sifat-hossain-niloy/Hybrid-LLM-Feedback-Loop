#!/usr/bin/env python3
"""
Interactive submission helper - opens browser and provides solution code.
"""

import argparse
import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from playwright.sync_api import sync_playwright
from core.config import CF_USERNAME

def interactive_submit(solution_file: str, contest_id: int, problem_letter: str):
    """Open browser for manual submission with solution code provided."""
    
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
    
    print("🚀 **Interactive Codeforces Submission Helper**")
    print("=" * 50)
    print()
    print(f"📋 Solution file: {solution_file}")
    print(f"🎯 Target: https://codeforces.com/problemset/problem/{contest_id}/{problem_letter}")
    print(f"📏 Code length: {len(source_code)} characters")
    if CF_USERNAME:
        print(f"👤 Username: {CF_USERNAME}")
    print()
    
    # Show the code that will be submitted
    print("📝 **Solution Code:**")
    print("-" * 40)
    print(source_code)
    print("-" * 40)
    print()
    
    # Copy to clipboard if possible
    try:
        import pyperclip
        pyperclip.copy(source_code)
        print("✅ **Solution code copied to clipboard!**")
        print("   You can paste it directly in the editor.")
    except ImportError:
        print("💡 Install 'pyperclip' to auto-copy code to clipboard:")
        print("   pip install pyperclip")
    print()
    
    print("🌐 **Opening browser for manual submission...**")
    print()
    print("**Instructions:**")
    print("1. ✅ Login to Codeforces if prompted")
    print("2. 🔍 Navigate to the problem (will open automatically)")
    print("3. 🔗 Click 'Submit' button")
    print("4. 📝 Paste the solution code in the editor")
    print("5. 🚀 Click 'Submit' to submit your solution")
    print("6. ⏳ Wait for the verdict")
    print()
    
    input("Press Enter to open browser...")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
            # Open the problem page directly
            problem_url = f"https://codeforces.com/problemset/problem/{contest_id}/{problem_letter}"
            print(f"🔗 Opening: {problem_url}")
            
            page.goto(problem_url)
            
            print()
            print("🎯 **Browser opened! Follow the instructions above.**")
            print("   The solution code is in your clipboard (if pyperclip is installed)")
            print()
            print("⏳ **Waiting for you to complete submission...**")
            print("   Press Enter here when you're done or want to close browser...")
            
            # Wait for user input
            input()
            
            # Check current URL to see if we're on a submission page
            current_url = page.url
            if 'submission' in current_url:
                print("✅ **Detected submission page!**")
                print(f"   URL: {current_url}")
                
                # Try to extract submission ID
                import re
                match = re.search(r'/submission/(\d+)', current_url)
                if match:
                    submission_id = match.group(1)
                    print(f"🎯 **Submission ID: {submission_id}**")
                
                print("🔍 **Checking for verdict...**")
                time.sleep(2)
                
                # Look for common verdict text
                page_text = page.content().lower()
                verdicts = [
                    ('accepted', '🎉 ACCEPTED! '),
                    ('wrong answer', '❌ Wrong Answer'),
                    ('time limit', '⏰ Time Limit Exceeded'),
                    ('memory limit', '💾 Memory Limit Exceeded'),
                    ('runtime error', '💥 Runtime Error'),
                    ('compilation error', '🔨 Compilation Error'),
                    ('in queue', '⏳ In Queue'),
                    ('running', '🏃 Running')
                ]
                
                for verdict_text, emoji_msg in verdicts:
                    if verdict_text in page_text:
                        print(f"   Status: {emoji_msg}")
                        break
                
            else:
                print("ℹ️  Not on submission page - manual submission may still be in progress")
            
            print()
            print("🏁 **Submission helper complete!**")
            browser.close()
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Interactive submission helper for Codeforces")
    parser.add_argument("solution_file", help="Path to C++ solution file")
    parser.add_argument("--contest-id", type=int, help="Contest ID (e.g., 2045)")
    parser.add_argument("--problem", help="Problem letter (e.g., A)")
    
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
        return
    
    success = interactive_submit(
        args.solution_file,
        contest_id,
        problem_letter.upper()
    )
    
    if success:
        print("\n✨ **Helper session completed successfully!**")
    else:
        print("\n❌ **Helper session failed!**")

if __name__ == "__main__":
    main()
