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

def await_verdict(page, submission_id, max_wait_time=120):
    """Poll for verdict using XPath elements until not 'Running...'"""
    print("⏳ Polling for verdict... (this may take up to 2 minutes)")
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
                    # Wait a bit for API calls to complete after verdict appears
                    print("⏳ Waiting for API responses to complete...")
                    time.sleep(3)  # Give time for API calls to finish
                    
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
                                    # Wait a bit for API calls to complete after verdict appears
                                    print("⏳ Waiting for API responses to complete...")
                                    time.sleep(3)  # Give time for API calls to finish
                                    
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
    """Click on submission ID to get detailed popup results from #facebox"""
    try:
        print(f"🖱️  Clicking on submission ID {submission_id} for details...")
        
        # Find and click the submission ID link
        submission_link = page.locator(f'a:has-text("{submission_id}")').first
        if submission_link.is_visible():
            submission_link.click()
            
            # Wait for the facebox popup to appear
            print("⏳ Waiting for facebox popup...")
            try:
                page.wait_for_selector('#facebox', state='visible', timeout=10000)
                page.wait_for_timeout(2000)  # Extra wait for content to load
                print("✅ Facebox popup appeared!")
            except Exception as e:
                print(f"⚠️  Facebox not found: {e}")
                return None
            
            # Extract ALL test case divs - handle both single and multiple test cases
            try:
                # Get all test case containers
                # For single test: /html/body/div[11]/div/div/div/div
                # For multiple tests: /html/body/div[11]/div/div/div/div[1], div[2], etc.
                test_containers = page.locator('/html/body/div[11]/div/div/div/div').all()
                
                print(f"✅ Found {len(test_containers)} test case containers")
                
                test_results = []
                facebox_html_all = ""
                facebox_text_all = ""
                
                for idx, container in enumerate(test_containers, 1):
                    try:
                        test_html = container.inner_html()
                        test_text = container.inner_text()
                        
                        facebox_html_all += test_html + "\n"
                        facebox_text_all += test_text + "\n\n"
                        
                        print(f"  📋 Parsing test case {idx}: {len(test_html)} chars")
                        
                        # Parse using HTML structure (more reliable than text parsing)
                        # Extract test header info
                        test_header_match = re.search(r'Test:\s*#<span[^>]*>(\d+)</span>', test_html)
                        test_number = test_header_match.group(1) if test_header_match else str(idx)
                        
                        time_match = re.search(r'time:\s*<span[^>]*>(\d+)</span>', test_html)
                        memory_match = re.search(r'memory:\s*<span[^>]*>(\d+)</span>', test_html)
                        verdict_match = re.search(r'verdict:\s*<span[^>]*>([^<]+)</span>', test_html)
                        
                        # Extract input, output, answer, checker log using HTML classes
                        input_match = re.search(r'<pre class="input">([^<]*)</pre>', test_html, re.DOTALL)
                        output_match = re.search(r'<pre class="output">([^<]*)</pre>', test_html, re.DOTALL)
                        answer_match = re.search(r'<pre class="answer">([^<]*)</pre>', test_html, re.DOTALL)
                        checker_match = re.search(r'<pre class="checker">([^<]*)</pre>', test_html, re.DOTALL)
                        
                        current_test = {
                            'test_id': f"Test #{test_number}",
                            'test_number': test_number
                        }
                        
                        if time_match:
                            current_test['time'] = f"{time_match.group(1)} ms"
                        if memory_match:
                            current_test['memory'] = f"{memory_match.group(1)} KB"
                        if verdict_match:
                            current_test['verdict'] = verdict_match.group(1).strip()
                        
                        if input_match:
                            current_test['input'] = input_match.group(1).strip()
                        if output_match:
                            current_test['output'] = output_match.group(1).strip()
                        if answer_match:
                            current_test['answer'] = answer_match.group(1).strip()
                        if checker_match:
                            current_test['checker_log'] = checker_match.group(1).strip()
                        
                        test_results.append(current_test)
                        print(f"    ✅ Test #{test_number}: {current_test.get('verdict', 'N/A')}")
                        
                    except Exception as e:
                        print(f"    ⚠️ Error parsing container {idx}: {e}")
                        continue
                
                facebox_html = facebox_html_all
                facebox_text = facebox_text_all
                
                if test_results:
                    print(f"✅ Extracted facebox content: {len(facebox_html)} chars HTML, {len(facebox_text)} chars text")
                    
                    print(f"✅ Parsed {len(test_results)} test cases from facebox")
                    
                    result = {
                        "method": "facebox_extraction",
                        "submission_id": submission_id,
                        "facebox_html": facebox_html,
                        "facebox_text": facebox_text,
                        "test_results": test_results,
                        "test_count": len(test_results),
                        "page_title": page.title(),
                        "current_url": page.url
                    }
                    
                    return json.dumps(result, indent=2)
                else:
                    print("⚠️  Facebox content not visible")
                    return None
            except Exception as e:
                print(f"⚠️  Error extracting facebox content: {e}")
                return None
        else:
            print(f"⚠️  Could not find clickable submission ID {submission_id}")
            return None
            
    except Exception as e:
        print(f"⚠️  Error clicking submission ID: {e}")
        return None

def get_detailed_results(page, submission_id, captured_api_responses=None):
    """Enhanced method to get detailed submission results via multiple approaches"""
    from datetime import datetime
    import os
    import json  # Import at function level
    
    try:
        print("📊 Getting detailed results using multiple methods...")
        
        # Method 1: Use API responses captured during verdict polling (most reliable!)
        if captured_api_responses is None:
            captured_api_responses = []
        
        captured_responses = captured_api_responses
        comprehensive_data = None
        filename = None
        initial_response_count = len(captured_responses)  # Track count before click
        
        if captured_responses:
            print(f"✅ Using {len(captured_responses)} API responses captured during polling")
            for i, resp in enumerate(captured_responses, 1):
                print(f"   Response {i}: {resp.get('url', 'unknown')[:80]}... ({resp.get('status', 'N/A')})")
            
            # IMMEDIATELY save API response to file (don't wait for facebox)
            api_response = captured_responses[-1]  # Use the latest response
            
            # Create api_responses directory if it doesn't exist
            api_dir = "api_responses"
            if not os.path.exists(api_dir):
                os.makedirs(api_dir)
            
            # Create filename with submission ID and timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{api_dir}/submission_{submission_id}_{timestamp}.json"
            
            # Prepare data to save
            comprehensive_data = {
                "submission_id": submission_id,
                "timestamp": datetime.now().isoformat(),
                "collection_methods": ["api_interception"]
            }
            
            comprehensive_data["api_response"] = api_response
            
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
                        for i in range(1, min(int(test_count) + 1, 4)):  # Show first 3
                            verdict_key = f"verdict#{i}"
                            if verdict_key in parsed_api:
                                print(f"🧪 Test {i}: {parsed_api[verdict_key]}")
                    
                except json.JSONDecodeError as e:
                    print(f"⚠️  Could not parse API response as JSON: {e}")
            
            # Save immediately!
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(comprehensive_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Comprehensive results saved to: {filename}")
        
        # Method 2: Click on submission ID to get facebox details (this may trigger API calls!)
        click_results = click_submission_for_details(page, submission_id)
        
        # Give a moment for any API calls triggered by the click to complete
        time.sleep(2)
        
        # Check if clicking triggered NEW API responses (check count increased)
        if initial_response_count == 0 and len(captured_api_responses) > 0:
            print(f"✅ API responses captured during click: {len(captured_api_responses)}")
            captured_responses = captured_api_responses
            
            # Now save the API response that was just captured
            api_response = captured_responses[-1]
            api_dir = "api_responses"
            if not os.path.exists(api_dir):
                os.makedirs(api_dir)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{api_dir}/submission_{submission_id}_{timestamp}.json"
            
            comprehensive_data = {
                "submission_id": submission_id,
                "timestamp": datetime.now().isoformat(),
                "collection_methods": ["api_interception_via_click"]
            }
            
            comprehensive_data["api_response"] = api_response
            
            # Try to parse API response
            response_text = api_response.get("response_text", "")
            if response_text and response_text.strip().startswith('{'):
                try:
                    parsed_api = json.loads(response_text)
                    comprehensive_data["parsed_api_response"] = parsed_api
                    print("✅ API response parsed as JSON")
                    
                    if 'testCount' in parsed_api:
                        test_count = parsed_api['testCount']
                        print(f"📊 Test Count: {test_count}")
                        
                        if 'verdict' in parsed_api:
                            print(f"🏆 Overall Verdict: {parsed_api['verdict']}")
                        
                        for i in range(1, min(int(test_count) + 1, 4)):
                            verdict_key = f"verdict#{i}"
                            if verdict_key in parsed_api:
                                print(f"🧪 Test {i}: {parsed_api[verdict_key]}")
                except json.JSONDecodeError as e:
                    print(f"⚠️  Could not parse API response as JSON: {e}")
            
            # Save immediately!
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(comprehensive_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Comprehensive results saved to: {filename}")
        
        # Also check click results
        if click_results:
            try:
                click_data = json.loads(click_results)
                test_count = click_data.get('test_count', 0)
                print(f"📊 Facebox extraction found {test_count} test cases")
            except:
                pass
        
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
        
        # If we have facebox results, update the existing file
        if click_results and captured_responses:
            print("📝 Adding facebox data to existing API response file...")
            try:
                # Read the existing file
                import json
                with open(filename, 'r', encoding='utf-8') as f:
                    comprehensive_data = json.load(f)
                
                # Add facebox data
                if isinstance(click_results, str):
                    try:
                        click_data = json.loads(click_results)
                        comprehensive_data["click_results"] = click_results
                        if "test_results" in click_data:
                            comprehensive_data["test_results"] = click_data["test_results"]
                            print(f"✅ Added {len(click_data['test_results'])} test cases from facebox")
                    except json.JSONDecodeError:
                        comprehensive_data["click_results"] = click_results
                else:
                    comprehensive_data["click_results"] = click_results
                
                if "click_extraction" not in comprehensive_data.get("collection_methods", []):
                    comprehensive_data["collection_methods"].append("click_extraction")
                
                # Save updated data
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(comprehensive_data, f, indent=2, ensure_ascii=False)
                
                print(f"💾 Updated file with facebox data: {filename}")
                return comprehensive_data
                
            except Exception as e:
                print(f"⚠️  Could not update file with facebox data: {e}")
                return comprehensive_data if captured_responses else None
        
        # If we only have API response (already saved) or only facebox
        if captured_responses:
            return comprehensive_data
        elif click_results:
            # Only facebox, no API response - save it
            from datetime import datetime
            import os
            
            api_dir = "api_responses"
            if not os.path.exists(api_dir):
                os.makedirs(api_dir)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{api_dir}/submission_{submission_id}_{timestamp}.json"
            
            comprehensive_data = {
                "submission_id": submission_id,
                "timestamp": datetime.now().isoformat(),
                "collection_methods": ["click_extraction"],
                "click_results": click_results
            }
            
            # Extract test_results if available
            if isinstance(click_results, str):
                try:
                    click_data = json.loads(click_results)
                    if "test_results" in click_data:
                        comprehensive_data["test_results"] = click_data["test_results"]
                except:
                    pass
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(comprehensive_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Facebox results saved to: {filename}")
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

def submit_with_existing_chrome(solution_file: str, contest_id: int, problem_letter: str, port=9222, no_interactive=False):
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
                if not no_interactive:
                    print("   I'll wait for you to login...")
                    input("Press Enter after logging in...")
                else:
                    print("❌ Not logged in and running in non-interactive mode")
                    return False
            
            print()
            print("🎯 **Automated submission process starting...**")
            
            try:
                # Step 1: Find and click submit link
                print("🔗 Step 1: Looking for Submit button...")
                
                # Wait for page to be fully loaded
                page.wait_for_load_state('networkidle', timeout=15000)
                time.sleep(3)
                
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
                    if not no_interactive:
                        print("   Please click the Submit button manually in the browser")
                        input("Press Enter after clicking Submit...")
                    else:
                        print("❌ Cannot proceed in non-interactive mode")
                        return False
                
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
                    if not no_interactive:
                        print("   The code is in your clipboard - please paste it manually")
                        print(f"   Code length: {len(source_code)} characters")
                        input("Press Enter after pasting code...")
                    else:
                        print("❌ Cannot proceed in non-interactive mode")
                        return False
                
                # Step 3: Submit the solution
                print("🚀 Step 3: Submitting solution...")
                time.sleep(1)
                
                # Try multiple submit button selectors
                submit_btn_selectors = [
                    '#singlePageSubmitButton',  # Direct ID selector - most reliable
                    'input[type="submit"]',
                    'button:has-text("Submit")',
                    '//*[@id="singlePageSubmitButton"]',  # XPath version
                    '.submit-button',
                    '#submitButton'
                ]
                
                submitted = False
                for selector in submit_btn_selectors:
                    try:
                        if selector.startswith('//'):
                            page.locator(f'xpath={selector}').click(timeout=5000)
                        else:
                            page.click(selector, timeout=5000)
                        
                        print(f"✅ Submit button clicked using: {selector}")
                        submitted = True
                        time.sleep(2)  # Wait for submission to process
                        break
                    except Exception as e:
                        # Only show error for first selector attempt
                        if selector == submit_btn_selectors[0]:
                            print(f"   Trying alternative selectors...")
                        continue
                
                if not submitted:
                    print("⚠️  Could not click submit button automatically")
                    if not no_interactive:
                        print("   Please click the Submit button manually")
                        input("Press Enter after submitting...")
                    else:
                        print("❌ Cannot proceed in non-interactive mode")
                        return False
                
                # Step 4: Navigate to status page and get submission ID
                print("⏳ Step 4: Waiting for submission to be recorded...")
                time.sleep(5)  # Increased wait time for submission to be recorded
                
                current_url = page.url
                print(f"📍 Current URL: {current_url}")
                submission_id = None
                
                # Navigate to status page to get submission details
                if 'status' not in current_url:
                    print("🔄 Navigating to status page...")
                    try:
                        page.goto("https://codeforces.com/problemset/status?my=on", wait_until='domcontentloaded', timeout=10000)
                        time.sleep(3)
                    except Exception as e:
                        print(f"⚠️  Navigation warning: {e}")
                        # Try alternative navigation
                        page.goto("https://codeforces.com/submissions", wait_until='domcontentloaded', timeout=10000)
                        time.sleep(3)
                    
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
                
                # Step 5.5: Set up API interception BEFORE polling (API calls happen during polling!)
                captured_api_responses = []
                all_urls_seen = []  # Debug: track all URLs
                
                def handle_api_response(response):
                    """Synchronous handler for Playwright's sync API"""
                    try:
                        url = response.url
                        
                        # Debug: Log all URLs from codeforces
                        if 'codeforces.com' in url and '/data/' in url:
                            all_urls_seen.append(url)
                            print(f"🔍 DEBUG: Codeforces /data/ URL seen: {url[:100]}")
                        
                        # Look for submitSource API calls
                        if 'data/submitSource' in url or 'submissionVerdict' in url:
                            print(f"🎯 MATCHED API call: {url}")
                            
                            # Extract rv parameter from URL
                            rv_match = re.search(r'rv=([a-zA-Z0-9]+)', url)
                            rv_param = rv_match.group(1) if rv_match else "unknown"
                            
                            # Get response text (synchronous in sync Playwright)
                            try:
                                response_text = response.text()
                                print(f"✅ Captured API response ({len(response_text)} chars)")
                                
                                captured_api_responses.append({
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
                
                # Set up response listener BEFORE polling starts
                page.on("response", handle_api_response)
                print("🎯 API interception enabled (will capture during verdict polling)")
                
                # Step 6: Poll for verdict using your XPath elements
                verdict = await_verdict(page, submission_id)
                
                # Debug: Show what /data/ URLs were seen
                print(f"\n🔍 DEBUG: Total Codeforces /data/ URLs seen: {len(all_urls_seen)}")
                if all_urls_seen:
                    for url in all_urls_seen[:5]:  # Show first 5
                        print(f"   - {url[:120]}")
                
                # Step 7: Get detailed results via API - do this ALWAYS if we have submission_id
                # (even on timeout, because we may have captured API responses)
                if submission_id and captured_api_responses:
                    print(f"📊 Captured {len(captured_api_responses)} API responses during polling")
                    detailed_results = get_detailed_results(page, submission_id, captured_api_responses)
                    if detailed_results:
                        print("📊 Detailed Results Available")
                
                if verdict and verdict != "Timeout":
                    print(f"🏆 Final Verdict: {verdict}")
                    
                    # If we didn't save API responses above (no responses during polling), try clicking
                    if submission_id and not captured_api_responses:
                        print(f"📊 No API responses during polling, trying click method...")
                        detailed_results = get_detailed_results(page, submission_id, captured_api_responses)
                        if detailed_results:
                            print("📊 Detailed Results Available")
                            # detailed_results is a dict, convert to JSON for printing
                            try:
                                # Print summary from the dict
                                if 'compilationError' in detailed_results:
                                    print(f"⚠️  Compilation Error: {detailed_results['compilationError']}")
                                
                                # Check for facebox test results
                                if 'click_results' in detailed_results and isinstance(detailed_results['click_results'], str):
                                    try:
                                        click_data = json.loads(detailed_results['click_results'])
                                        if 'test_results' in click_data:
                                            test_count = click_data.get('test_count', len(click_data['test_results']))
                                            print(f"📊 Total Tests (Facebox): {test_count}")
                                            print(f"📊 Test Results Parsed from Facebox:")
                                            for i, test in enumerate(click_data['test_results'][:3], 1):  # Show first 3
                                                print(f"   Test {i}: {test.get('verdict', 'N/A')}")
                                                if test.get('checker_log'):
                                                    print(f"      Checker: {test['checker_log'][:80]}")
                                    except:
                                        pass
                                
                                # Print the FULL JSON for automated_solver to capture
                                print("\n📦 DETAILED_API_RESPONSE_START")
                                print(json.dumps(detailed_results, indent=2, ensure_ascii=False))
                                print("📦 DETAILED_API_RESPONSE_END\n")
                            except Exception as e:
                                print(f"⚠️  Error processing results: {e}")
                                print("📊 Raw Results:")
                                print(str(detailed_results)[:500])
                    
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
                    
                    if not no_interactive:
                        input("Press Enter to finish (browser will remain open)...")
                    return is_accepted
                else:
                    print("⏰ Could not determine final verdict within timeout")
                    print("🔍 Browser will remain open for manual inspection")
                    if not no_interactive:
                        input("Press Enter to finish...")
                    return False
                    
            except Exception as e:
                print(f"❌ Error during automated submission: {e}")
                print("   You can continue manually in the browser")
                if not no_interactive:
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
    parser.add_argument("--no-interactive", action="store_true", help="Skip interactive prompts (for automation)")
    
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
        print("   Please provide --contest-id and --problem arguments")
        print("   Example: --contest-id 2045 --problem A")
        sys.exit(1)
    
    # Start Chromium if requested
    if args.start_chrome:
        if not start_chromium_with_debugging(args.profile, args.port):
            return
    
    # Submit solution
    success = submit_with_existing_chrome(
        args.solution_file,
        contest_id,
        problem_letter.upper(),
        args.port,
        args.no_interactive
    )
    
    # Always return success (0) if submission was made, regardless of verdict
    # The verdict will be parsed from the output
    if success or success is not None:  # success can be True (Accepted) or False (other verdict)
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
