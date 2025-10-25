# 🤖 Hybrid LLM ICPC Solver - Simplified

An automated competitive programming solution system that uses GPT in a feedback loop to solve ICPC problems.

## 🎯 Core Workflow

1. **Generate Solution**: GPT creates C++ solution from problem statement
2. **Submit to Codeforces**: Automated submission via Chromium browser
3. **Get Verdict**: Wait for and capture detailed verdict + test results  
4. **Analyze & Improve**: If failed, use verdict details to generate better solution
5. **Repeat**: Loop up to 3 times until accepted

## 🚀 Quick Start

### 1. Setup
```bash
# Create virtual environment
python -m venv venv

# Windows
venv\Scripts\Activate.ps1
# macOS/Linux  
source venv/bin/activate

# Install dependencies
pip install -e .
```

### 2. Configure
```bash
# Create .env file
OPENAI_API_KEY=your_openai_api_key_here
CF_USERNAME=your_codeforces_username
CF_PASSWORD=your_codeforces_password
```

### 3. Initialize Database
```bash
python scripts/setup_sample_data.py
python scripts/load_all_problems.py
```

### 4. Add Contest Mapping
```bash
python apps/cli/add_mapping.py --our-contest 2045 --our-letter A --cf-contest 2045 --cf-letter A
```

### 5. Run Automated Solver
```bash
# Start Chromium with your profile (replace "YourProfile" with your actual profile name)
# Windows:
"C:\Program Files\Google\Chrome\Application\chrome.exe" --profile-directory="YourProfile" --remote-debugging-port=9222 &

# macOS:
/Applications/Chromium.app/Contents/MacOS/Chromium --profile-directory="YourProfile" --remote-debugging-port=9222 &

# Run solver (up to 3 attempts)
python apps/cli/auto_solve.py 2045_A --max-attempts 3 --profile YourProfile
```

## 📁 Project Structure

```
├── apps/cli/
│   ├── auto_solve.py              # 🎯 Main automated solver
│   ├── submit_existing_chromium.py # 🌐 Chromium submission
│   └── add_mapping.py             # 🗺️ Contest mappings
├── core/
│   ├── automated_solver.py        # 🧠 Core solving logic
│   ├── llm_gateway.py            # 🤖 GPT integration
│   ├── solution_saver.py         # 💾 Solution storage
│   ├── data_loader.py            # 📊 Problem loading
│   ├── models.py                 # 🗃️ Database models
│   └── prompts/                  # 📝 GPT prompts
├── problems/                     # 📋 Problem JSON files
├── problems_solved/              # 🏆 Automated results
└── scripts/                      # 🔧 Setup utilities
```

## 🎯 Available Commands

### Core Command
```bash
# Automated solving with feedback loop
python apps/cli/auto_solve.py PROBLEM_ID --max-attempts 3 --profile YourProfile
```

### Setup Commands  
```bash
# Load problems
python scripts/load_all_problems.py

# Add contest mapping
python apps/cli/add_mapping.py --our-contest 2045 --our-letter A --cf-contest 2045 --cf-letter A

# Setup database
python scripts/setup_sample_data.py
```

## 🔧 Requirements

- **Python 3.8+**
- **OpenAI API Key** (for GPT-4)
- **Codeforces Account** (for submissions)
- **Chrome/Chromium Browser** (for automated submission)

## 🏗️ Output Structure

Each solved problem creates:
```
problems_solved/PROBLEM_ID/
├── solutions/                    # All solution attempts
│   ├── PROBLEM_ID_Solution_1.cpp
│   ├── PROBLEM_ID_Solution_2.cpp
│   └── PROBLEM_ID_Solution_3.cpp
├── api_responses/               # Codeforces verdict details
├── problem_info.json           # Problem statement
├── solving_log.json            # Complete process log
└── final_result.json           # Final status
```

## 🎉 Success Flow

```
🤖 Generate Solution → 🌐 Submit to CF → ⏳ Wait for Verdict → 
✅ ACCEPTED! OR ❌ Failed → 🧠 Analyze Error → 🔄 Improve & Retry
```

That's it! Simple, focused, and effective. 🚀