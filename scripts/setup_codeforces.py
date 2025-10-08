#!/usr/bin/env python3
"""
Setup script for Codeforces integration.
"""

import os
import sys
import getpass

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.codeforces_client import CodeforcesClient

def setup_credentials():
    """Setup Codeforces credentials."""
    print("🔐 **Codeforces Credentials Setup**")
    print("=" * 40)
    
    env_file = ".env"
    
    if os.path.exists(env_file):
        print("✅ Found existing .env file")
        
        # Read existing content
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Check if credentials already exist
        has_username = "CF_USERNAME=" in content and not content.count("CF_USERNAME=your_codeforces_username")
        has_password = "CF_PASSWORD=" in content and not content.count("CF_PASSWORD=your_codeforces_password")
        
        if has_username and has_password:
            print("✅ Codeforces credentials already configured")
            return True
            
    else:
        print("📄 No .env file found, creating from template...")
        # Copy from .env.example
        if os.path.exists(".env.example"):
            with open(".env.example", 'r') as f:
                content = f.read()
        else:
            content = "# Codeforces credentials\nCF_USERNAME=\nCF_PASSWORD=\n"
    
    print("\n📝 Please provide your Codeforces credentials:")
    print("   (These will be stored in your .env file)")
    
    username = input("Codeforces Username: ").strip()
    if not username:
        print("❌ Username is required")
        return False
        
    password = getpass.getpass("Codeforces Password: ").strip()
    if not password:
        print("❌ Password is required")
        return False
    
    # Update or add credentials
    lines = content.split('\n')
    updated_lines = []
    found_username = False
    found_password = False
    
    for line in lines:
        if line.startswith('CF_USERNAME='):
            updated_lines.append(f'CF_USERNAME={username}')
            found_username = True
        elif line.startswith('CF_PASSWORD='):
            updated_lines.append(f'CF_PASSWORD={password}')
            found_password = True
        else:
            updated_lines.append(line)
    
    # Add if not found
    if not found_username:
        updated_lines.append(f'CF_USERNAME={username}')
    if not found_password:
        updated_lines.append(f'CF_PASSWORD={password}')
    
    # Write back to .env
    with open(env_file, 'w') as f:
        f.write('\n'.join(updated_lines))
    
    print(f"✅ Credentials saved to {env_file}")
    return True

def test_login():
    """Test login with the configured credentials."""
    print("\n🧪 **Testing Login**")
    print("=" * 20)
    
    try:
        # Reload environment
        from dotenv import load_dotenv
        load_dotenv(override=True)
        
        from core.config import CF_USERNAME, CF_PASSWORD
        
        if not CF_USERNAME or not CF_PASSWORD:
            print("❌ Credentials not found in environment")
            return False
            
        client = CodeforcesClient()
        success = client.login()
        
        if success:
            print("✅ Login successful!")
            print("🎉 Codeforces integration is ready!")
            return True
        else:
            print("❌ Login failed")
            print("   Please check your credentials and try again")
            return False
            
    except Exception as e:
        print(f"❌ Login test error: {e}")
        return False

def setup_captcha_service():
    """Setup CAPTCHA solving service (optional)."""
    print("\n🤖 **CAPTCHA Solving Setup (Optional)**")
    print("=" * 45)
    
    print("For fully automated submissions, you may want to configure")
    print("a CAPTCHA solving service for when Codeforces shows CAPTCHAs.")
    print()
    print("Supported services:")
    print("  1. 2captcha.com - Popular and reliable")
    print("  2. Anti-Captcha - Alternative service")
    print("  3. None - Skip CAPTCHA solving (manual intervention required)")
    
    choice = input("\nChoose service (1/2/3): ").strip()
    
    env_file = ".env"
    
    with open(env_file, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    updated_lines = []
    found_service = False
    found_key = False
    
    if choice == "1":
        service = "2captcha"
        print(f"\n📝 Setting up {service}...")
        print("   Get your API key from: https://2captcha.com/account")
        api_key = input("2captcha API Key (or press Enter to skip): ").strip()
    elif choice == "2":
        service = "anticaptcha"
        print(f"\n📝 Setting up {service}...")
        print("   Get your API key from: https://anti-captcha.com/settings")
        api_key = input("Anti-Captcha API Key (or press Enter to skip): ").strip()
    else:
        service = "none"
        api_key = ""
        print("⚠️  CAPTCHA solving disabled")
    
    # Update configuration
    for line in lines:
        if line.startswith('CAPTCHA_SERVICE='):
            updated_lines.append(f'CAPTCHA_SERVICE={service}')
            found_service = True
        elif line.startswith('CAPTCHA_API_KEY='):
            updated_lines.append(f'CAPTCHA_API_KEY={api_key}')
            found_key = True
        else:
            updated_lines.append(line)
    
    if not found_service:
        updated_lines.append(f'CAPTCHA_SERVICE={service}')
    if not found_key:
        updated_lines.append(f'CAPTCHA_API_KEY={api_key}')
    
    with open(env_file, 'w') as f:
        f.write('\n'.join(updated_lines))
    
    if service != "none" and api_key:
        print(f"✅ {service} configured successfully")
    else:
        print("✅ CAPTCHA service configuration complete")

def setup_contest_mapping():
    """Help user set up contest mappings."""
    print("\n🎯 **Contest Mapping Setup**")
    print("=" * 30)
    
    print("To submit solutions, you need to map your problems to")
    print("actual Codeforces contests. Here's how:")
    print()
    print("1. Find your problem in Codeforces Gym")
    print("2. Note the contest ID and problem letter")
    print("3. Add mapping using this command:")
    print()
    print("   python -c \"")
    print("   from core.data_loader import add_contest_mapping")
    print("   add_contest_mapping(2051, 'E', 123456, 'A')")
    print("   \"")
    print()
    print("Where:")
    print("  - 2051, 'E' = Your problem (contest_id, letter)")
    print("  - 123456, 'A' = Codeforces gym contest and problem")
    
    example = input("\nWould you like to add a mapping now? (y/n): ").strip().lower()
    
    if example in ['y', 'yes']:
        try:
            print("\nExample: Map problem 2051_E to CF contest 102951 problem A")
            
            our_contest = input("Your contest ID (e.g., 2051): ").strip()
            our_letter = input("Your problem letter (e.g., E): ").strip().upper()
            cf_contest = input("Codeforces gym contest ID (e.g., 102951): ").strip()
            cf_letter = input("Codeforces problem letter (e.g., A): ").strip().upper()
            
            if all([our_contest, our_letter, cf_contest, cf_letter]):
                from core.data_loader import add_contest_mapping
                from core.db import init_db
                
                init_db()
                add_contest_mapping(
                    int(our_contest), 
                    our_letter, 
                    int(cf_contest), 
                    cf_letter
                )
                print("✅ Contest mapping added successfully!")
            else:
                print("⚠️  Incomplete information, skipping mapping")
                
        except Exception as e:
            print(f"❌ Error adding mapping: {e}")

def main():
    print("🚀 **Codeforces Integration Setup**")
    print("=" * 50)
    print()
    print("This script will help you set up Codeforces integration")
    print("for automated solution submission and verdict polling.")
    print()
    
    # Step 1: Credentials
    if not setup_credentials():
        print("❌ Setup failed at credentials step")
        return
    
    # Step 2: Test login
    if not test_login():
        print("❌ Setup failed at login test")
        return
    
    # Step 3: CAPTCHA service (optional)
    setup_captcha_service()
    
    # Step 4: Contest mapping info
    setup_contest_mapping()
    
    print("\n" + "=" * 50)
    print("🎉 **Setup Complete!**")
    print("=" * 50)
    print()
    print("✅ Codeforces client ready for submissions")
    print("✅ Cloudflare bypass working")
    print("✅ Authentication configured")
    print()
    print("📝 **Next Steps:**")
    print("   1. Add contest mappings for problems you want to solve")
    print("   2. Test with: python apps/cli/run_session.py --contest-id 2051 --letter E")
    print("   3. Monitor solutions in the solutions/ directory")
    print()
    print("🔧 **Troubleshooting:**")
    print("   - If login fails, check your credentials")
    print("   - For CAPTCHAs, configure a solving service")
    print("   - Test connection: python apps/cli/test_codeforces.py")

if __name__ == "__main__":
    main()
