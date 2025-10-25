# 🤖 Hybrid LLM ICPC Solver - Simplified

An automated competitive programming solution system that uses GPT in a feedback loop to solve ICPC problems.

## 🎯 Core Workflow

1. **Generate Solution**: GPT-4 creates C++ solution from problem statement
2. **Submit to Codeforces**: Automated submission via Chromium browser
3. **Get Verdict**: Wait for and capture detailed verdict + test results  
4. **Generate Hint**: If failed, use Mistral/Groq to analyze errors and provide debugging hints
5. **Improve Solution**: GPT-4 uses hints to generate better solution
6. **Repeat**: Loop up to 3 times until accepted

## 🧠 Available Workflows

### **GPT + Mistral** (Default)
- **Solution Generation**: GPT-4 (OpenAI)
- **Debugging Hints**: Codestral-2508 (Mistral AI)
- **Best for**: Code-focused debugging and algorithmic improvements

### **GPT + Groq** 
- **Solution Generation**: GPT-4 (OpenAI)  
- **Debugging Hints**: Llama 3.3 70B (Groq)
- **Best for**: Fast inference and detailed error analysis

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
MISTRAL_API_KEY=your_mistral_api_key_here  # For GPT+Mistral workflow
GROQ_API_KEY=your_groq_api_key_here        # For GPT+Groq workflow
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

# Run solver (up to 3 attempts) - Default GPT+Mistral workflow
python apps/cli/auto_solve.py 2045_A --max-attempts 3 --profile YourProfile

# Or use GPT+Groq workflow
python apps/cli/auto_solve.py 2045_A --workflow gpt_groq --max-attempts 3 --profile YourProfile
```

## 📁 Project Structure

```
├── apps/cli/
│   ├── auto_solve.py              # 🎯 Main automated solver
│   ├── submit_existing_chromium.py # 🌐 Chromium submission
│   └── add_mapping.py             # 🗺️ Contest mappings
├── core/
│   ├── automated_solver.py        # 🧠 Core solving logic
│   ├── workflow_manager.py        # 🔄 Multi-LLM workflow orchestration
│   ├── llm_providers/             # 🤖 LLM provider integrations
│   │   ├── openai_provider.py     #   - GPT-4 (OpenAI)
│   │   ├── mistral_provider.py    #   - Codestral (Mistral AI)
│   │   └── groq_provider.py       #   - Llama 3.3 70B (Groq)
│   ├── solution_saver.py         # 💾 Solution storage
│   ├── data_loader.py            # 📊 Problem loading
│   └── models.py                 # 🗃️ Database models
├── problems/                     # 📋 Problem JSON files
├── problems_solved/              # 🏆 Automated results
└── scripts/                      # 🔧 Setup utilities
```

## 🎯 Available Commands

### Core Commands
```bash
# GPT + Mistral workflow (default)
python apps/cli/auto_solve.py PROBLEM_ID --max-attempts 3 --profile YourProfile

# GPT + Groq workflow  
python apps/cli/auto_solve.py PROBLEM_ID --workflow gpt_groq --max-attempts 3 --profile YourProfile
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
- **OpenAI API Key** (for GPT-4 solution generation)
- **Mistral API Key** OR **Groq API Key** (for debugging hints)
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
🤖 GPT-4 Generate Solution → 🌐 Submit to CF → ⏳ Wait for Verdict → 
✅ ACCEPTED! OR ❌ Failed → 💡 Mistral/Groq Generate Hint → 🔄 GPT-4 Improve & Retry
```

## 🧠 Context Persistence

Each workflow maintains **persistent chat contexts** throughout the solving session:

- **Solution Context**: GPT-4 remembers all previous attempts and improvements
- **Hint Context**: Mistral/Groq builds understanding of recurring issues
- **Session Isolation**: Each problem gets its own isolated conversation threads

This ensures that:
- Solutions improve iteratively based on accumulated knowledge
- Hints become more targeted as the session progresses  
- No context bleeding between different problems

That's it! Simple, focused, and effective. 🚀