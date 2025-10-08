#!/usr/bin/env python3
"""
Submit solution using existing Chrome/Chromium browser with user profile.
"""

import argparse
import sys
import os
import time
import subprocess
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from playwright.sync_api import sync_playwright
from core.config import CF_USERNAME

def get_chromium_path():
    """Find Chromium executable path."""
    possible_paths = [
        # macOS Chromium
        '/Applications/Chromium.app/Contents/MacOS/Chromium',
        # Alternative Chromium locations on macOS
        '/usr/local/bin/chromium',
        '/opt/homebrew/bin/chromium',
        # Linux Chromium
        '/usr/bin/chromium-browser',
        '/usr/bin/chromium',
        '/snap/bin/chromium',
        # macOS Chrome as fallback
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        '/usr/bin/google-chrome',
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def start_chromium_with_debugging(profile_name="Sifat", port=9222):
    """Start Chromium with remote debugging enabled."""
    chromium_path = get_chromium_path()
    
    if not chromium_path:
        print("❌ Could not find Chromium executable")
        print("   Please install Chromium browser")
        print("   Download from: https://www.chromium.org/getting-involved/download-chromium/")
        return False
    
    print(f"🌐 Starting Chromium with profile '{profile_name}' and debugging...")
    print(f"   Using: {chromium_path}")
    
    # Chromium arguments for remote debugging
    chromium_args = [
        chromium_path,
        f"--profile-directory={profile_name}",
        f"--remote-debugging-port={port}",
        "--disable-web-security",
        "--disable-features=VizDisplayCompositor",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-dev-shm-usage",
        "--no-sandbox"
    ]
    
    try:
        # Start Chromium in background
        subprocess.Popen(chromium_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait a moment for Chromium to start
        time.sleep(3)
        
        print(f"✅ Chromium started with remote debugging on port {port}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to start Chromium: {e}")
        return False

def submit_with_existing_chrome(solution_file: str, contest_id: int, problem_letter: str, port=9222):
    """Submit solution using existing Chromium browser."""
    
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
    
    print("🚀 **Codeforces Submission via Existing Chromium**")
    print("=" * 50)
    print()
    print(f"📋 Solution file: {solution_file}")
    print(f"🎯 Target: https://codeforces.com/problemset/problem/{contest_id}/{problem_letter}")
    print(f"📏 Code length: {len(source_code)} characters")
    print()
    
    # Copy to clipboard if possible
    try:
        import pyperclip
        pyperclip.copy(source_code)
        print("✅ **Solution code copied to clipboard!**")
    except ImportError:
        print("💡 Install 'pyperclip' to auto-copy code: pip install pyperclip")
    
    print()
    
    # Try to connect to existing Chrome instance
    try:
        with sync_playwright() as p:
            print(f"🔗 Connecting to Chromium on port {port}...")
            
            # Connect to existing Chromium instance
            browser = p.chromium.connect_over_cdp(f"http://localhost:{port}")
            
            # Get the default context (existing browser session)
            contexts = browser.contexts
            if not contexts:
                print("❌ No browser contexts found. Make sure Chromium is running.")
                return False
            
            context = contexts[0]  # Use first context
            
            # Create new page or use existing one
            pages = context.pages
            if pages:
                page = pages[0]  # Use first existing page
            else:
                page = context.new_page()
            
            print("✅ Connected to existing Chromium browser!")
            print()
            
            # Navigate to the problem page
            problem_url = f"https://codeforces.com/problemset/problem/{contest_id}/{problem_letter}"
            print(f"🔗 Navigating to: {problem_url}")
            
            page.goto(problem_url, wait_until='domcontentloaded')
            page.wait_for_load_state('networkidle', timeout=10000)
            
            print("📄 Problem page loaded!")
            print()
            
            # Check if we're logged in
            page_content = page.content()
            if "logout" in page_content.lower() or "enter" not in page_content.lower():
                print("✅ Already logged in to Codeforces!")
            else:
                print("⚠️  Not logged in - please login in the browser first")
                print("   I'll wait for you to login...")
                input("Press Enter after logging in...")
            
            print()
            print("🎯 **Automated submission process starting...**")
            
            try:
                # Step 1: Find and click submit link
                print("🔗 Step 1: Looking for Submit button...")
                
                # Wait for page to be fully loaded
                time.sleep(2)
                
                # Try multiple selectors for submit link
                submit_selectors = [
                    'a[href*="submit"]:has-text("Submit")',
                    'a:has-text("Submit")',
                    'ul.nav li:nth-child(3) a',  # Third item in navigation
                    '//*[@id="pageContent"]/div[1]/ul/li[3]/a'  # Your original xpath
                ]
                
                submit_clicked = False
                for selector in submit_selectors:
                    try:
                        if selector.startswith('//'):
                            # XPath selector
                            page.locator(f'xpath={selector}').click(timeout=3000)
                        else:
                            # CSS selector
                            page.click(selector, timeout=3000)
                        
                        page.wait_for_load_state('networkidle', timeout=10000)
                        print(f"✅ Submit link clicked using: {selector}")
                        submit_clicked = True
                        break
                    except:
                        continue
                
                if not submit_clicked:
                    print("⚠️  Could not find submit link automatically")
                    print("   Please click the Submit button manually in the browser")
                    input("Press Enter after clicking Submit...")
                
                # Step 2: Paste code in editor
                print("📝 Step 2: Pasting code in editor...")
                time.sleep(2)
                
                # Try multiple editor selectors
                editor_selectors = [
                    'textarea[name="source"]',
                    '#editor textarea',
                    '//*[@id="editor"]/div[2]/div',  # Your original xpath
                    '.CodeMirror textarea',
                    'textarea.form-control'
                ]
                
                code_pasted = False
                for selector in editor_selectors:
                    try:
                        if selector.startswith('//'):
                            # XPath - click first then type
                            editor = page.locator(f'xpath={selector}')
                            editor.click()
                            page.keyboard.press('Control+a')
                            page.keyboard.type(source_code)
                        else:
                            # CSS selector - use fill
                            page.fill(selector, source_code, timeout=5000)
                        
                        print(f"✅ Code pasted using: {selector}")
                        code_pasted = True
                        break
                    except:
                        continue
                
                if not code_pasted:
                    print("⚠️  Could not paste code automatically")
                    print("   The code is in your clipboard - please paste it manually")
                    print(f"   Code length: {len(source_code)} characters")
                    input("Press Enter after pasting code...")
                
                # Step 3: Submit the solution
                print("🚀 Step 3: Submitting solution...")
                time.sleep(1)
                
                # Try multiple submit button selectors
                submit_btn_selectors = [
                    'input[type="submit"]',
                    'button:has-text("Submit")',
                    '//*[@id="singlePageSubmitButton"]',  # Your original xpath
                    '.submit-button',
                    '#submitButton'
                ]
                
                submitted = False
                for selector in submit_btn_selectors:
                    try:
                        if selector.startswith('//'):
                            page.locator(f'xpath={selector}').click(timeout=3000)
                        else:
                            page.click(selector, timeout=3000)
                        
                        print(f"✅ Submit button clicked using: {selector}")
                        submitted = True
                        break
                    except:
                        continue
                
                if not submitted:
                    print("⚠️  Could not click submit button automatically")
                    print("   Please click the Submit button manually")
                    input("Press Enter after submitting...")
                
                # Step 4: Wait for result
                print("⏳ Step 4: Waiting for submission result...")
                time.sleep(5)
                
                # Check for submission success
                current_url = page.url
                print(f"📍 Current URL: {current_url}")
                
                if 'submission' in current_url:
                    print("✅ Successfully redirected to submission page!")
                    
                    # Extract submission ID
                    import re
                    match = re.search(r'/submission/(\d+)', current_url)
                    if match:
                        submission_id = match.group(1)
                        print(f"🎯 Submission ID: {submission_id}")
                
                # Look for verdict
                page_text = page.content().lower()
                verdicts = [
                    ('accepted', '🎉 ACCEPTED!'),
                    ('wrong answer', '❌ Wrong Answer'),
                    ('time limit', '⏰ Time Limit Exceeded'),
                    ('memory limit', '💾 Memory Limit Exceeded'),
                    ('runtime error', '💥 Runtime Error'),
                    ('compilation error', '🔨 Compilation Error'),
                    ('in queue', '⏳ In Queue'),
                    ('running', '🏃 Running'),
                    ('judging', '⚖️ Judging')
                ]
                
                for verdict_text, emoji_msg in verdicts:
                    if verdict_text in page_text:
                        print(f"📊 Status: {emoji_msg}")
                        break
                
                print()
                print("🎉 **Submission process completed!**")
                print("   Check the browser for detailed results")
                print()
                
                # Keep browser open for user to see result
                input("Press Enter to finish (browser will remain open)...")
                
                return True
                
            except Exception as e:
                print(f"❌ Error during automated submission: {e}")
                print("   You can continue manually in the browser")
                input("Press Enter to finish...")
                return False
            
    except Exception as e:
        print(f"❌ Failed to connect to Chromium: {e}")
        print("   Make sure Chromium is running with remote debugging enabled")
        return False

def main():
    parser = argparse.ArgumentParser(description="Submit solution using existing Chromium browser")
    parser.add_argument("solution_file", help="Path to C++ solution file")
    parser.add_argument("--contest-id", type=int, help="Contest ID (e.g., 2045)")
    parser.add_argument("--problem", help="Problem letter (e.g., A)")
    parser.add_argument("--profile", default="Sifat", help="Chromium profile name (default: Sifat)")
    parser.add_argument("--port", type=int, default=9222, help="Chromium debugging port (default: 9222)")
    parser.add_argument("--start-chrome", action="store_true", help="Start Chromium with debugging enabled")
    
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
    
    # Start Chromium if requested
    if args.start_chrome:
        if not start_chromium_with_debugging(args.profile, args.port):
            return
    
    # Submit solution
    success = submit_with_existing_chrome(
        args.solution_file,
        contest_id,
        problem_letter.upper(),
        args.port
    )
    
    if success:
        print("\n🎉 **Submission completed successfully!**")
    else:
        print("\n❌ **Submission had issues - check browser**")

if __name__ == "__main__":
    main()
