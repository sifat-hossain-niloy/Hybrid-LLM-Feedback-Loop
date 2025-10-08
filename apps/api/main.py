from fastapi import FastAPI
from core.db import init_db
from core.orchestrator import start_session

app = FastAPI(title="Hybrid LLM ICPC Solver")

@app.on_event("startup")
def _init():
    init_db()

@app.post("/solve/{contest_id}/{letter}")
def solve(contest_id: int, letter: str, max_attempts: int = 3):
    """Solve a problem from a contest."""
    sid = start_session(contest_id, letter, max_attempts)
    return {"session_id": sid}
