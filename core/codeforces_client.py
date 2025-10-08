"""
Robust Codeforces submission client with Cloudflare bypass and CAPTCHA solving.
"""

import time
import re
import json
import os
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import cloudscraper
from core.config import (
    CF_USERNAME, CF_PASSWORD, CF_SUBMIT_SPACING_SEC, CF_POLL_TIMEOUT_SEC,
    CF_DEFAULT_LANG_ID, CAPTCHA_SERVICE, CAPTCHA_API_KEY, CF_SUBMIT_METHOD
)

class CodeforcesClient:
    def __init__(self):
        # Create cloudscraper session with enhanced features
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            },
            debug=False
        )
        
        # Set realistic headers
        self.scraper.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        self.logged_in = False
        self.csrf_token = None
        self.last_submit_time = 0
        
    def _rate_limit(self):
        """Apply rate limiting between submissions."""
        elapsed = time.time() - self.last_submit_time
        if elapsed < CF_SUBMIT_SPACING_SEC:
            sleep_time = CF_SUBMIT_SPACING_SEC - elapsed
            print(f"⏳ Rate limiting: waiting {sleep_time:.1f}s...")
            time.sleep(sleep_time)
        self.last_submit_time = time.time()
        
    def _solve_captcha(self, captcha_img_url: str) -> Optional[str]:
        """Solve CAPTCHA using configured service."""
        if CAPTCHA_SERVICE == "none" or not CAPTCHA_API_KEY:
            print("⚠️  CAPTCHA detected but no solving service configured")
            return None
            
        print(f"🔍 Solving CAPTCHA using {CAPTCHA_SERVICE}...")
        
        # Download CAPTCHA image
        img_response = self.scraper.get(captcha_img_url)
        if img_response.status_code != 200:
            print("❌ Failed to download CAPTCHA image")
            return None
            
        # Here you would integrate with actual CAPTCHA solving services
        # For now, this is a placeholder
        if CAPTCHA_SERVICE == "2captcha":
            return self._solve_with_2captcha(img_response.content)
        elif CAPTCHA_SERVICE == "anticaptcha":
            return self._solve_with_anticaptcha(img_response.content)
        
        return None
    
    def _solve_with_2captcha(self, img_data: bytes) -> Optional[str]:
        """Solve CAPTCHA using 2captcha service."""
        # Placeholder for 2captcha integration
        print("📝 2captcha integration would go here")
        return None
    
    def _solve_with_anticaptcha(self, img_data: bytes) -> Optional[str]:
        """Solve CAPTCHA using anticaptcha service."""
        # Placeholder for anticaptcha integration
        print("📝 Anticaptcha integration would go here")
        return None
        
    def _extract_csrf_token(self, html: str) -> Optional[str]:
        """Extract CSRF token from HTML."""
        # Look for meta CSRF token
        soup = BeautifulSoup(html, 'lxml')
        
        # Try meta tag first
        meta_token = soup.find('meta', {'name': 'X-Csrf-Token'})
        if meta_token and meta_token.get('content'):
            return meta_token['content']
            
        # Try hidden input
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        if csrf_input and csrf_input.get('value'):
            return csrf_input['value']
            
        # Try to find in script tags
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                match = re.search(r'csrf["\']?\s*:\s*["\']([^"\']+)["\']', script.string, re.I)
                if match:
                    return match.group(1)
                    
        return None
    
    def login(self, username: Optional[str] = None, password: Optional[str] = None) -> bool:
        """Login to Codeforces."""
        if self.logged_in:
            return True
            
        username = username or CF_USERNAME
        password = password or CF_PASSWORD
        
        if not username or not password:
            print("❌ No Codeforces credentials provided")
            return False
            
        print(f"🔐 Logging in to Codeforces as {username}...")
        
        try:
            # Get login page
            login_url = "https://codeforces.com/enter"
            response = self.scraper.get(login_url)
            
            if response.status_code != 200:
                print(f"❌ Failed to access login page: {response.status_code}")
                return False
                
            # Extract CSRF token
            self.csrf_token = self._extract_csrf_token(response.text)
            if not self.csrf_token:
                print("⚠️  Could not find CSRF token")
                
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Find login form
            login_form = soup.find('form', {'id': 'enterForm'})
            if not login_form:
                print("❌ Could not find login form")
                return False
                
            # Prepare login data
            form_data = {
                'handleOrEmail': username,
                'password': password,
                'action': 'enter',
                '_tta': '176',  # Common value, may need updating
            }
            
            if self.csrf_token:
                form_data['csrf_token'] = self.csrf_token
                
            # Check for CAPTCHA
            captcha_img = soup.find('img', {'class': 'captcha-img'})
            if captcha_img:
                captcha_url = urljoin(login_url, captcha_img['src'])
                captcha_solution = self._solve_captcha(captcha_url)
                if captcha_solution:
                    form_data['captcha'] = captcha_solution
                else:
                    print("❌ CAPTCHA solving failed")
                    return False
                    
            # Submit login form
            response = self.scraper.post(login_url, data=form_data)
            
            # Check if login was successful
            if 'handle' in response.url or 'logout' in response.text.lower():
                print("✅ Successfully logged in to Codeforces")
                self.logged_in = True
                return True
            else:
                print("❌ Login failed")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def get_language_options(self, contest_id: int) -> Dict[str, int]:
        """Get available programming languages for a contest."""
        if not self.logged_in and not self.login():
            return {}
            
        try:
            submit_url = f"https://codeforces.com/gym/{contest_id}/submit"
            response = self.scraper.get(submit_url)
            
            if response.status_code != 200:
                return {}
                
            soup = BeautifulSoup(response.text, 'lxml')
            lang_select = soup.find('select', {'name': 'programTypeId'})
            
            if not lang_select:
                return {}
                
            languages = {}
            for option in lang_select.find_all('option'):
                if option.get('value'):
                    languages[option.text.strip()] = int(option['value'])
                    
            return languages
            
        except Exception as e:
            print(f"⚠️  Error getting language options: {e}")
            return {}
    
    def submit_solution(
        self, 
        contest_id: int, 
        problem_index: str, 
        source_code: str,
        language_id: Optional[int] = None
    ) -> Tuple[Optional[int], Optional[str]]:
        """Submit a solution to Codeforces."""
        
        if not self.logged_in and not self.login():
            raise Exception("Failed to login to Codeforces")
            
        self._rate_limit()
        
        language_id = language_id or CF_DEFAULT_LANG_ID
        
        print(f"📤 Submitting to contest {contest_id}, problem {problem_index}...")
        
        try:
            submit_url = f"https://codeforces.com/gym/{contest_id}/submit"
            
            # Get submit page
            response = self.scraper.get(submit_url)
            if response.status_code != 200:
                raise Exception(f"Failed to access submit page: {response.status_code}")
                
            # Extract CSRF token
            csrf_token = self._extract_csrf_token(response.text)
            
            # Prepare submission data
            submit_data = {
                'csrf_token': csrf_token,
                'action': 'submitSolutionFormSubmitted',
                'submittedProblemIndex': problem_index,
                'programTypeId': str(language_id),
                'source': source_code,
                'tabsize': '4',
                '_tta': '176'
            }
            
            # Submit the solution
            response = self.scraper.post(submit_url, data=submit_data)
            
            if response.status_code != 200:
                raise Exception(f"Submission failed with status: {response.status_code}")
                
            # Check if submission was successful by looking for redirect or success indicators
            if 'submissions' in response.url or 'my' in response.url:
                # Get submission ID from the my submissions page
                my_url = f"https://codeforces.com/gym/{contest_id}/my"
                my_response = self.scraper.get(my_url)
                
                if my_response.status_code == 200:
                    soup = BeautifulSoup(my_response.text, 'lxml')
                    
                    # Find the most recent submission
                    submission_links = soup.find_all('a', href=re.compile(r'/gym/\d+/submission/\d+'))
                    
                    if submission_links:
                        submission_url = submission_links[0]['href']
                        submission_id = int(submission_url.split('/')[-1])
                        full_url = f"https://codeforces.com{submission_url}"
                        
                        print(f"✅ Submission successful! ID: {submission_id}")
                        return submission_id, full_url
                        
            raise Exception("Could not determine submission ID")
            
        except Exception as e:
            print(f"❌ Submission error: {e}")
            raise
    
    def get_submission_result(self, contest_id: int, submission_id: int) -> Dict[str, Any]:
        """Get the result of a submission."""
        
        print(f"⏳ Polling submission {submission_id}...")
        
        submission_url = f"https://codeforces.com/gym/{contest_id}/submission/{submission_id}"
        start_time = time.time()
        
        while True:
            try:
                response = self.scraper.get(submission_url)
                
                if response.status_code != 200:
                    print(f"⚠️  Error accessing submission: {response.status_code}")
                    time.sleep(3)
                    continue
                    
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Look for verdict in the submission table
                verdict_cell = soup.find('span', {'class': re.compile(r'verdict.*')})
                if not verdict_cell:
                    # Alternative: look in submission info table
                    info_table = soup.find('table', {'class': 'rtable'})
                    if info_table:
                        rows = info_table.find_all('tr')
                        for row in rows:
                            cells = row.find_all('td')
                            if len(cells) >= 2 and 'Verdict' in cells[0].text:
                                verdict_cell = cells[1]
                                break
                
                if verdict_cell:
                    verdict_text = verdict_cell.get_text(strip=True)
                    
                    # Extract additional information
                    test_match = re.search(r'on test (\d+)', verdict_text, re.I)
                    time_match = re.search(r'(\d+) ms', response.text)
                    memory_match = re.search(r'(\d+) KB', response.text)
                    
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

# Global instance
_cf_client = None

def get_codeforces_client() -> CodeforcesClient:
    """Get or create the global Codeforces client instance."""
    global _cf_client
    if _cf_client is None:
        _cf_client = CodeforcesClient()
    return _cf_client

# Compatibility functions for existing code
def submit_source(contest_id: int, problem_index: str, source: str, language_id: Optional[int] = None):
    """Submit source code to Codeforces (compatibility function)."""
    client = get_codeforces_client()
    return client.submit_solution(contest_id, problem_index, source, language_id)

def poll_submission(contest_id: int, submission_id: int, timeout_sec: int = CF_POLL_TIMEOUT_SEC):
    """Poll submission result (compatibility function)."""
    client = get_codeforces_client()
    result = client.get_submission_result(contest_id, submission_id)
    
    # Convert to old format for compatibility
    return {
        'verdict': result['verdict'],
        'test_number': result['test_number'],
        'time_ms': result['time_ms'],
        'memory_kb': result['memory_kb'],
        'raw_row_html': result['raw_html']
    }
