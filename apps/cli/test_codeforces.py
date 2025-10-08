#!/usr/bin/env python3
"""
Test the Codeforces client functionality.
"""

import argparse
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from core.codeforces_client import CodeforcesClient
from core.config import CF_USERNAME, CF_PASSWORD

def test_basic_connection():
    """Test basic connection to Codeforces."""
    print("🌐 Testing basic connection to Codeforces...")
    
    try:
        client = CodeforcesClient()
        
        # Try to access the main page
        response = client.scraper.get("https://codeforces.com/")
        
        if response.status_code == 200:
            print("✅ Successfully connected to Codeforces")
            print(f"   Response size: {len(response.text)} bytes")
            
            if "codeforces" in response.text.lower():
                print("✅ Content looks valid")
            else:
                print("⚠️  Content might be blocked or unusual")
                
            return True
        else:
            print(f"❌ Connection failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_login():
    """Test login functionality."""
    print("🔐 Testing login functionality...")
    
    if not CF_USERNAME or not CF_PASSWORD:
        print("⚠️  No credentials provided in environment variables")
        print("   Set CF_USERNAME and CF_PASSWORD in your .env file to test login")
        return None
        
    try:
        client = CodeforcesClient()
        success = client.login()
        
        if success:
            print("✅ Login successful!")
            return True
        else:
            print("❌ Login failed")
            return False
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False

def test_language_detection(contest_id: int = 102951):
    """Test language detection for a contest."""
    print(f"💻 Testing language detection for contest {contest_id}...")
    
    try:
        client = CodeforcesClient()
        
        # Try to login first if credentials are available
        if CF_USERNAME and CF_PASSWORD:
            client.login()
            
        languages = client.get_language_options(contest_id)
        
        if languages:
            print(f"✅ Found {len(languages)} programming languages:")
            for name, id_num in list(languages.items())[:5]:  # Show first 5
                print(f"   {id_num}: {name}")
            if len(languages) > 5:
                print(f"   ... and {len(languages) - 5} more")
            return True
        else:
            print("⚠️  No languages found (might need login or contest doesn't exist)")
            return False
            
    except Exception as e:
        print(f"❌ Language detection error: {e}")
        return False

def test_submit_page_access(contest_id: int = 102951):
    """Test access to submit page."""
    print(f"📄 Testing access to submit page for contest {contest_id}...")
    
    try:
        client = CodeforcesClient()
        
        if CF_USERNAME and CF_PASSWORD:
            login_success = client.login()
            if not login_success:
                print("❌ Could not login, skipping submit page test")
                return False
        else:
            print("⚠️  No credentials provided, will test without login")
            
        submit_url = f"https://codeforces.com/gym/{contest_id}/submit"
        response = client.scraper.get(submit_url)
        
        if response.status_code == 200:
            print("✅ Successfully accessed submit page")
            
            # Check for key elements
            if 'programTypeId' in response.text:
                print("✅ Found language selector")
            if 'source' in response.text:
                print("✅ Found source code textarea")
            if 'submit' in response.text.lower():
                print("✅ Found submit button")
                
            return True
        else:
            print(f"❌ Failed to access submit page: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Submit page access error: {e}")
        return False

def run_all_tests(contest_id: int = 102951):
    """Run all tests."""
    print("🧪 **Codeforces Client Test Suite**")
    print("=" * 50)
    
    tests = [
        ("Basic Connection", test_basic_connection),
        ("Login", test_login),
        ("Language Detection", lambda: test_language_detection(contest_id)),
        ("Submit Page Access", lambda: test_submit_page_access(contest_id)),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 30)
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results[test_name] = False
            
    # Summary
    print("\n" + "=" * 50)
    print("📊 **Test Results Summary**")
    print("=" * 50)
    
    for test_name, result in results.items():
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⚠️  SKIP"
        print(f"{test_name:<25} {status}")
        
    passed = sum(1 for r in results.values() if r is True)
    total = len([r for r in results.values() if r is not None])
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total and total > 0:
        print("🎉 All tests passed! Codeforces client is ready.")
    elif passed > 0:
        print("⚠️  Some tests passed. Check configuration and credentials.")
    else:
        print("❌ No tests passed. Check your setup and internet connection.")
        
    return results

def main():
    parser = argparse.ArgumentParser(description="Test Codeforces client functionality")
    parser.add_argument("--contest-id", type=int, default=102951, help="Contest ID to test with")
    parser.add_argument("--test", choices=["connection", "login", "languages", "submit"], help="Run specific test")
    
    args = parser.parse_args()
    
    if args.test == "connection":
        test_basic_connection()
    elif args.test == "login":
        test_login()
    elif args.test == "languages":
        test_language_detection(args.contest_id)
    elif args.test == "submit":
        test_submit_page_access(args.contest_id)
    else:
        run_all_tests(args.contest_id)

if __name__ == "__main__":
    main()
