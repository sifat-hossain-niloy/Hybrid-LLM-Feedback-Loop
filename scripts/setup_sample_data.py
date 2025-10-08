#!/usr/bin/env python3
"""
Setup script to initialize the database and load a few sample problems for testing.
"""

import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.db import init_db
from core.data_loader import load_problems_from_file, add_contest_mapping

def setup_sample_data():
    """Initialize database and load a few sample problems."""
    print("Initializing database...")
    init_db()
    
    # Find a few sample problems to load for testing
    problems_dir = os.path.join(os.path.dirname(__file__), '..', 'problems')
    
    if not os.path.exists(problems_dir):
        print("Problems directory not found!")
        return
    
    problem_files = [f for f in os.listdir(problems_dir) if f.endswith('.json')][:5]  # Load first 5
    
    if not problem_files:
        print("No problem files found in problems/ directory!")
        return
    
    print(f"Loading {len(problem_files)} sample problems...")
    loaded_problems = []
    
    for filename in problem_files:
        filepath = os.path.join(problems_dir, filename)
        try:
            problem_id = load_problems_from_file(filepath)
            loaded_problems.append((problem_id, filename))
        except Exception as e:
            print(f"Error loading {filename}: {e}")
    
    # Add sample contest mappings (you'll need to replace with actual CF contests)
    print("\nAdding sample contest mappings...")
    for problem_id, filename in loaded_problems[:2]:  # Map first 2 problems
        parts = problem_id.split('_')
        if len(parts) == 2:
            contest_id, letter = int(parts[0]), parts[1]
            # Example mapping - you'll need real CF contest IDs
            add_contest_mapping(
                contest_id=contest_id,
                letter=letter,
                cf_contest_id=102951,  # Example CF gym contest ID
                cf_problem_index=letter
            )
    
    print("\n" + "="*50)
    print("✅ Sample data setup complete!")
    print("="*50)
    print(f"Loaded {len(loaded_problems)} problems:")
    for problem_id, filename in loaded_problems:
        print(f"  - {problem_id} (from {filename})")
    
    print("\nNext steps:")
    print("1. Load all problems: python scripts/load_all_problems.py")
    print("2. Update your .env file with API keys")
    print("3. Setup Playwright authentication for Codeforces")
    print("4. Update contest mappings with real CF contest IDs")
    print("5. Test solving: python apps/cli/run_session.py --contest-id 2072 --letter F")

if __name__ == "__main__":
    setup_sample_data()
