# 🚀 Simple Setup Guide

## 📋 What You Need
- Python 3.8+
- OpenAI API key
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

### 2. Configure
Create `.env` file:
```
OPENAI_API_KEY=sk-your-key-here
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
```bash
python apps/cli/auto_solve.py 2045_A --max-attempts 3 --profile Default
```

## 🎉 What Happens

1. **GPT generates solution** from problem statement
2. **Submits to Codeforces** via your browser
3. **Waits for verdict** automatically  
4. **If failed**: Uses error details to improve solution
5. **Repeats up to 3 times** until accepted

## 📁 Results Saved To
```
problems_solved/2045_A/
├── solutions/           # All attempts
├── api_responses/       # Verdict details  
├── problem_info.json   # Problem data
└── final_result.json   # Success/failure
```

## 🐛 Troubleshooting

**Browser connection failed?**
- Make sure browser is running with `--remote-debugging-port=9222`
- Check you're logged into Codeforces

**OpenAI API error?**  
- Verify your API key in `.env` file

**No contest mapping?**
- Add mapping with `add_mapping.py` command

That's it! 🚀
