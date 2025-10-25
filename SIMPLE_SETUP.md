# 🚀 Simple Setup Guide - Multi-LLM Workflows

## 📋 What You Need
- Python 3.8+
- OpenAI API key (for GPT-4 solution generation)
- Mistral API key OR Groq API key (for debugging hints)
- Codeforces account
- Chrome/Chromium browser

## ⚡ Quick Setup

### 1. Install
```bash
# Clone and enter directory
git clone <repo-url>
cd "Hybrid LLM Feedback Loop"

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\Activate.ps1
# Activate (macOS/Linux)
source venv/bin/activate

# Install
pip install -e .
```

### 2. Configure API Keys
Create `.env` file:
```
# Required for solution generation
OPENAI_API_KEY=sk-your-openai-key-here

# Choose ONE for debugging hints:
MISTRAL_API_KEY=your-mistral-key-here     # For GPT+Mistral workflow
GROQ_API_KEY=your-groq-key-here           # For GPT+Groq workflow

# Required for submissions
CF_USERNAME=your_codeforces_username  
CF_PASSWORD=your_codeforces_password
```

### 3. Setup Database
```bash
python scripts/setup_sample_data.py
python scripts/load_all_problems.py
```

### 4. Add Problem Mapping
```bash
python apps/cli/add_mapping.py --our-contest 2045 --our-letter A --cf-contest 2045 --cf-letter A
```

## 🎯 Run the Solver

### Step 1: Start Browser
```bash
# Windows (Chrome)
"C:\Program Files\Google\Chrome\Application\chrome.exe" --profile-directory="Default" --remote-debugging-port=9222 &

# macOS (Chromium)  
/Applications/Chromium.app/Contents/MacOS/Chromium --profile-directory="Default" --remote-debugging-port=9222 &

# Linux (Chromium)
chromium-browser --profile-directory="Default" --remote-debugging-port=9222 &
```

### Step 2: Login to Codeforces
- Open browser and login to Codeforces manually
- Keep browser open

### Step 3: Run Automated Solver

#### **GPT + Mistral Workflow** (Default)
```bash
python apps/cli/auto_solve.py 2045_A --max-attempts 3 --profile Default
```

#### **GPT + Groq Workflow** (Fast inference)
```bash
python apps/cli/auto_solve.py 2045_A --workflow gpt_groq --max-attempts 3 --profile Default
```

## 🧠 How Each Workflow Works

### **GPT + Mistral**
1. **GPT-4** generates initial C++ solution
2. **Submits** to Codeforces automatically
3. If failed: **Codestral** analyzes errors and provides coding-focused hints
4. **GPT-4** uses hints to improve solution
5. **Repeats** until accepted (max 3 attempts)

### **GPT + Groq**  
1. **GPT-4** generates initial C++ solution
2. **Submits** to Codeforces automatically
3. If failed: **Llama 3.3 70B** provides detailed error analysis
4. **GPT-4** uses analysis to improve solution
5. **Repeats** until accepted (max 3 attempts)

## 📁 Results Saved To
```
problems_solved/2045_A/
├── solutions/           # All attempts with metadata headers
├── api_responses/       # Codeforces verdict details  
├── problem_info.json   # Problem statement and data
├── solving_log.json    # Complete workflow log with hints
└── final_result.json   # Success/failure summary
```

## 🔄 Context Persistence

Each workflow maintains **separate persistent chat contexts**:

- **Solution Context**: GPT-4 remembers all previous attempts and learns from failures
- **Hint Context**: Mistral/Groq builds understanding of the problem and recurring issues
- **Session Isolation**: Each problem gets completely isolated conversation threads

This means:
- ✅ Solutions get progressively better with each attempt
- ✅ Hints become more targeted as failures are analyzed
- ✅ No interference between different problems

## 🐛 Troubleshooting

**Browser connection failed?**
- Make sure browser is running with `--remote-debugging-port=9222`
- Check you're logged into Codeforces

**OpenAI API error?**  
- Verify your API key in `.env` file

**Mistral/Groq API error?**
- Check your API key for the chosen workflow
- Try switching workflows if one provider is down

**No contest mapping?**
- Add mapping with `add_mapping.py` command

## 🚀 Future Extensibility

The architecture supports easy addition of new workflows:
- **GPT + Claude** (when Anthropic API is added)
- **Mistral + Groq** (dual hint providers)
- **Custom model combinations**

Just add new providers to `core/llm_providers/` and register them in `workflow_manager.py`!

That's it! Choose your workflow and start solving! 🎯