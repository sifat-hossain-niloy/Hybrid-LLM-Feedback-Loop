"""
Codeforces problemset submission client for main contest problems.
"""

import time
import re
from typing import Optional, Tuple, Dict, Any
from bs4 import BeautifulSoup
from core.codeforces_client import CodeforcesClient

class CodeforcesProblemsetClient(CodeforcesClient):
    """Extended client for main problemset submissions."""
    
    def submit_problemset_solution(
        self, 
        contest_id: int, 
        problem_letter: str, 
        source_code: str,
        language_id: Optional[int] = None
    ) -> Tuple[Optional[int], Optional[str]]:
        """Submit a solution to main Codeforces problemset."""
        
        if not self.logged_in and not self.login():
            raise Exception("Failed to login to Codeforces")
            
        self._rate_limit()
        
        from core.config import CF_DEFAULT_LANG_ID
        language_id = language_id or CF_DEFAULT_LANG_ID
        
        print(f"📤 Submitting to problemset {contest_id}{problem_letter}...")
        
        try:
            # Step 1: Visit the problem page
            problem_url = f"https://codeforces.com/problemset/problem/{contest_id}/{problem_letter}"
            print(f"🔗 Accessing problem: {problem_url}")
            
            response = self.scraper.get(problem_url)
            if response.status_code != 200:
                raise Exception(f"Failed to access problem page: {response.status_code}")
            
            # Step 2: Find and click the submit link
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Look for submit link - usually in the problem menu
            submit_links = soup.find_all('a', href=re.compile(r'/problemset/submit'))
            if not submit_links:
                raise Exception("Could not find submit link on problem page")
                
            submit_url = f"https://codeforces.com{submit_links[0]['href']}"
            print(f"🔗 Found submit URL: {submit_url}")
            
            # Step 3: Go to submit page
            response = self.scraper.get(submit_url)
            if response.status_code != 200:
                raise Exception(f"Failed to access submit page: {response.status_code}")
                
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Step 4: Extract CSRF token and form data
            csrf_token = self._extract_csrf_token(response.text)
            
            # Find the form
            submit_form = soup.find('form', {'class': 'submit-form'}) or soup.find('form')
            if not submit_form:
                raise Exception("Could not find submit form")
                
            # Get form action
            form_action = submit_form.get('action', submit_url)
            if not form_action.startswith('http'):
                form_action = f"https://codeforces.com{form_action}"
            
            # Step 5: Prepare submission data
            submit_data = {
                'csrf_token': csrf_token,
                'action': 'submitSolutionFormSubmitted',
                'submittedProblemCode': f"{contest_id}{problem_letter}",
                'programTypeId': str(language_id),
                'source': source_code,
                'tabsize': '4',
                '_tta': '176'
            }
            
            # Add any hidden fields from the form
            hidden_inputs = submit_form.find_all('input', type='hidden')
            for hidden_input in hidden_inputs:
                name = hidden_input.get('name')
                value = hidden_input.get('value', '')
                if name and name not in submit_data:
                    submit_data[name] = value
            
            print("📝 Submitting solution...")
            
            # Step 6: Submit the form
            response = self.scraper.post(form_action, data=submit_data)
            
            if response.status_code != 200:
                raise Exception(f"Submission failed with status: {response.status_code}")
            
            print("✅ Submission sent successfully!")
            
            # Step 7: Try to get submission ID from the response or my submissions page
            # Check if we're redirected to status page
            if 'submissions' in response.url or 'status' in response.url:
                # Try to extract submission ID from URL or page content
                submission_match = re.search(r'submission/(\d+)', response.url)
                if submission_match:
                    submission_id = int(submission_match.group(1))
                    submission_url = f"https://codeforces.com/problemset/submission/{contest_id}/{submission_id}"
                    print(f"🎯 Submission ID: {submission_id}")
                    return submission_id, submission_url
            
            # Alternative: Check my submissions page
            my_url = f"https://codeforces.com/problemset/status/{contest_id}/problem/{problem_letter}/my"
            print(f"🔍 Checking submissions at: {my_url}")
            
            my_response = self.scraper.get(my_url)
            
            if my_response.status_code == 200:
                soup = BeautifulSoup(my_response.text, 'lxml')
                
                # Find the most recent submission
                submission_rows = soup.find_all('tr', {'data-submission-id': True})
                
                if submission_rows:
                    submission_id = int(submission_rows[0]['data-submission-id'])
                    submission_url = f"https://codeforces.com/problemset/submission/{contest_id}/{submission_id}"
                    
                    print(f"🎯 Found submission ID: {submission_id}")
                    return submission_id, submission_url
                else:
                    # Try alternative method - look for submission links
                    submission_links = soup.find_all('a', href=re.compile(r'/problemset/submission/\d+/\d+'))
                    if submission_links:
                        href = submission_links[0]['href']
                        submission_id = int(href.split('/')[-1])
                        submission_url = f"https://codeforces.com{href}"
                        
                        print(f"🎯 Found submission ID: {submission_id}")
                        return submission_id, submission_url
            
            raise Exception("Could not determine submission ID - submission may have failed")
            
        except Exception as e:
            print(f"❌ Submission error: {e}")
            raise
    
    def get_problemset_submission_result(self, contest_id: int, submission_id: int) -> Dict[str, Any]:
        """Get the result of a problemset submission."""
        
        print(f"⏳ Polling problemset submission {submission_id}...")
        
        submission_url = f"https://codeforces.com/problemset/submission/{contest_id}/{submission_id}"
        start_time = time.time()
        
        from core.config import CF_POLL_TIMEOUT_SEC
        
        while True:
            try:
                response = self.scraper.get(submission_url)
                
                if response.status_code != 200:
                    print(f"⚠️  Error accessing submission: {response.status_code}")
                    time.sleep(3)
                    continue
                    
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Look for verdict in submission details
                verdict_spans = soup.find_all('span', {'class': re.compile(r'verdict.*')})
                
                verdict_text = None
                for span in verdict_spans:
                    text = span.get_text(strip=True)
                    if any(verdict in text for verdict in ['Accepted', 'Wrong answer', 'Time limit', 'Memory limit', 'Runtime error', 'Compilation error']):
                        verdict_text = text
                        break
                
                if not verdict_text:
                    # Alternative: look in the submission table
                    verdict_cell = soup.find('td', string=re.compile(r'(Accepted|Wrong answer|Time limit|Memory limit|Runtime error|Compilation error)', re.I))
                    if verdict_cell:
                        verdict_text = verdict_cell.get_text(strip=True)
                
                if not verdict_text:
                    # Look for "In queue" or "Running" status
                    status_indicators = ['In queue', 'Compiling', 'Running', 'Judging']
                    for indicator in status_indicators:
                        if indicator.lower() in response.text.lower():
                            verdict_text = indicator
                            break
                
                if verdict_text:
                    # Extract additional information
                    test_match = re.search(r'on test (\d+)', response.text, re.I)
                    time_match = re.search(r'(\d+)\s*ms', response.text)
                    memory_match = re.search(r'(\d+)\s*KB', response.text)
                    
                    # Check if verdict is final
                    final_verdicts = [
                        'Accepted', 'Wrong answer', 'Time limit exceeded',
                        'Memory limit exceeded', 'Runtime error', 'Compilation error',
                        'Presentation error', 'Idleness limit exceeded', 'Security violated'
                    ]
                    
                    is_final = any(final in verdict_text for final in final_verdicts)
                    
                    result = {
                        'verdict': verdict_text,
                        'test_number': int(test_match.group(1)) if test_match else None,
                        'time_ms': int(time_match.group(1)) if time_match else None,
                        'memory_kb': int(memory_match.group(1)) if memory_match else None,
                        'raw_html': str(soup),
                        'final': is_final
                    }
                    
                    if is_final:
                        print(f"🔍 Final verdict: {verdict_text}")
                        return result
                    else:
                        print(f"⏳ Current status: {verdict_text}")
                
                # Check timeout
                from core.config import CF_POLL_TIMEOUT_SEC
                if time.time() - start_time > CF_POLL_TIMEOUT_SEC:
                    return {
                        'verdict': 'JUDGE_TIMEOUT',
                        'test_number': None,
                        'time_ms': None,
                        'memory_kb': None,
                        'raw_html': response.text,
                        'final': True
                    }
                    
                time.sleep(3)
                
            except Exception as e:
                print(f"⚠️  Polling error: {e}")
                time.sleep(5)
                
                if time.time() - start_time > CF_POLL_TIMEOUT_SEC:
                    return {
                        'verdict': 'ERROR',
                        'test_number': None,
                        'time_ms': None,
                        'memory_kb': None,
                        'raw_html': str(e),
                        'final': True
                    }

# Global instance for problemset
_problemset_client = None

def get_problemset_client() -> CodeforcesProblemsetClient:
    """Get or create the global problemset client instance."""
    global _problemset_client
    if _problemset_client is None:
        _problemset_client = CodeforcesProblemsetClient()
    return _problemset_client
