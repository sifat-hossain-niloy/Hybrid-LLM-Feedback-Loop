#!/usr/bin/env python3
"""
Submit solution using existing Chrome/Chromium browser with user profile.
"""

import argparse
import sys
import os
import time
import subprocess
import json
import re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from playwright.sync_api import sync_playwright
from core.config import CF_USERNAME

def await_verdict(page, submission_id, max_wait_time=10000):
    """Poll for verdict using XPath elements until not 'Running...'"""
    print("⏳ Polling for verdict...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        try:
            # Check verdict using your corrected XPath
            verdict_element = page.locator('//*[@id="pageContent"]/div[4]/div[6]/table/tbody/tr[2]/td[6]/a/span')
            if verdict_element.is_visible():
                verdict_text = verdict_element.inner_text().strip()
                print(f"📊 Current Status: {verdict_text}")
                
                # Check if verdict is final (not running)
                if "Running" not in verdict_text.lower() and "in queue" not in verdict_text.lower():
                    if "accepted" in verdict_text.lower():
                        print("🎉 ACCEPTED!")
                        return verdict_text
                    else:
                        print(f"❌ {verdict_text}")
                        return verdict_text
                
                # Still running, wait and refresh
                time.sleep(5)
                page.reload()
                page.wait_for_load_state('networkidle')
            else:
                print("⚠️  XPath element not found, trying to find specific submission...")
                # Try to find the specific submission ID and get its verdict
                if submission_id:
                    try:
                        # Look for the submission ID link in the table
                        submission_link = page.locator(f'a:has-text("{submission_id}")').first
                        if submission_link.is_visible():
                            # Get the row containing this submission
                            submission_row = submission_link.locator('xpath=ancestor::tr[1]')
                            # Get the verdict cell (6th column, index 5)
                            verdict_cell = submission_row.locator('td').nth(5)
                            
                            # Try different selectors for verdict
                            verdict_element = verdict_cell.locator('span, a span, a').first
                            if verdict_element.is_visible():
                                verdict_text = verdict_element.inner_text().strip()
                                print(f"📊 Found verdict for {submission_id}: {verdict_text}")
                                
                                if "running" not in verdict_text.lower() and "in queue" not in verdict_text.lower() and "judging" not in verdict_text.lower():
                                    if "accepted" in verdict_text.lower():
                                        print("🎉 ACCEPTED!")
                                        return verdict_text
                                    else:
                                        print(f"❌ {verdict_text}")
                                        return verdict_text
                            else:
                                print(f"⚠️  Verdict element not visible for submission {submission_id}")
                        else:
                            print(f"⚠️  Could not find submission {submission_id} in table")
                    except Exception as e:
                        print(f"⚠️  Error finding specific submission: {e}")
                
                print("⏳ Waiting for verdict to appear...")
                time.sleep(5)
                page.reload()
                page.wait_for_load_state('networkidle')
                
        except Exception as e:
            print(f"⚠️  Error checking verdict: {e}")
            time.sleep(5)
            continue
    
    print("⏰ Timeout waiting for verdict")
    return "Timeout"

def intercept_api_calls(page, submission_id):
    """Intercept and capture API calls for submission details"""
    print("🎯 Setting up API call interception...")
    
    captured_responses = []
    
    def handle_response(response):
        try:
            url = response.url
            # Look for submitSource API calls
            if 'data/submitSource' in url:
                print(f"🔍 Intercepted API call: {url}")
                
                # Extract rv parameter from URL
                rv_match = re.search(r'rv=([a-zA-Z0-9]+)', url)
                rv_param = rv_match.group(1) if rv_match else "unknown"
                
                # Get response text
                try:
                    response_text = response.text()
                    print(f"✅ Captured API response ({len(response_text)} chars)")
                    
                    captured_responses.append({
                        "url": url,
                        "rv_parameter": rv_param,
                        "response_text": response_text,
                        "status": response.status,
                        "headers": dict(response.headers)
                    })
                except Exception as e:
                    print(f"⚠️  Could not read response text: {e}")
        except Exception as e:
            print(f"⚠️  Error handling response: {e}")
    
    # Set up response listener
    page.on("response", handle_response)
    
    return captured_responses

def click_submission_for_details(page, submission_id):
    """Click on submission ID to get detailed popup results"""
    try:
        print(f"🖱️  Clicking on submission ID {submission_id} for details...")
        
        # Find and click the submission ID link
        submission_link = page.locator(f'a:has-text("{submission_id}")').first
        if submission_link.is_visible():
            submission_link.click()
            page.wait_for_load_state('networkidle', timeout=10000)
            
            # Wait for any popup or new page to load
            page.wait_for_timeout(3000)
            
            print("✅ Clicked submission ID, checking for detailed results...")
            
            # Try to extract detailed test information from the current page
            page_content = page.content()
            
            # Look for test result patterns in the HTML
            test_patterns = [
                r'"testCount":\s*"(\d+)"',
                r'"verdict#\d+":\s*"([^"]+)"',
                r'"output#\d+":\s*"([^"]+)"',
                r'"input#\d+":\s*"([^"]+)"',
                r'"answer#\d+":\s*"([^"]+)"',
                r'"timeConsumed#\d+":\s*"([^"]+)"',
                r'"memoryConsumed#\d+":\s*"([^"]+)"'
            ]
            
            found_details = {}
            for pattern in test_patterns:
                matches = re.findall(pattern, page_content)
                if matches:
                    found_details[pattern] = matches
            
            if found_details:
                print("✅ Found detailed test results in page content")
                return {
                    "method": "click_extraction",
                    "submission_id": submission_id,
                    "extracted_details": found_details,
                    "page_title": page.title(),
                    "current_url": page.url
                }
            else:
                print("⚠️  No detailed test results found after clicking")
                return None
        else:
            print(f"⚠️  Could not find clickable submission ID {submission_id}")
            return None
            
    except Exception as e:
        print(f"⚠️  Error clicking submission ID: {e}")
        return None

def get_detailed_results(page, submission_id):
    """Enhanced method to get detailed submission results via multiple approaches"""
    try:
        print("📊 Getting detailed results using multiple methods...")
        
        # Method 1: Set up API interception BEFORE any navigation
        captured_responses = intercept_api_calls(page, submission_id)
        
        # Method 2: Click on submission ID to trigger detailed loading
        click_results = click_submission_for_details(page, submission_id)
        
        # Method 3: Try manual API call with extracted parameters
        page_content = page.content()
        
        # Extract CSRF token more aggressively
        csrf_patterns = [
            r'csrf["\s]*[:=]["\s]*["\']([a-f0-9]+)["\']',
            r'"csrf_token"["\s]*:["\s]*["\']([a-f0-9]+)["\']',
            r'_tta["\s]*[:=]["\s]*["\']([a-f0-9]+)["\']',
        ]
        
        csrf_token = None
        for pattern in csrf_patterns:
            match = re.search(pattern, page_content, re.IGNORECASE)
            if match:
                csrf_token = match.group(1)
                break
        
        # Extract rv parameter from multiple sources
        rv_patterns = [
            r'rv["\s]*[:=]["\s]*["\']([a-zA-Z0-9]+)["\']',
            r'data/submitSource\?rv=([a-zA-Z0-9]+)',
            r'"rv"["\s]*:["\s]*"([a-zA-Z0-9]+)"'
        ]
        
        rv_param = None
        for pattern in rv_patterns:
            match = re.search(pattern, page_content, re.IGNORECASE)
            if match:
                rv_param = match.group(1)
                break
        
        # Use captured responses if available
        api_response = None
        if captured_responses:
            print(f"✅ Found {len(captured_responses)} intercepted API calls")
            api_response = captured_responses[-1]  # Use the latest response
        
        # Fallback: Try manual API call if we have the tokens
        if not api_response and csrf_token and submission_id:
            print("🔄 Attempting manual API call...")
            if not rv_param:
                rv_param = "k1pqe12g2"  # Fallback
            
            api_url = f"https://codeforces.com/data/submitSource?rv={rv_param}"
            
            manual_response = page.evaluate(f"""
            async () => {{
                try {{
                    const response = await fetch('{api_url}', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'X-Requested-With': 'XMLHttpRequest'
                        }},
                        body: 'submissionId={submission_id}&csrf_token={csrf_token}'
                    }});
                    
                    if (response.ok) {{
                        const text = await response.text();
                        return {{
                            url: '{api_url}',
                            rv_parameter: '{rv_param}',
                            response_text: text,
                            status: response.status
                        }};
                    }} else {{
                        return {{
                            error: true,
                            status: response.status,
                            statusText: response.statusText
                        }};
                    }}
                }} catch (error) {{
                    return {{
                        error: true,
                        message: error.toString()
                    }};
                }}
            }}
            """)
            
            if manual_response and not manual_response.get('error'):
                api_response = manual_response
                print("✅ Manual API call successful")
        
        # Save all collected data
        if api_response or click_results:
            from datetime import datetime
            import os
            
            # Create api_responses directory if it doesn't exist
            api_dir = "api_responses"
            if not os.path.exists(api_dir):
                os.makedirs(api_dir)
            
            # Create filename with submission ID and timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{api_dir}/submission_{submission_id}_{timestamp}.json"
            
            # Prepare comprehensive data to save
            comprehensive_data = {
                "submission_id": submission_id,
                "timestamp": datetime.now().isoformat(),
                "collection_methods": []
            }
            
            if api_response:
                comprehensive_data["api_response"] = api_response
                comprehensive_data["collection_methods"].append("api_interception")
                
                # Try to parse API response
                response_text = api_response.get("response_text", "")
                if response_text and response_text.strip().startswith('{'):
                    try:
                        parsed_api = json.loads(response_text)
                        comprehensive_data["parsed_api_response"] = parsed_api
                        print("✅ API response parsed as JSON")
                        
                        # Display key information
                        if 'testCount' in parsed_api:
                            test_count = parsed_api['testCount']
                            print(f"📊 Test Count: {test_count}")
                            
                            # Look for verdict information
                            if 'verdict' in parsed_api:
                                print(f"🏆 Overall Verdict: {parsed_api['verdict']}")
                            
                            # Show individual test results
                            for i in range(1, int(test_count) + 1):
                                verdict_key = f"verdict#{i}"
                                if verdict_key in parsed_api:
                                    print(f"🧪 Test {i}: {parsed_api[verdict_key]}")
                        
                    except json.JSONDecodeError as e:
                        print(f"⚠️  Could not parse API response as JSON: {e}")
            
            if click_results:
                comprehensive_data["click_results"] = click_results
                comprehensive_data["collection_methods"].append("click_extraction")
            
            # Save comprehensive data
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(comprehensive_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Comprehensive results saved to: {filename}")
            
            return comprehensive_data
        else:
            print("⚠️  No detailed results obtained from any method")
            return None
            
    except Exception as e:
        print(f"⚠️  Error in enhanced result collection: {e}")
        return None

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
                
                # Step 4: Navigate to status page and get submission ID
                print("⏳ Step 4: Waiting for submission result...")
                time.sleep(3)
                
                current_url = page.url
                print(f"📍 Current URL: {current_url}")
                submission_id = None
                
                # Navigate to status page to get submission details
                if 'status' not in current_url:
                    print("🔄 Navigating to status page...")
                    page.goto("https://codeforces.com/problemset/status?my=on", wait_until='networkidle')
                    time.sleep(2)
                
                # Step 5: Extract submission ID using your XPath
                try:
                    submission_link = page.locator('//*[@id="pageContent"]/div[4]/div[6]/table/tbody/tr[2]/td[1]/a').first
                    if submission_link.is_visible():
                        submission_id = submission_link.inner_text().strip()
                        print(f"🎯 Submission ID: {submission_id}")
                    else:
                        # Fallback: try to extract from URL or page
                        match = re.search(r'/submission/(\d+)', current_url)
                        if match:
                            submission_id = match.group(1)
                            print(f"🎯 Submission ID (from URL): {submission_id}")
                        else:
                            # Try to find submission ID in page content
                            page_content = page.content()
                            id_match = re.search(r'"submissionId":\s*(\d+)', page_content)
                            if id_match:
                                submission_id = id_match.group(1)
                                print(f"🎯 Submission ID (from page): {submission_id}")
                except Exception as e:
                    print(f"⚠️  Could not extract submission ID: {e}")
                
                print("🎉 Solution submitted successfully!")
                
                # Step 6: Poll for verdict using your XPath elements
                verdict = await_verdict(page, submission_id)
                
                if verdict and verdict != "Timeout":
                    print(f"🏆 Final Verdict: {verdict}")
                    
                    # Step 7: Get detailed results via API if submission ID was found
                    if submission_id:
                        detailed_results = get_detailed_results(page, submission_id)
                        if detailed_results and len(detailed_results) > 50:
                            print("📊 Detailed Results Available")
                            # Parse results if they're JSON
                            try:
                                if detailed_results.startswith('{'):
                                    results_json = json.loads(detailed_results)
                                    if 'compilationError' in results_json:
                                        print(f"⚠️  Compilation Error: {results_json['compilationError']}")
                                    if 'testCount' in results_json:
                                        print(f"📊 Tests Passed: {results_json.get('passedTestCount', 0)}/{results_json['testCount']}")
                            except:
                                print("📊 Raw Results:")
                                print(detailed_results[:300] + "..." if len(detailed_results) > 300 else detailed_results)
                    
                    # Determine success based on verdict
                    is_accepted = "accepted" in verdict.lower()
                    if is_accepted:
                        print("🎊 CONGRATULATIONS! Solution Accepted! 🎊")
                    else:
                        print(f"💭 Try again! Verdict: {verdict}")
                    
                    print()
                    print("🎉 **Submission process completed!**")
                    print("   Browser will remain open for your review")
                    print()
                    
                    input("Press Enter to finish (browser will remain open)...")
                    return is_accepted
                else:
                    print("⏰ Could not determine final verdict within timeout")
                    print("🔍 Browser will remain open for manual inspection")
                    input("Press Enter to finish...")
                    return False
                
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
