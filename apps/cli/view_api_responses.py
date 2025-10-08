#!/usr/bin/env python3
"""
View saved API responses from Codeforces submissions.
"""

import argparse
import json
import os
import glob
from datetime import datetime

def list_api_responses():
    """List all saved API responses."""
    api_dir = "api_responses"
    if not os.path.exists(api_dir):
        print("❌ No API responses directory found")
        print("   Submit some solutions first to generate API responses")
        return
    
    files = glob.glob(f"{api_dir}/submission_*.json")
    if not files:
        print("❌ No API responses found")
        return
    
    print("📊 **Saved API Responses**")
    print("=" * 50)
    
    # Sort by modification time (newest first)
    files.sort(key=os.path.getmtime, reverse=True)
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            submission_id = data.get('submission_id', 'Unknown')
            timestamp = data.get('timestamp', 'Unknown')
            file_size = os.path.getsize(file_path)
            
            print(f"📄 {os.path.basename(file_path)}")
            print(f"   🎯 Submission ID: {submission_id}")
            print(f"   ⏰ Timestamp: {timestamp}")
            print(f"   📏 Size: {file_size} bytes")
            
            # Show verdict if available (new format)
            if 'parsed_api_response' in data:
                parsed = data['parsed_api_response']
                if 'verdict' in parsed:
                    verdict_html = parsed['verdict']
                    if 'accepted' in verdict_html.lower():
                        print(f"   ✅ Verdict: ACCEPTED")
                    else:
                        print(f"   ❌ Verdict: {verdict_html[:50]}...")
                
                if 'testCount' in parsed:
                    test_count = int(parsed['testCount'])
                    print(f"   📊 Test Count: {test_count}")
                    
                    # Count verdicts
                    accepted_tests = 0
                    for i in range(1, test_count + 1):
                        verdict_key = f"verdict#{i}"
                        if verdict_key in parsed:
                            if 'OK' in parsed[verdict_key] or 'ACCEPTED' in parsed[verdict_key]:
                                accepted_tests += 1
                    print(f"   📊 Tests Passed: {accepted_tests}/{test_count}")
            
            # Also check old format for backward compatibility
            elif 'parsed_response' in data:
                parsed = data['parsed_response']
                if 'verdict' in parsed:
                    verdict = parsed['verdict']
                    if verdict == 'OK':
                        print(f"   ✅ Verdict: ACCEPTED")
                    else:
                        print(f"   ❌ Verdict: {verdict}")
                
                if 'testCount' in parsed:
                    passed = parsed.get('passedTestCount', 0)
                    total = parsed['testCount']
                    print(f"   📊 Tests: {passed}/{total}")
            
            # Show collection methods
            if 'collection_methods' in data:
                methods = data['collection_methods']
                print(f"   🔧 Methods: {', '.join(methods)}")
            
            print()
            
        except Exception as e:
            print(f"⚠️  Error reading {file_path}: {e}")

def view_api_response(submission_id):
    """View specific API response."""
    api_dir = "api_responses"
    
    # Find file with this submission ID
    files = glob.glob(f"{api_dir}/submission_{submission_id}_*.json")
    if not files:
        print(f"❌ No API response found for submission {submission_id}")
        return
    
    # Use the newest one if multiple exist
    file_path = max(files, key=os.path.getmtime)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📊 **API Response for Submission {submission_id}**")
        print("=" * 60)
        
        # Basic info
        print(f"🎯 Submission ID: {data.get('submission_id', 'Unknown')}")
        print(f"⏰ Timestamp: {data.get('timestamp', 'Unknown')}")
        
        # Show collection methods
        if 'collection_methods' in data:
            methods = data['collection_methods']
            print(f"🔧 Collection Methods: {', '.join(methods)}")
        
        # API response details
        if 'api_response' in data:
            api_data = data['api_response']
            print(f"🌐 API URL: {api_data.get('url', 'Unknown')}")
            print(f"📍 RV Parameter: {api_data.get('rv_parameter', 'Unknown')}")
        else:
            print(f"🌐 API URL: {data.get('api_url', 'Unknown')}")
            print(f"🔑 CSRF Token: {data.get('csrf_token', 'Unknown')[:8]}...")
            print(f"📍 RV Parameter: {data.get('rv_parameter', 'Unknown')}")
        print()
        
        # Parsed API response (new format)
        if 'parsed_api_response' in data:
            parsed = data['parsed_api_response']
            print("📋 **Parsed API Response:**")
            print("-" * 30)
            
            # Overall verdict
            if 'verdict' in parsed:
                verdict_html = parsed['verdict']
                print(f"🏆 Overall Verdict: {verdict_html}")
            
            # Problem info
            if 'problemName' in parsed:
                print(f"🎯 Problem: {parsed['problemName']}")
            if 'contestName' in parsed:
                print(f"🏆 Contest: {parsed['contestName']}")
            
            # Test results
            if 'testCount' in parsed:
                test_count = int(parsed['testCount'])
                print(f"📊 Test Count: {test_count}")
                
                # Show individual test results
                for i in range(1, test_count + 1):
                    verdict_key = f"verdict#{i}"
                    time_key = f"timeConsumed#{i}"
                    memory_key = f"memoryConsumed#{i}"
                    output_key = f"output#{i}"
                    answer_key = f"answer#{i}"
                    
                    if verdict_key in parsed:
                        verdict = parsed[verdict_key]
                        time_ms = parsed.get(time_key, 'N/A')
                        memory_kb = parsed.get(memory_key, 'N/A')
                        
                        status_icon = "✅" if 'OK' in verdict or 'ACCEPTED' in verdict else "❌"
                        print(f"   {status_icon} Test {i}: {verdict} ({time_ms}ms, {memory_kb}KB)")
                        
                        # Show output vs expected if failed
                        if status_icon == "❌" and output_key in parsed and answer_key in parsed:
                            output = parsed[output_key][:100]
                            expected = parsed[answer_key][:100]
                            print(f"      🔍 Got: {output}...")
                            print(f"      🎯 Expected: {expected}...")
                            
                            # Show checker error if available
                            checker_key = f"checkerStdoutAndStderr#{i}"
                            if checker_key in parsed and parsed[checker_key]:
                                print(f"      💬 Checker: {parsed[checker_key][:200]}...")
            
            # Source code
            if 'source' in parsed:
                source_code = parsed['source']
                print(f"💻 Source Code ({len(source_code)} chars):")
                # Show first few lines
                lines = source_code.split('\\n')[:10]
                for line in lines:
                    if line.strip():
                        print(f"   {line[:100]}")
                if len(source_code.split('\\n')) > 10:
                    print(f"   ... ({len(source_code.split('\\n'))} total lines)")
            
            print()
        
        # Parsed response (old format - backward compatibility)
        elif 'parsed_response' in data:
            parsed = data['parsed_response']
            print("📋 **Parsed Response:**")
            print("-" * 30)
            
            # Verdict
            if 'verdict' in parsed:
                verdict = parsed['verdict']
                if verdict == 'OK':
                    print(f"🏆 Verdict: ✅ ACCEPTED")
                else:
                    print(f"🏆 Verdict: ❌ {verdict}")
            
            # Test results
            if 'testCount' in parsed:
                passed = parsed.get('passedTestCount', 0)
                total = parsed['testCount']
                print(f"📊 Tests Passed: {passed}/{total}")
                
                if passed < total:
                    if 'checkerStderr' in parsed and parsed['checkerStderr']:
                        print(f"🔍 Checker Error: {parsed['checkerStderr']}")
            
            # Time and memory
            if 'timeConsumedMillis' in parsed:
                time_ms = parsed['timeConsumedMillis']
                print(f"⏱️  Time: {time_ms} ms")
            
            if 'memoryConsumedBytes' in parsed:
                memory_bytes = parsed['memoryConsumedBytes']
                memory_mb = memory_bytes / (1024 * 1024)
                print(f"💾 Memory: {memory_mb:.2f} MB")
            
            # Compilation error
            if 'compilationError' in parsed and parsed['compilationError']:
                print(f"🔨 Compilation Error:")
                print(parsed['compilationError'])
            
            # Source code
            if 'source' in parsed:
                source_preview = parsed['source'][:200]
                print(f"💻 Source Code Preview:")
                print(source_preview + ("..." if len(parsed['source']) > 200 else ""))
            
            print()
        
        # Raw response
        print("📄 **Raw Response:**")
        print("-" * 30)
        
        # Check new format first
        raw_response = None
        if 'api_response' in data and 'response_text' in data['api_response']:
            raw_response = data['api_response']['response_text']
        elif 'raw_response' in data:
            raw_response = data['raw_response']
        
        if raw_response:
            if isinstance(raw_response, str):
                if len(raw_response) > 500:
                    print(raw_response[:500] + "...")
                    print(f"\n(Truncated - full response is {len(raw_response)} characters)")
                else:
                    print(raw_response)
            else:
                print(json.dumps(raw_response, indent=2))
        else:
            print("No raw response available")
        
        # Click results if available
        if 'click_results' in data:
            click_data = data['click_results']
            print("\n🖱️  **Click Extraction Results:**")
            print("-" * 30)
            print(f"Method: {click_data.get('method', 'Unknown')}")
            print(f"Page Title: {click_data.get('page_title', 'Unknown')}")
            print(f"URL: {click_data.get('current_url', 'Unknown')}")
            
            if 'extracted_details' in click_data:
                details = click_data['extracted_details']
                for pattern, matches in details.items():
                    print(f"Pattern {pattern}: {len(matches)} matches")
                    for match in matches[:3]:  # Show first 3 matches
                        print(f"   - {match}")
                    if len(matches) > 3:
                        print(f"   ... and {len(matches) - 3} more")
            
    except Exception as e:
        print(f"❌ Error reading API response: {e}")

def main():
    parser = argparse.ArgumentParser(description="View saved Codeforces API responses")
    parser.add_argument("--submission-id", help="View specific submission ID")
    parser.add_argument("--list", action="store_true", help="List all saved responses")
    
    args = parser.parse_args()
    
    if args.submission_id:
        view_api_response(args.submission_id)
    elif args.list:
        list_api_responses()
    else:
        # Default: list all responses
        list_api_responses()

if __name__ == "__main__":
    main()
