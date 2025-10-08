from datetime import datetime
from typing import Optional
from enum import Enum
from sqlmodel import SQLModel, Field

class Verdict(str, Enum):
    AC = "AC"
    WA = "WA"
    TLE = "TLE"
    MLE = "MLE"
    RE = "RE"
    CE = "CE"
    PE = "PE"
    SEC = "SEC"
    IL = "IL"
    JUDGE_TIMEOUT = "JUDGE_TIMEOUT"
    ERROR = "ERROR"

class TestKind(str, Enum):
    SAMPLE = "sample"
    HIDDEN = "hidden"

class Problem(SQLModel, table=True):
    id: str = Field(primary_key=True)
    contest_id: int
    letter: str
    title: str
    statement_md: str
    rating: Optional[str] = None
    tags: Optional[str] = None  # JSON string of tags array

class TestCase(SQLModel, table=True):
    id: str = Field(primary_key=True)
    problem_id: str = Field(foreign_key="problem.id")
    kind: TestKind = TestKind.HIDDEN
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
    contest_id: int
    letter: str
    cf_contest_id: int
    cf_problem_index: str
