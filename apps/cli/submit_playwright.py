#!/usr/bin/env python3
"""
Submit solution to Codeforces using Playwright (browser automation).
"""

import argparse
import sys
import os
import time
import json
import re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from playwright.sync_api import sync_playwright
from core.config import CF_USERNAME, CF_PASSWORD

def await_verdict(page, submission_id, max_wait_time=300):
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
                if "running" not in verdict_text.lower() and "in queue" not in verdict_text.lower():
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

def submit_with_playwright(solution_file: str, contest_id: int, problem_letter: str):
    """Submit solution using Playwright browser automation."""
    
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
    
    if not CF_USERNAME or not CF_PASSWORD:
        print("❌ Codeforces credentials not configured")
        print("   Run: python scripts/setup_codeforces.py")
        return False
    
    print(f"🔐 Logging in as: {CF_USERNAME}")
    print()
    
    try:
        with sync_playwright() as p:
            browser = None
            try:
                # Launch browser
                print("🌐 Launching browser...")
                browser = p.chromium.launch(
                    headless=False,
                    args=['--no-sandbox', '--disable-dev-shm-usage']
                )
                context = browser.new_context(
                    viewport={'width': 1366, 'height': 768}
                )
                page = context.new_page()
                # Step 1: Login to Codeforces
                print("🔐 Step 1: Logging in to Codeforces...")
                page.goto("https://codeforces.com/enter", wait_until='domcontentloaded')
                
                # Wait for login form to be visible
                page.wait_for_selector('input[name="handleOrEmail"]', timeout=10000)
                
                # Fill login form
                page.fill('input[name="handleOrEmail"]', CF_USERNAME)
                page.fill('input[name="password"]', CF_PASSWORD)
                
                # Submit login form
                page.click('input[type="submit"]')
                page.wait_for_load_state('networkidle', timeout=15000)
                
                # Check if login was successful
                if "logout" not in page.content().lower():
                    print("❌ Login failed - check your credentials")
                    browser.close()
                    return False
                    
                print("✅ Login successful!")
                
                # Step 2: Navigate to problem page
                problem_url = f"https://codeforces.com/problemset/problem/{contest_id}/{problem_letter}"
                print(f"📄 Step 2: Opening problem page...")
                page.goto(problem_url, wait_until='domcontentloaded')
                page.wait_for_load_state('networkidle', timeout=10000)
                
                # Step 3: Click submit link using your xpath
                print("🔗 Step 3: Clicking submit link...")
                try:
                    submit_link = page.locator('//*[@id="pageContent"]/div[1]/ul/li[3]/a')
                    submit_link.click()
                    page.wait_for_load_state('networkidle')
                except Exception as e:
                    print(f"⚠️  Could not find submit link with xpath, trying alternative...")
                    # Try alternative - look for any submit link
                    try:
                        page.click('a:has-text("Submit")')
                        page.wait_for_load_state('networkidle')
                    except Exception as e2:
                        print(f"❌ Could not find submit link: {e2}")
                        browser.close()
                        return False
                
                print("✅ Submit page opened!")
                
                # Step 4: Paste code in editor
                print("📝 Step 4: Pasting code in editor...")
                
                # Wait a moment for the editor to load
                time.sleep(2)
                
                try:
                    # Try your specific xpath for the editor
                    editor = page.locator('//*[@id="editor"]/div[2]/div')
                    
                    # Clear any existing content and paste new code
                    editor.click()
                    page.keyboard.press('Control+a')  # Select all
                    page.keyboard.type(source_code)
                    
                    print("✅ Code pasted successfully!")
                    
                except Exception as e:
                    print(f"⚠️  Could not find editor with xpath, trying alternatives...")
                    
                    # Try alternative selectors for code editor
                    editor_selectors = [
                        'textarea[name="source"]',
                        '#source',
                        '.CodeMirror-code',
                        'textarea.form-control',
                    ]
                    
                    success = False
                    for selector in editor_selectors:
                        try:
                            page.fill(selector, source_code)
                            print(f"✅ Code pasted using selector: {selector}")
                            success = True
                            break
                        except:
                            continue
                    
                    if not success:
                        print("❌ Could not find code editor")
                        browser.close()
                        return False
                
                # Step 5: Submit the solution
                print("🚀 Step 5: Submitting solution...")
                
                try:
                    # Try your specific xpath for submit button
                    submit_button = page.locator('//*[@id="singlePageSubmitButton"]')
                    submit_button.click()
                    
                    print("✅ Submission button clicked!")
                    
                except Exception as e:
                    print(f"⚠️  Could not find submit button with xpath, trying alternatives...")
                    
                    # Try alternative submit buttons
                    submit_selectors = [
                        'input[type="submit"]',
                        'button:has-text("Submit")',
                        '.submit',
                        '#submitButton'
                    ]
                    
                    success = False
                    for selector in submit_selectors:
                        try:
                            page.click(selector)
                            print(f"✅ Submitted using selector: {selector}")
                            success = True
                            break
                        except:
                            continue
                    
                    if not success:
                        print("❌ Could not find submit button")
                        browser.close()
                        return False
                
                # Step 6: Wait for submission to process and navigate to status page
                print("⏳ Step 6: Waiting for submission to process...")
                page.wait_for_load_state('networkidle')
                time.sleep(3)
                
                current_url = page.url
                print(f"📍 Current URL: {current_url}")
                submission_id = None
                
                # Try to navigate to status page if not already there
                if 'status' not in current_url:
                    print("🔄 Navigating to status page...")
                    page.goto("https://codeforces.com/problemset/status?my=on", wait_until='networkidle')
                    time.sleep(2)
                
                # Step 7: Extract submission ID using your XPath
                try:
                    submission_link = page.locator('//*[@id="pageContent"]/div[4]/div[6]/table/tbody/tr[2]/td[1]/a').first
                    if submission_link.is_visible():
                        submission_id = submission_link.inner_text().strip()
                        print(f"🎯 Submission ID: {submission_id}")
                    else:
                        # Fallback: try to extract from any URL if we can find it
                        match = re.search(r'/submission/(\d+)', current_url)
                        if match:
                            submission_id = match.group(1)
                            print(f"🎯 Submission ID (from URL): {submission_id}")
                        else:
                            # Try to find any submission ID in the page
                            page_content = page.content()
                            id_match = re.search(r'"submissionId":\s*(\d+)', page_content)
                            if id_match:
                                submission_id = id_match.group(1)
                                print(f"🎯 Submission ID (from page): {submission_id}")
                except Exception as e:
                    print(f"⚠️  Could not extract submission ID: {e}")
                
                print("🎉 Solution submitted successfully!")
                
                # Step 8: Poll for verdict using your XPath elements
                verdict = await_verdict(page, submission_id)
                
                if verdict and verdict != "Timeout":
                    print(f"🏆 Final Verdict: {verdict}")
                    
                    # Step 9: Get detailed results via API if submission ID was found
                    if submission_id:
                        detailed_results = get_detailed_results(page, submission_id)
                        if detailed_results and len(detailed_results) > 50:  # Check if we got meaningful data
                            print("📊 Detailed Results Available")
                            # Parse the results if they're JSON
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
                    
                    print("🔍 Submission completed! Browser will close in 5 seconds...")
                    time.sleep(5)
                    browser.close()
                    return is_accepted
                else:
                    print("⏰ Could not determine final verdict within timeout")
                    print("🔍 Browser will stay open for manual inspection...")
                    input("Press Enter to close browser...")
                    browser.close()
                    return False
                    
            except Exception as inner_error:
                print(f"❌ Error during submission process: {inner_error}")
                return False
                
            finally:
                # Ensure browser is closed
                if browser:
                    try:
                        browser.close()
                    except:
                        pass
                        
    except Exception as e:
        print(f"❌ Submission error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Submit solution to Codeforces using Playwright")
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
    
    print("🚀 **Codeforces Playwright Submission**")
    print("=" * 40)
    print()
    
    success = submit_with_playwright(
        args.solution_file,
        contest_id,
        problem_letter.upper()
    )
    
    if success:
        print("\n🎉 **Submission Complete!**")
    else:
        print("\n❌ **Submission Failed!**")

if __name__ == "__main__":
    main()
