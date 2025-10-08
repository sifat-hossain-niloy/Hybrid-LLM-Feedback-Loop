# Problems Solved Directory Structure

This directory contains automatically solved competitive programming problems using the hybrid LLM feedback loop system.

## Folder Structure

```
problems_solved/
├── 2045_A/                          # Problem ID
│   ├── solutions/                   # All solution attempts
│   │   ├── 2045_A_Solution_1.cpp   # First attempt
│   │   ├── 2045_A_Solution_2.cpp   # Second attempt (if needed)
│   │   └── 2045_A_Solution_3.cpp   # Third attempt (if needed)
│   ├── api_responses/               # Codeforces submission results
│   │   ├── submission_339631265_20250921_035531.json
│   │   ├── submission_339631266_20250921_040112.json
│   │   └── submission_339631267_20250921_040645.json
│   ├── problem_info.json            # Problem statement and metadata
│   ├── solving_log.json             # Complete solving process log
│   └── final_result.json            # Final acceptance status and summary
├── 2072_F/                          # Another problem
│   ├── solutions/
│   ├── api_responses/
│   ├── problem_info.json
│   └── ...
```

## File Naming Conventions

- **Solutions**: `{PROBLEM_ID}_Solution_{N}.cpp`
- **API Responses**: `submission_{SUBMISSION_ID}_{TIMESTAMP}.json`
- **Problem Info**: `problem_info.json` (contains statement, samples, constraints)
- **Solving Log**: `solving_log.json` (iteration details, GPT responses, verdicts)
- **Final Result**: `final_result.json` (acceptance status, best solution, statistics)

## Automated Process

1. **Parse Problem ID** → Load from database
2. **Generate Solution** → Ask GPT with problem context
3. **Submit to Codeforces** → Use existing submission system
4. **Analyze Result** → Extract verdict and failed tests
5. **Iterate if Failed** → Use failure info to improve solution
6. **Repeat** → Up to 3 attempts until accepted
7. **Save Everything** → Complete audit trail of solving process
