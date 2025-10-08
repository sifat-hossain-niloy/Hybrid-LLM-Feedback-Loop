import json
import uuid
import os
from typing import Dict, List, Any, Tuple
from core.db import get_session
from core.models import Problem, TestCase, ContestMap, TestKind

def parse_filename(filename: str) -> Tuple[int, str]:
    """Parse contest_id and letter from filename like '2072-F.json'."""
    basename = os.path.basename(filename)
    if basename.endswith('.json'):
        basename = basename[:-5]  # Remove .json extension
    
    parts = basename.split('-')
    if len(parts) != 2:
        raise ValueError(f"Invalid filename format: {filename}. Expected format: 'CONTEST_ID-LETTER.json'")
    
    try:
        contest_id = int(parts[0])
        letter = parts[1]
        return contest_id, letter
    except ValueError:
        raise ValueError(f"Invalid filename format: {filename}. Contest ID must be numeric.")

def parse_sample_tests(sample_tests: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Parse sample test cases from the scraped format."""
    test_cases = []
    
    for test_group in sample_tests:
        input_lines = test_group["input"].strip().split('\n')
        output_lines = test_group["output"].strip().split('\n')
        
        # Parse test count from first line
        if input_lines[0].isdigit():
            test_count = int(input_lines[0])
            input_data = '\n'.join(input_lines[1:])
        else:
            # Single test case
            test_count = 1
            input_data = test_group["input"]
        
        # For now, treat the entire sample as one test case
        # You may need to adjust this logic based on your specific format
        test_cases.append({
            "input_text": test_group["input"],
            "expected_output_text": test_group["output"],
        })
    
    return test_cases

def format_problem_statement(problem_data: Dict[str, Any]) -> str:
    """Format the problem data into a markdown statement."""
    statement = f"# {problem_data.get('title', 'Problem')}\n\n"
    
    # Add statement
    statement += "## Problem Statement\n\n"
    statement += problem_data.get('statement', '') + "\n\n"
    
    # Add input specification
    if 'input_specification' in problem_data:
        statement += "## Input\n\n"
        statement += problem_data['input_specification'] + "\n\n"
    
    # Add output specification
    if 'output_specification' in problem_data:
        statement += "## Output\n\n" 
        statement += problem_data['output_specification'] + "\n\n"
    
    # Add constraints/notes
    if 'note' in problem_data and problem_data['note']:
        statement += "## Note\n\n"
        statement += problem_data['note'] + "\n\n"
    
    # Add tags and rating
    if 'tags' in problem_data:
        statement += f"**Tags:** {', '.join(problem_data['tags'])}\n\n"
    
    if 'rating' in problem_data:
        statement += f"**Rating:** {problem_data['rating']}\n\n"
    
    return statement

def load_problem_from_json(problem_data: Dict[str, Any], contest_id: int, letter: str) -> str:
    """Load a problem from scraped JSON format into the database."""
    
    # Generate problem ID
    problem_id = f"{contest_id}_{letter}"
    
    # Format statement
    statement_md = format_problem_statement(problem_data)
    
    # Handle tags - convert list to JSON string
    tags_json = None
    if 'tags' in problem_data and problem_data['tags']:
        tags_json = json.dumps(problem_data['tags'])
    
    # Create problem
    problem = Problem(
        id=problem_id,
        contest_id=contest_id,
        letter=letter,
        title=problem_data.get('title', f"Problem {letter}"),
        statement_md=statement_md,
        rating=problem_data.get('rating'),
        tags=tags_json
    )
    
    # Parse sample test cases
    test_cases_data = parse_sample_tests(problem_data.get('sample_tests', []))
    test_cases = []
    
    for idx, test_data in enumerate(test_cases_data):
        test_case = TestCase(
            id=f"{problem_id}_sample_{idx+1}",
            problem_id=problem_id,
            kind=TestKind.SAMPLE,
            idx=idx + 1,
            input_text=test_data["input_text"],
            expected_output_text=test_data["expected_output_text"]
        )
        test_cases.append(test_case)
    
    # Save to database
    with get_session() as session:
        # Check if problem already exists
        existing = session.get(Problem, problem_id)
        if existing:
            print(f"Problem {problem_id} already exists, updating...")
            existing.title = problem.title
            existing.statement_md = problem.statement_md
            session.add(existing)
        else:
            session.add(problem)
        
        # Remove existing test cases and add new ones
        from sqlmodel import select
        existing_tests = session.exec(select(TestCase).where(TestCase.problem_id == problem_id)).all()
        for test in existing_tests:
            session.delete(test)
        
        for test_case in test_cases:
            session.add(test_case)
        
        session.commit()
        print(f"Loaded problem {problem_id} with {len(test_cases)} test cases")
    
    return problem_id

def add_contest_mapping(contest_id: int, letter: str, cf_contest_id: int, cf_problem_index: str):
    """Add a mapping from contest problem to Codeforces contest."""
    mapping = ContestMap(
        id=f"{contest_id}_{letter}_cf",
        contest_id=contest_id,
        letter=letter,
        cf_contest_id=cf_contest_id,
        cf_problem_index=cf_problem_index
    )
    
    with get_session() as session:
        existing = session.get(ContestMap, mapping.id)
        if existing:
            existing.cf_contest_id = cf_contest_id
            existing.cf_problem_index = cf_problem_index
            session.add(existing)
        else:
            session.add(mapping)
        session.commit()
        print(f"Added contest mapping: {contest_id}{letter} -> CF {cf_contest_id}{cf_problem_index}")

def load_problems_from_file(filepath: str):
    """Load a single problem from a JSON file, parsing contest_id and letter from filename."""
    contest_id, letter = parse_filename(filepath)
    
    with open(filepath, 'r') as f:
        problem_data = json.load(f)
    
    return load_problem_from_json(problem_data, contest_id, letter)

def load_all_problems_from_directory(directory: str = "problems"):
    """Load all problems from JSON files in a directory."""
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist!")
        return []
    
    loaded_problems = []
    json_files = [f for f in os.listdir(directory) if f.endswith('.json')]
    
    print(f"Found {len(json_files)} problem files in {directory}/")
    
    for filename in sorted(json_files):
        filepath = os.path.join(directory, filename)
        try:
            problem_id = load_problems_from_file(filepath)
            loaded_problems.append(problem_id)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
    
    print(f"\nSuccessfully loaded {len(loaded_problems)} problems!")
    return loaded_problems

if __name__ == "__main__":
    import argparse
    from core.db import init_db
    
    parser = argparse.ArgumentParser(description="Load problems into database")
    parser.add_argument("file", help="JSON file containing problem data (contest_id-letter.json format)")
    
    args = parser.parse_args()
    
    init_db()
    
    problem_id = load_problems_from_file(args.file)
    print(f"Successfully loaded problem: {problem_id}")
