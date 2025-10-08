#!/usr/bin/env python3
"""
Script to load all problems from the problems directory.
"""

import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.db import init_db
from core.data_loader import load_all_problems_from_directory

def main():
    print("Initializing database...")
    init_db()
    
    print("Loading all problems from problems/ directory...")
    loaded_problems = load_all_problems_from_directory("problems")
    
    print("\n" + "="*50)
    print("✅ Batch problem loading complete!")
    print("="*50)
    print(f"Successfully loaded {len(loaded_problems)} problems")
    
    if loaded_problems:
        print("\nLoaded problems:")
        for problem_id in loaded_problems[:10]:  # Show first 10
            print(f"  - {problem_id}")
        if len(loaded_problems) > 10:
            print(f"  ... and {len(loaded_problems) - 10} more")
    
    print(f"\nNext steps:")
    print("1. Add contest mappings for problems you want to submit to Codeforces")
    print("2. Configure your .env file with API keys")
    print("3. Setup Playwright authentication")
    print("4. Test solving: python apps/cli/run_session.py --contest-id 2072 --letter F")

if __name__ == "__main__":
    main()
