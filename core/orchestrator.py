import uuid
from datetime import datetime
from core.db import get_session
from core.models import *
from core.llm_gateway import gpt_generate_solution, deepseek_diagnose
from core.codeforces_client import submit_source, poll_submission
from core.config import MAX_ATTEMPTS, CF_SUBMIT_SPACING_SEC
from core.solution_saver import save_solution, get_next_iteration_number

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

def start_session(contest_id: int, letter: str, max_attempts: int = MAX_ATTEMPTS) -> str:
    sid = str(uuid.uuid4())
    with get_session() as s:
        from sqlmodel import select
        prob = s.exec(
            select(Problem).where(Problem.contest_id == contest_id, Problem.letter == letter)
        ).first()
        if not prob:
            raise RuntimeError(f"Problem {contest_id}{letter} not found; seed it first.")
        sess = SolveSession(id=sid, problem_id=prob.id, max_attempts=max_attempts, status="running")
        s.add(sess); s.commit()
    run_session(sid)
    return sid

def run_session(session_id: str):
    with get_session() as s:
        from sqlmodel import select
        sess = s.get(SolveSession, session_id)
        prob = s.get(Problem, sess.problem_id)
        cmap = s.exec(select(ContestMap).where(ContestMap.contest_id==prob.contest_id, ContestMap.letter==prob.letter)).first()

        # Build samples text
        samples = ""
        from core.models import TestKind
        for tc in s.exec(select(TestCase).where(TestCase.problem_id==prob.id, TestCase.kind==TestKind.SAMPLE).order_by(TestCase.idx)):
            samples += f"\n=== Sample #{tc.idx} ===\nInput:\n{tc.input_text}\nOutput:\n{tc.expected_output_text}\n"

        analysis = None
        final_verdict = "ERROR"
        previous_verdict = None

        # Get starting iteration number for this problem
        base_iteration = get_next_iteration_number(prob.id)

        for k in range(1, sess.max_attempts+1):
            iteration_num = base_iteration + k - 1
            print(f"🤖 Generating solution (attempt {k}/{sess.max_attempts}, iteration {iteration_num})...")
            
            code = gpt_generate_solution(prob.statement_md, samples, analysis)
            att = Attempt(id=str(uuid.uuid4()), session_id=sess.id, attempt_no=k, model="gpt", prompt="...", code_cpp=code)
            s.add(att); s.commit()

            # Save solution with metadata
            try:
                save_solution(
                    problem_id=prob.id,
                    code=code,
                    model="GPT-4",
                    iteration=iteration_num,
                    verdict=previous_verdict,
                    analysis=analysis,
                    timestamp=datetime.utcnow()
                )
            except Exception as e:
                print(f"Warning: Could not save solution: {e}")

            # Check if we have a contest mapping before submitting
            if not cmap:
                print(f"⚠️  No Codeforces mapping found for {prob.id}. Skipping submission.")
                print(f"💾 Solution saved locally as iteration {iteration_num}")
                final_verdict = "NO_MAPPING"
                break

            print(f"📤 Submitting to Codeforces contest {cmap.cf_contest_id} problem {cmap.cf_problem_index}...")
            _rate_limit_submit()
            sub_id, url = submit_source(cmap.cf_contest_id, cmap.cf_problem_index, code)
            print(f"⏳ Polling submission {sub_id}...")
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
            previous_verdict = cf.verdict

            print(f"🔍 Verdict: {cf.verdict}")

            if att.verdict == "AC":
                print(f"🎉 Accepted! Solution saved as iteration {iteration_num}")
                sess.status = "ac"; sess.finished_at = datetime.utcnow(); s.add(sess); s.commit(); return

            # Build minimal local failure context (optional: run some of your tests and capture diffs)
            local_failures = "(no local reproduction)"  # keep simple in Lite
            print(f"🔍 Analyzing failure with DeepSeek...")
            analysis = deepseek_diagnose(prob.statement_md, code, cf.verdict, local_failures)
            print(f"📝 Analysis: {analysis[:100]}...")

        sess.status = final_verdict; sess.finished_at = datetime.utcnow(); s.add(sess); s.commit()
