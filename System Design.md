# Hybrid LLM ICPC Solver — 

## Stack

* Python 3.11
* SQLite (via SQLModel)
* FastAPI (optional endpoint) or pure CLI
* Playwright (Python) for CF submit/poll
* OpenAI (GPT) + DeepSeek (diagnose)

---

## Repo layout

```
.
├─ apps/
│  ├─ api/               # optional FastAPI wrapper
│  │  └─ main.py
│  └─ cli/
│     └─ run_session.py  # CLI entrypoint
├─ core/
│  ├─ config.py
│  ├─ db.py
│  ├─ models.py
│  ├─ orchestrator.py
│  ├─ llm_gateway.py
│  ├─ judge_cf.py
│  ├─ runner_local.py    # optional; can disable entirely
│  └─ prompts/
│     ├─ gpt_solution.txt
│     └─ deepseek_diagnose.txt
├─ infra/
│  └─ playwright/        # storageState.json (gitignored)
├─ problems/             # your ICPC WF assets
│  └─ 2018/A/...
├─ .env.example
├─ pyproject.toml
└─ README.md
```

---

## Env

```dotenv
# file: .env.example
DATABASE_URL=sqlite:///./icpc.db
OPENAI_API_KEY=sk-...
DEEPSEEK_API_KEY=...
PLAYWRIGHT_STORAGE=infra/playwright/storageState.json
MAX_ATTEMPTS=3
CF_SUBMIT_SPACING_SEC=10      # min secs between submissions (per account)
CF_POLL_TIMEOUT_SEC=900
CF_DEFAULT_LANG_ID=54         # fallback; you can scrape at runtime
```

---

## Dependencies (minimal)

```toml
# file: pyproject.toml
[project]
name = "hybrid-llm-icpc-lite"
version = "0.1.0"
dependencies = [
  "fastapi",
  "uvicorn[standard]",
  "sqlmodel",
  "pydantic",
  "python-dotenv",
  "playwright",
  "httpx",
  "tenacity",
  "orjson",
  "loguru",
]

[tool.playwright]
# Run once:  playwright install chromium
```

---

## DB + models (SQLite via SQLModel)

```python
# file: core/db.py
from sqlmodel import SQLModel, create_engine, Session
from core.config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)
```

```python
# file: core/models.py
from datetime import datetime
from typing import Optional, Literal
from sqlmodel import SQLModel, Field

Verdict = Literal["AC","WA","TLE","MLE","RE","CE","PE","SEC","IL","JUDGE_TIMEOUT","ERROR"]

class Problem(SQLModel, table=True):
    id: str = Field(primary_key=True)
    year: int
    letter: str
    title: str
    statement_md: str

class TestCase(SQLModel, table=True):
    id: str = Field(primary_key=True)
    problem_id: str = Field(foreign_key="problem.id")
    kind: Literal["sample","hidden"] = "hidden"
    idx: int
    input_text: str
    expected_output_text: str

class SolveSession(SQLModel, table=True):
    id: str = Field(primary_key=True)
    problem_id: str = Field(foreign_key="problem.id")
    max_attempts: int = 3
    status: Optional[str]
    started_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None

class Attempt(SQLModel, table=True):
    id: str = Field(primary_key=True)
    session_id: str = Field(foreign_key="solvesession.id")
    attempt_no: int
    model: str
    prompt: str
    code_cpp: str
    verdict: Optional[Verdict]
    finished_at: Optional[datetime]

class CFSubmission(SQLModel, table=True):
    id: str = Field(primary_key=True)
    attempt_id: str = Field(foreign_key="attempt.id")
    contest_id: int
    problem_index: str
    cf_submission_id: Optional[int]
    verdict: Optional[str]
    test_number: Optional[int]
    time_ms: Optional[int]
    memory_kb: Optional[int]
    web_url: Optional[str]
    raw_row_html: Optional[str]

class ContestMap(SQLModel, table=True):
    id: str = Field(primary_key=True)
    wf_year: int
    letter: str
    cf_contest_id: int
    cf_problem_index: str
```

---

## Config

```python
# file: core/config.py
import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL","sqlite:///./icpc.db")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
PLAYWRIGHT_STORAGE = os.getenv("PLAYWRIGHT_STORAGE","infra/playwright/storageState.json")
MAX_ATTEMPTS = int(os.getenv("MAX_ATTEMPTS","3"))
CF_SUBMIT_SPACING_SEC = int(os.getenv("CF_SUBMIT_SPACING_SEC","10"))
CF_POLL_TIMEOUT_SEC = int(os.getenv("CF_POLL_TIMEOUT_SEC","900"))
CF_DEFAULT_LANG_ID = int(os.getenv("CF_DEFAULT_LANG_ID","54"))
```

---

## LLM stubs (fill with your API calls)

```python
# file: core/llm_gateway.py
from typing import Optional

def gpt_generate_solution(problem_md: str, samples: str, hints: Optional[str]) -> str:
    # TODO: call OpenAI; return raw C++ source as str
    return "// TODO: generated C++"

def deepseek_diagnose(problem_md: str, code_cpp: str, cf_verdict: str, local_failures: str) -> str:
    # TODO: call DeepSeek; return bullet-point analysis
    return "- Hypothesis: ..."
```

Prompts (same content as before; keep short, deterministic).
`core/prompts/gpt_solution.txt` and `core/prompts/deepseek_diagnose.txt`.

---

## Codeforces adapter (Playwright; in-process)

```python
# file: core/judge_cf.py
import time, re
from typing import Optional
from playwright.sync_api import sync_playwright
from core.config import PLAYWRIGHT_STORAGE, CF_POLL_TIMEOUT_SEC, CF_DEFAULT_LANG_ID

def submit_source(contest_id: int, problem_index: str, source: str, language_id: Optional[int]=None):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(storage_state=PLAYWRIGHT_STORAGE)
        page = ctx.new_page()
        page.goto(f"https://codeforces.com/gym/{contest_id}/submit")
        page.wait_for_selector("#programTypeId")
        page.select_option("#programTypeId", str(language_id or CF_DEFAULT_LANG_ID))
        page.select_option("#problemIndex", problem_index)
        page.fill('textarea[name="source"]', source)
        with page.expect_navigation():
            page.click('input[type="submit"]')
        page.goto(f"https://codeforces.com/gym/{contest_id}/my")
        row = page.locator("#pageContent table.status-frame-datatable tbody tr").first
        href = row.locator('a[href*="/submission/"]').first.get_attribute("href")
        sub_id = int(href.split("/")[-1])
        browser.close()
        return sub_id, f"https://codeforces.com{href}"

def poll_submission(contest_id: int, submission_id: int, timeout_sec: int = CF_POLL_TIMEOUT_SEC):
    start = time.time()
    last_html = None
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(storage_state=PLAYWRIGHT_STORAGE)
        page = ctx.new_page()
        while True:
            page.goto(f"https://codeforces.com/gym/{contest_id}/submission/{submission_id}")
            table = page.locator("table").first
            html = table.inner_html()
            last_html = html
            verdict_m = re.search(
                r"(In queue|Compiling|Running|Accepted|Wrong answer|Time limit|Memory limit|Runtime error|Compilation error|Idleness limit|Presentation error|Security violated)",
                html, re.I)
            test_m = re.search(r"on test\s+(\d+)", html, re.I)
            time_m = re.search(r"(\d+)\s*ms", html)
            mem_m = re.search(r"(\d+)\s*KB", html)

            verdict = verdict_m.group(0) if verdict_m else "In queue"
            done = bool(re.search(r"(Accepted|Wrong answer|Time limit|Memory limit|Runtime error|Compilation error|Idleness|Presentation|Security)", verdict, re.I))
            if done:
                browser.close()
                return {
                    "verdict": verdict,
                    "test_number": int(test_m.group(1)) if test_m else None,
                    "time_ms": int(time_m.group(1)) if time_m else None,
                    "memory_kb": int(mem_m.group(1)) if mem_m else None,
                    "raw_row_html": html
                }
            if time.time() - start > timeout_sec:
                browser.close()
                return {"verdict":"JUDGE_TIMEOUT","raw_row_html": last_html}
            time.sleep(3)
```

> One-time login to create storage state:
> `playwright codegen https://codeforces.com/enter` → log in → save storage → copy JSON to `infra/playwright/storageState.json`.

---

## Optional local reproduction (no Docker)

```python
# file: core/runner_local.py
import subprocess, tempfile, os, time

def compile_cpp(source: str):
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "main.cpp")
        out = os.path.join(d, "a.out")
        open(src, "w").write(source)
        p = subprocess.run(
            ["g++","-std=gnu++17","-O2","-pipe",src,"-o",out],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        ok = (p.returncode == 0)
        return ok, p.stderr, (out if ok else None)

def run_case(binary: str, input_text: str, time_limit_ms: int=2000):
    start = time.time()
    p = subprocess.run([binary], input=input_text, text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       timeout=time_limit_ms/1000)
    dt = int((time.time()-start)*1000)
    return {"rc": p.returncode, "stdout": p.stdout, "stderr": p.stderr, "runtime_ms": dt}
```

> Safety note: this is **not sandboxed**. If you prefer, **skip local runs** and rely solely on CF verdicts.

---

## Orchestrator (single-process loop)

```python
# file: core/orchestrator.py
import uuid
from datetime import datetime
from core.db import get_session
from core.models import *
from core.llm_gateway import gpt_generate_solution, deepseek_diagnose
from core.judge_cf import submit_source, poll_submission
from core.config import MAX_ATTEMPTS, CF_SUBMIT_SPACING_SEC

_last_submit_ts = 0.0

def _normalize_verdict(cf_v: str) -> str:
    v = cf_v.lower()
    if "accepted" in v: return "AC"
    if "wrong answer" in v: return "WA"
    if "time limit" in v: return "TLE"
    if "memory limit" in v: return "MLE"
    if "runtime error" in v: return "RE"
    if "compilation error" in v: return "CE"
    if "idleness" in v: return "IL"
    if "presentation" in v: return "PE"
    if "security" in v: return "SEC"
    if "judge_timeout" in v: return "JUDGE_TIMEOUT"
    return "ERROR"

def _rate_limit_submit():
    import time
    global _last_submit_ts
    delta = time.time() - _last_submit_ts
    if delta < CF_SUBMIT_SPACING_SEC:
        time.sleep(CF_SUBMIT_SPACING_SEC - delta)
    _last_submit_ts = time.time()

def start_session(year: int, letter: str, max_attempts: int = MAX_ATTEMPTS) -> str:
    sid = str(uuid.uuid4())
    with get_session() as s:
        prob = s.exec(
            Problem.select().where(Problem.year == year, Problem.letter == letter)
        ).first()
        if not prob:
            raise RuntimeError("Problem not found; seed it first.")
        sess = SolveSession(id=sid, problem_id=prob.id, max_attempts=max_attempts, status="running")
        s.add(sess); s.commit()
    run_session(sid)
    return sid

def run_session(session_id: str):
    with get_session() as s:
        sess = s.get(SolveSession, session_id)
        prob = s.get(Problem, sess.problem_id)
        cmap = s.exec(ContestMap.select().where(ContestMap.wf_year==prob.year, ContestMap.letter==prob.letter)).first()

        # Build samples text
        samples = ""
        for tc in s.exec(TestCase.select().where(TestCase.problem_id==prob.id, TestCase.kind=="sample").order_by(TestCase.idx)):
            samples += f"\n=== Sample #{tc.idx} ===\nInput:\n{tc.input_text}\nOutput:\n{tc.expected_output_text}\n"

        analysis = None
        final_verdict = "ERROR"

        for k in range(1, sess.max_attempts+1):
            code = gpt_generate_solution(prob.statement_md, samples, analysis)
            att = Attempt(id=str(uuid.uuid4()), session_id=sess.id, attempt_no=k, model="gpt", prompt="...", code_cpp=code)
            s.add(att); s.commit()

            _rate_limit_submit()
            sub_id, url = submit_source(cmap.cf_contest_id, cmap.cf_problem_index, code)
            res = poll_submission(cmap.cf_contest_id, sub_id)

            cf = CFSubmission(
                id=str(uuid.uuid4()), attempt_id=att.id, contest_id=cmap.cf_contest_id,
                problem_index=cmap.cf_problem_index, cf_submission_id=sub_id, web_url=url,
                verdict=res["verdict"], test_number=res.get("test_number"),
                time_ms=res.get("time_ms"), memory_kb=res.get("memory_kb"),
                raw_row_html=res.get("raw_row_html")
            )
            att.verdict = _normalize_verdict(cf.verdict)
            att.finished_at = datetime.utcnow()
            s.add(cf); s.add(att); s.commit()
            final_verdict = att.verdict

            if att.verdict == "AC":
                sess.status = "ac"; sess.finished_at = datetime.utcnow(); s.add(sess); s.commit(); return

            # Build minimal local failure context (optional: run some of your tests and capture diffs)
            local_failures = "(no local reproduction)"  # keep simple in Lite
            analysis = deepseek_diagnose(prob.statement_md, code, cf.verdict, local_failures)

        sess.status = final_verdict; sess.finished_at = datetime.utcnow(); s.add(sess); s.commit()
```

---

## CLI entrypoint

```python
# file: apps/cli/run_session.py
import argparse
from core.db import init_db
from core.orchestrator import start_session

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--letter", type=str, required=True)
    parser.add_argument("--attempts", type=int, default=3)
    args = parser.parse_args()
    init_db()
    sid = start_session(args.year, args.letter, args.attempts)
    print("Session:", sid)

if __name__ == "__main__":
    main()
```

---

## Optional: FastAPI (runs inline; no background queue)

```python
# file: apps/api/main.py
from fastapi import FastAPI
from core.db import init_db
from core.orchestrator import start_session

app = FastAPI(title="ICPC Lite")

@app.on_event("startup")
def _init():
    init_db()

@app.post("/solve/{year}/{letter}")
def solve(year: int, letter: str, max_attempts: int = 3):
    sid = start_session(year, letter, max_attempts)
    return {"session_id": sid}
```

> Note: this endpoint **blocks** until the loop finishes. For long runs, prefer the CLI.

---

## First-run checklist

1. `playwright install chromium`
2. Login once to save storage state:

   * `playwright codegen https://codeforces.com/enter` → log in → save → put JSON at `infra/playwright/storageState.json`
3. `python -c "from core.db import init_db; init_db()"`
4. Seed a `Problem`, its `TestCase`s, and a `ContestMap` row.
5. Run: `python apps/cli/run_session.py --year 2018 --letter A`

---

## About Docker

* You **can** exclude Docker entirely.
* If later you want safer local reproduction without containers, consider:

  * Linux `nsjail` (no Docker), or
  * Skip local runs and rely solely on CF verdicts (safest, simplest).

---