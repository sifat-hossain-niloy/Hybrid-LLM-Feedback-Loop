# Hybrid LLM Feedback Loop - Commands

## Quick Start (Run these now!)

```bash
# 1. Activate environment
source venv/bin/activate.fish

# 2. Generate solution (demo mode)  
python3 apps/cli/demo_solve.py --contest-id 2045 --letter A --attempts 1

# 3. Submit solution manually (most reliable)
python3 apps/cli/submit_simple.py solutions/2045_A/solution_4.cpp
```

## Full System Commands

### Setup (One-time)
```bash
source venv/bin/activate.fish
python3 scripts/setup_sample_data.py
python3 scripts/load_all_problems.py
python3 apps/cli/add_mapping.py --our-contest 2045 --our-letter A --cf-contest 2045 --cf-letter A
```

### Solving Problems
```bash
# Demo mode (no actual submission)
python3 apps/cli/demo_solve.py --contest-id 2045 --letter A --attempts 2

# Full system with feedback loop  
python3 apps/cli/run_session.py --contest-id 2045 --letter A --attempts 3
```

### Submission Methods

#### Method 1: Simple (Best)
```bash
python3 apps/cli/submit_simple.py solutions/2045_A/solution_1.cpp
```

#### Method 2: Chromium Profile ⭐ **NEW: Auto Verdict!**
```bash
# Start Chromium with debugging
/Applications/Chromium.app/Contents/MacOS/Chromium --profile-directory=Sifat --remote-debugging-port=9222 --disable-web-security --no-first-run &

# Wait 5 seconds, then submit (now with automatic verdict polling!)
python3 apps/cli/submit_existing_chromium.py solutions/2045_A/solution_1.cpp --profile Sifat
```

#### Method 3: Automated Playwright ⭐ **NEW: Auto Verdict!**
```bash
python3 apps/cli/submit_playwright.py solutions/2045_A/solution_1.cpp
```

### Utilities
```bash
# View solutions
python3 apps/cli/view_solutions.py

# View API responses ⭐ NEW!
python3 apps/cli/view_api_responses.py --list
python3 apps/cli/view_api_responses.py --submission-id 339630338

# Start API server
uvicorn apps.api.main:app --host 127.0.0.1 --port 8000

# List problems
ls problems/

# List solutions  
ls -la solutions/

# Check saved API responses ⭐ NEW!
ls -la api_responses/
```

## Available Problems
```bash
ls problems/  # Shows: 2045-A.json, 2051-E.json, 2072-F.json, etc.
```

## 🆕 **Automatic Verdict Polling Features**

### What's New
- **Automatic Submission ID Detection**: Uses XPath `//*[@id="pageContent"]/div[4]/div[6]/table/tbody/tr[2]/td[1]/a`
- **Real-time Verdict Monitoring**: Polls `//*[@id="pageContent"]/div[4]/div[6]/table/tbody/tr[2]/td[6]/a/span` until not "Running..."
- **Detailed Results via API**: Calls `https://codeforces.com/data/submitSource` for full submission details
- **Smart Status Detection**: Automatically detects AC, WA, TLE, MLE, RE, CE
- **Timeout Handling**: 5-minute maximum wait with graceful fallback

### How It Works
1. 📤 **Submit** solution to Codeforces
2. 🎯 **Extract** submission ID from status page
3. ⏳ **Poll** verdict every 5 seconds until final
4. 📊 **Fetch** detailed results via API
5. 💾 **Save** full API response to JSON file
6. 🎉 **Report** final verdict and test results

## 🆕 **Enhanced API Response Interception**

### 🔍 **Multiple Collection Methods**
1. **Network Interception** - Captures live API calls with dynamic rv parameters
2. **Click Extraction** - Clicks submission ID to extract popup data
3. **Manual API Calls** - Fallback with extracted CSRF tokens

### 📊 **Complete Data Capture**
- **Dynamic Parameters**: Real rv values that change per submission
- **Full API Response**: Complete JSON in your exact format
- **Individual Test Results**: verdict#1, output#1, input#1, answer#1
- **Performance Data**: timeConsumed#1, memoryConsumed#1
- **Source Code**: Your submitted solution
- **Problem Context**: problemName, contestName
- **Checker Details**: checkerStdoutAndStderr#1 for failed tests

### 📁 **Enhanced File Format**
```json
{
  "submission_id": "339631265",
  "timestamp": "2025-09-21T03:41:41",
  "collection_methods": ["api_interception", "click_extraction"],
  "api_response": {
    "url": "https://codeforces.com/data/submitSource?rv=abc123def",
    "rv_parameter": "abc123def",
    "response_text": "{\"testCount\":\"1\",\"verdict#1\":\"WRONG_ANSWER\",...}",
    "status": 200
  },
  "parsed_api_response": {
    "testCount": "1",
    "verdict#1": "WRONG_ANSWER",
    "output#1": "21\\r\\n",
    "answer#1": "9\\r\\n",
    "checkerStdoutAndStderr#1": "wrong answer 1st words differ...",
    "timeConsumed#1": "46",
    "memoryConsumed#1": "8192",
    "source": "#include<bits/stdc++.h>\\r\\n...",
    "problemName": "(A) Scrambled Scrabble"
  }
}
```

## 🤖 **Automated Problem Solving with Feedback Loop**

### 🚀 **Main Command**
```bash
# Solve a problem automatically with up to 3 attempts
source venv/bin/activate.fish && python3 apps/cli/auto_solve.py 2045_A

# Custom settings
source venv/bin/activate.fish && python3 apps/cli/auto_solve.py 2045_A --max-attempts 5 --profile Sifat
```

### 📊 **View Results**
```bash
# List all solved problems
source venv/bin/activate.fish && python3 apps/cli/view_results.py --list

# View detailed results for specific problem
source venv/bin/activate.fish && python3 apps/cli/view_results.py --problem 2045_A
```

### 🏗️ **Folder Structure Created**
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
```

### 🔄 **Automated Process**
1. **Load Problem** from database using contest_id_letter format
2. **Generate Solution** using GPT-4 with problem context
3. **Submit to Codeforces** using existing Chromium automation
4. **Analyze Result** and extract detailed test failure information
5. **If Failed**: Use failure details to generate improved solution
6. **Repeat** up to max attempts until accepted
7. **Save Everything** with complete audit trail

### 📋 **Solution File Format**
Each solution includes a header with metadata:
```cpp
/*
 * Problem: 2045_A - Scrambled Scrabble
 * Generated: 2025-09-21 03:41:23
 * Model: GPT-4
 * Iteration: 1
 * Rating: 1700
 */

#include<bits/stdc++.h>
using namespace std;
// ... solution code
```