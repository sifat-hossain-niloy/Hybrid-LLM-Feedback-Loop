#!/usr/bin/env python3
"""
Launch Chromium with remote debugging for automated submissions
"""

import os
import sys
import time
import subprocess
import platform
from pathlib import Path

def find_chromium_executable():
    """Find Chromium or Chrome executable based on OS"""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        paths = [
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        ]
    elif system == "Windows":
        paths = [
            r"C:\Program Files\Chromium\Application\chrome.exe",
            r"C:\Program Files (x86)\Chromium\Application\chrome.exe",
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
    else:  # Linux
        paths = [
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/usr/bin/google-chrome",
            "/snap/bin/chromium",
        ]
    
    for path in paths:
        if os.path.exists(path):
            return path
    
    return None

def is_port_in_use(port):
    """Check if a port is already in use"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def get_user_data_dir(profile_name):
    """Get user data directory based on OS"""
    system = platform.system()
    home = Path.home()
    
    if system == "Darwin":  # macOS
        base = home / "Library" / "Application Support" / "Chromium-Profiles"
    elif system == "Windows":
        base = home / "AppData" / "Local" / "Chromium-Profiles"
    else:  # Linux
        base = home / ".config" / "chromium-profiles"
    
    return base / profile_name

def launch_chromium(profile="Sifat", port=9222, url="https://codeforces.com"):
    """Launch Chromium with remote debugging enabled"""
    
    print("="*60)
    print("   Chromium Launcher for Automated Solver")
    print("="*60)
    print()
    
    # Check if already running
    if is_port_in_use(port):
        print(f"✓ Chromium is already running on port {port}")
        print()
        return True
    
    # Find Chromium executable
    chromium_path = find_chromium_executable()
    if not chromium_path:
        print("❌ Chromium/Chrome not found!")
        print()
        print("Please install Chromium:")
        if platform.system() == "Darwin":
            print("  brew install --cask chromium")
        elif platform.system() == "Windows":
            print("  Download from: https://www.chromium.org/getting-involved/download-chromium/")
        else:
            print("  sudo apt install chromium-browser")
        print()
        return False
    
    # Get user data directory
    user_data_dir = get_user_data_dir(profile)
    user_data_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Profile: {profile}")
    print(f"Port: {port}")
    print(f"Executable: {chromium_path}")
    print(f"User Data: {user_data_dir}")
    print()
    
    # Launch Chromium
    print("🚀 Launching Chromium...")
    
    cmd = [
        chromium_path,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={user_data_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        url
    ]
    
    try:
        # Launch in background
        if platform.system() == "Windows":
            # Windows: use CREATE_NEW_PROCESS_GROUP to detach
            subprocess.Popen(
                cmd,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            # Unix: use nohup-like behavior
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
        
        # Wait for Chromium to start
        print("Waiting for Chromium to start...", end="", flush=True)
        for i in range(10):
            time.sleep(1)
            print(".", end="", flush=True)
            if is_port_in_use(port):
                print(" ✓")
                break
        else:
            print(" ✗")
            print()
            print("❌ Chromium didn't start within 10 seconds")
            return False
        
        print()
        print("✓ Chromium is running successfully!")
        print()
        print("Next steps:")
        print("  1. Login to Codeforces in the browser (if needed)")
        print("  2. Run the automated solver:")
        print("     python3 run_solver_2041A.py")
        print()
        print("Note: Keep the Chromium window open while solving problems")
        print()
        
        return True
        
    except Exception as e:
        print()
        print(f"❌ Failed to launch Chromium: {e}")
        return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Launch Chromium for automated submissions")
    parser.add_argument("--profile", default="Sifat", help="Profile name (default: Sifat)")
    parser.add_argument("--port", type=int, default=9222, help="Remote debugging port (default: 9222)")
    parser.add_argument("--url", default="https://codeforces.com", help="URL to open (default: https://codeforces.com)")
    
    args = parser.parse_args()
    
    success = launch_chromium(args.profile, args.port, args.url)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

