import os
import json
from datetime import datetime
from typing import Optional

def ensure_solution_directory(problem_id: str) -> str:
    """Ensure the solution directory exists for a problem."""
    base_dir = "solutions"
    problem_dir = os.path.join(base_dir, problem_id)
    
    # Create directories if they don't exist
    os.makedirs(problem_dir, exist_ok=True)
    
    return problem_dir

def get_next_iteration_number(problem_id: str) -> int:
    """Get the next iteration number for a problem."""
    problem_dir = ensure_solution_directory(problem_id)
    
    # Find existing solution files
    existing_files = [f for f in os.listdir(problem_dir) if f.endswith('.cpp')]
    
    if not existing_files:
        return 1
    
    # Extract iteration numbers from existing files
    iterations = []
    for filename in existing_files:
        try:
            # Files are named like "solution_1.cpp", "solution_2.cpp"
            if filename.startswith('solution_') and filename.endswith('.cpp'):
                num_str = filename.replace('solution_', '').replace('.cpp', '')
                iterations.append(int(num_str))
        except ValueError:
            continue
    
    return max(iterations) + 1 if iterations else 1

def create_solution_header(
    model: str,
    iteration: int,
    timestamp: datetime,
    problem_id: str,
    verdict: Optional[str] = None,
    analysis: Optional[str] = None
) -> str:
    """Create the header comment for a solution file."""
    
    header = f"""/*
 * Problem: {problem_id}
 * Generated: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}
 * Model: {model}
 * Iteration: {iteration}
"""
    
    if verdict:
        header += f" * Previous Verdict: {verdict}\n"
    
    if analysis:
        header += f" * Analysis:\n"
        for line in analysis.split('\n'):
            if line.strip():
                header += f" *   {line.strip()}\n"
    
    header += " */\n\n"
    
    return header

def save_solution(
    problem_id: str,
    code: str,
    model: str,
    iteration: int,
    verdict: Optional[str] = None,
    analysis: Optional[str] = None,
    timestamp: Optional[datetime] = None
) -> str:
    """Save a solution to the solutions directory with metadata."""
    
    if timestamp is None:
        timestamp = datetime.now()
    
    # Ensure directory exists
    problem_dir = ensure_solution_directory(problem_id)
    
    # Create header
    header = create_solution_header(model, iteration, timestamp, problem_id, verdict, analysis)
    
    # Combine header and code
    full_solution = header + code
    
    # Create filename
    filename = f"solution_{iteration}.cpp"
    filepath = os.path.join(problem_dir, filename)
    
    # Save solution
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(full_solution)
    
    # Also save metadata as JSON
    metadata = {
        "problem_id": problem_id,
        "timestamp": timestamp.isoformat(),
        "model": model,
        "iteration": iteration,
        "verdict": verdict,
        "analysis": analysis,
        "filename": filename,
        "code_length": len(code)
    }
    
    metadata_file = os.path.join(problem_dir, f"solution_{iteration}_meta.json")
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✅ Solution saved: {filepath}")
    
    return filepath

def get_solution_summary(problem_id: str) -> dict:
    """Get a summary of all solutions for a problem."""
    problem_dir = ensure_solution_directory(problem_id)
    
    if not os.path.exists(problem_dir):
        return {"problem_id": problem_id, "total_attempts": 0, "solutions": []}
    
    solutions = []
    for filename in os.listdir(problem_dir):
        if filename.endswith('_meta.json'):
            try:
                with open(os.path.join(problem_dir, filename), 'r') as f:
                    metadata = json.load(f)
                    solutions.append(metadata)
            except Exception as e:
                print(f"Warning: Could not read metadata file {filename}: {e}")
    
    # Sort by iteration number
    solutions.sort(key=lambda x: x.get('iteration', 0))
    
    return {
        "problem_id": problem_id,
        "total_attempts": len(solutions),
        "solutions": solutions
    }

def list_all_solved_problems() -> list:
    """List all problems that have been attempted."""
    solutions_dir = "solutions"
    
    if not os.path.exists(solutions_dir):
        return []
    
    problems = []
    for item in os.listdir(solutions_dir):
        item_path = os.path.join(solutions_dir, item)
        if os.path.isdir(item_path):
            summary = get_solution_summary(item)
            if summary["total_attempts"] > 0:
                problems.append(summary)
    
    # Sort by problem ID
    problems.sort(key=lambda x: x["problem_id"])
    
    return problems
