# Hybrid LLM ICPC Solver

A competitive programming solution system that uses multiple LLMs in a feedback loop to solve ICPC problems automatically.

## Architecture

- **GPT**: Generates initial C++ solutions from problem statements
- **DeepSeek**: Analyzes failed submissions and provides diagnostic hints  
- **Codeforces**: Automated submission and verdict polling via Playwright
- **SQLite**: Tracks problems, sessions, attempts, and results

## Setup

1. **Install Dependencies**
   ```bash
   pip3 install -e .
   playwright install chromium
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Setup Codeforces Authentication**
   ```bash
   python scripts/setup_codeforces.py
   # Follow the interactive setup for credentials and CAPTCHA solving
   ```

4. **Initialize Database and Load Sample Data**
   ```bash
   python scripts/setup_sample_data.py
   ```

## Usage

### CLI
```bash
python apps/cli/run_session.py --contest-id 2072 --letter F --attempts 3
```

### API
```bash
uvicorn apps.api.main:app --reload
curl -X POST "http://localhost:8000/solve/2072/F?max_attempts=3"
```

### Loading Problems
```bash
# Load all problems from problems/ directory
python scripts/load_all_problems.py

# Load a single problem (contest_id-letter.json format)
python core/data_loader.py problems/2072-F.json

# Add Codeforces contest mapping for submissions
python apps/cli/add_mapping.py --our-contest 2072 --our-letter F --cf-contest 102951 --cf-letter A
```

## Project Structure

```
├── apps/
│   ├── api/main.py          # FastAPI wrapper
│   └── cli/run_session.py   # CLI entrypoint
├── core/
│   ├── config.py           # Environment configuration
│   ├── db.py               # Database setup
│   ├── models.py           # SQLModel data models
│   ├── orchestrator.py     # Main solving logic
│   ├── llm_gateway.py      # LLM API integration
│   ├── judge_cf.py         # Codeforces automation
│   ├── runner_local.py     # Optional local testing
│   └── prompts/            # LLM prompt templates
├── infra/playwright/       # Browser session storage
├── problems/               # Problem datasets
└── scripts/                # Utility scripts
```

## Workflow

1. Load problem statement and test cases
2. Generate C++ solution using GPT
3. Submit to Codeforces and poll for verdict
4. If failed, analyze with DeepSeek for insights  
5. Repeat up to max_attempts until AC or exhausted
6. Track all attempts and results in database

## Codeforces Integration Features

### 🛡️ **Cloudflare Bypass**
- Uses [cloudscraper](https://github.com/VeNoMouS/cloudscraper) to bypass Cloudflare protection
- Automatic handling of anti-bot challenges
- Enhanced browser fingerprinting and stealth mode

### 🤖 **CAPTCHA Solving**
- Support for 2captcha.com and Anti-Captcha services
- Automatic CAPTCHA detection and solving during login/submission
- Graceful fallback when CAPTCHA services are unavailable

### 🔐 **Robust Authentication**
- Secure credential storage in `.env` file
- Automatic CSRF token extraction and handling
- Session persistence across multiple submissions

### ⚡ **Smart Submission System**
- Rate limiting to respect Codeforces submission intervals
- Automatic language detection and selection
- Comprehensive error handling and retry logic

### 📊 **Advanced Verdict Parsing**
- Detailed verdict extraction (AC, WA, TLE, MLE, etc.)
- Test case number identification for failures
- Runtime and memory usage tracking
- Complete submission history in database

## Data Models

- **Problem**: Contest problem metadata and statement (contest_id, letter, rating, tags)
- **TestCase**: Sample and hidden test cases
- **SolveSession**: Solving attempt session
- **Attempt**: Individual solution attempt
- **CFSubmission**: Codeforces submission details
- **ContestMap**: Maps contest problems to CF contests for submission

## Problem Data Format

Problems should be stored in JSON files named `{CONTEST_ID}-{LETTER}.json` (e.g., `2072-F.json`, `2070-D.json`).

The JSON structure should be:

```json
{
    "statement": "Problem description text...",
    "input_specification": "Input format description...",
    "output_specification": "Output format description...",
    "sample_tests": [
        {
            "input": "Sample input text",
            "output": "Expected output text"
        }
    ],
    "note": "Additional notes (optional)",
    "tags": ["tag1", "tag2"],
    "rating": "1700"
}
```

The system automatically parses the contest ID and problem letter from the filename:
- `2072-F.json` → contest_id=2072, letter="F"
- `2070-D.json` → contest_id=2070, letter="D"

See the files in `problems/` directory for real examples.
