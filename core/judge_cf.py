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
