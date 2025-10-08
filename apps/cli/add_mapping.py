#!/usr/bin/env python3
"""
Add contest mappings for Codeforces submissions.
"""

import argparse
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from core.db import init_db
from core.data_loader import add_contest_mapping

def main():
    parser = argparse.ArgumentParser(description="Add contest mapping for Codeforces submissions")
    parser.add_argument("--our-contest", type=int, required=True, help="Our contest ID (e.g., 2051)")
    parser.add_argument("--our-letter", required=True, help="Our problem letter (e.g., E)")
    parser.add_argument("--cf-contest", type=int, required=True, help="Codeforces gym contest ID (e.g., 102951)")
    parser.add_argument("--cf-letter", required=True, help="Codeforces problem letter (e.g., A)")
    
    args = parser.parse_args()
    
    print("🎯 Adding contest mapping...")
    print(f"   {args.our_contest}{args.our_letter} -> CF gym {args.cf_contest}{args.cf_letter}")
    
    try:
        init_db()
        add_contest_mapping(
            args.our_contest,
            args.our_letter.upper(),
            args.cf_contest,
            args.cf_letter.upper()
        )
        print("✅ Contest mapping added successfully!")
        print(f"\nYou can now test with:")
        print(f"python apps/cli/run_session.py --contest-id {args.our_contest} --letter {args.our_letter.upper()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
