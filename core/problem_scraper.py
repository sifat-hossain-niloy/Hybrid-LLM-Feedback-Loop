import os
import json
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def init_webdriver(webdriver_path=None):
    options = webdriver.ChromeOptions()
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    # options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    if webdriver_path:
        service = Service(executable_path=webdriver_path)
        driver = webdriver.Chrome(options=options, service=service)
    else:
        driver = webdriver.Chrome(options=options)
    return driver


def scrape_codeforces_problem(url, driver=None):
    pattern = r'/problem/(\d+)/(\w+)'
    match = re.search(pattern, url)
    if match:
        contest_id = match.group(1)
        problem_index = match.group(2)
        filename = f"problems/{contest_id}-{problem_index}.json"
    else:
        filename = "problems/problem-data.json"

    # Check cache
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            print(f"Loading cached data from {filename}...")
            return json.load(f)

    # Initialize Chrome WebDriver only if not provided
    should_quit_driver = False
    if driver is None:
        driver = init_webdriver()
        should_quit_driver = True

    driver.get(url)
    wait = WebDriverWait(driver, 15)
    
    # Wait for the problem page to load by checking for the problem title
    try:
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#pageContent > div.problemindexholder > div.ttypography > div > div.header > div.title")
        ))
    except Exception:
        # Fallback to checking for problem-statement class
        wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "problem-statement")
        ))
    
    time.sleep(2)  # Give page time to fully render

    # --- Problem Statement ---
    try:
        statement_div = driver.find_element(By.CSS_SELECTOR, ".problem-statement .header + div")
        # Use JavaScript to extract text with proper MathJax handling
        statement = driver.execute_script("""
            function extractText(element) {
                let text = '';
                for (let node of element.childNodes) {
                    if (node.nodeType === Node.TEXT_NODE) {
                        text += node.textContent;
                    } else if (node.nodeType === Node.ELEMENT_NODE) {
                        // Check if it's a MathJax span - extract only the LaTeX from script tag
                        if (node.classList && node.classList.contains('MathJax')) {
                            // Get the LaTeX script tag inside MathJax
                            let script = node.querySelector('script[type="math/tex"]');
                            if (script) {
                                // Wrap in $ for inline math or $$ for display math
                                let mathText = script.textContent;
                                text += '$' + mathText + '$';
                            }
                        } else if (node.classList && node.classList.contains('MathJax_Preview')) {
                            // Skip preview spans - they contain duplicate content
                            continue;
                        } else {
                            // Recursively process other elements
                            text += extractText(node);
                        }
                    }
                }
                return text;
            }
            return extractText(arguments[0]);
        """, statement_div)
    except Exception as e:
        print(f"Warning: Could not find statement: {e}")
        statement = "Not found"
    
    # --- Input Specification ---
    try:
        input_spec_div = driver.find_element(By.CSS_SELECTOR, ".input-specification")
        # Use JavaScript to extract text with proper MathJax handling
        input_spec = driver.execute_script("""
            function extractText(element) {
                let text = '';
                for (let node of element.childNodes) {
                    if (node.nodeType === Node.TEXT_NODE) {
                        text += node.textContent;
                    } else if (node.nodeType === Node.ELEMENT_NODE) {
                        // Check if it's a MathJax span - extract only the LaTeX from script tag
                        if (node.classList && node.classList.contains('MathJax')) {
                            // Get the LaTeX script tag inside MathJax
                            let script = node.querySelector('script[type="math/tex"]');
                            if (script) {
                                // Wrap in $ for inline math
                                let mathText = script.textContent;
                                text += '$' + mathText + '$';
                            }
                        } else if (node.classList && node.classList.contains('MathJax_Preview')) {
                            // Skip preview spans - they contain duplicate content
                            continue;
                        } else {
                            // Recursively process other elements
                            text += extractText(node);
                        }
                    }
                }
                return text;
            }
            return extractText(arguments[0]);
        """, input_spec_div)
        if not input_spec or input_spec.strip() == "":
            input_spec = "Not found"
    except Exception as e:
        print(f"Warning: Could not find input spec: {e}")
        input_spec = "Not found"

    # --- Output Specification ---
    try:
        output_spec_div = driver.find_element(By.CSS_SELECTOR, ".output-specification")
        # Use JavaScript to extract text with proper MathJax handling
        output_spec = driver.execute_script("""
            function extractText(element) {
                let text = '';
                for (let node of element.childNodes) {
                    if (node.nodeType === Node.TEXT_NODE) {
                        text += node.textContent;
                    } else if (node.nodeType === Node.ELEMENT_NODE) {
                        // Check if it's a MathJax span - extract only the LaTeX from script tag
                        if (node.classList && node.classList.contains('MathJax')) {
                            // Get the LaTeX script tag inside MathJax
                            let script = node.querySelector('script[type="math/tex"]');
                            if (script) {
                                // Wrap in $ for inline math
                                let mathText = script.textContent;
                                text += '$' + mathText + '$';
                            }
                        } else if (node.classList && node.classList.contains('MathJax_Preview')) {
                            // Skip preview spans - they contain duplicate content
                            continue;
                        } else {
                            // Recursively process other elements
                            text += extractText(node);
                        }
                    }
                }
                return text;
            }
            return extractText(arguments[0]);
        """, output_spec_div)
        if not output_spec or output_spec.strip() == "":
            output_spec = "Not found"
    except Exception as e:
        print(f"Warning: Could not find output spec: {e}")
        output_spec = "Not found"

    # --- Sample Tests ---
    sample_tests = []
    try:
        sample_test_container = driver.find_element(By.XPATH, "//div[@class='sample-test']")
        input_blocks = sample_test_container.find_elements(By.XPATH, ".//div[@class='input']")
        output_blocks = sample_test_container.find_elements(By.XPATH, ".//div[@class='output']")

        for in_block, out_block in zip(input_blocks, output_blocks):
            in_pre = in_block.find_element(By.XPATH, ".//pre")
            out_pre = out_block.find_element(By.XPATH, ".//pre")
            sample_tests.append({
                "input": in_pre.text.strip(),
                "output": out_pre.text.strip()
            })
    except Exception:
        sample_tests = []

    # --- Note (optional) ---
    #   If a div with class "note" is present, gather the text from all <p> tags.
    #   XPATH example: /html/body/div[6]/div[5]/div[2]/div[3]/div[2]/div/div[6]
    try:
        note_div = driver.find_element(By.XPATH, "//div[@class='note']")
        note_p_elems = note_div.find_elements(By.TAG_NAME, "p")
        if note_p_elems:
            note = "\n".join(p.text for p in note_p_elems)
        else:
            note = "Not found"
    except Exception:
        note = "Not found"

    # --- Tags and Rating (from tags) ---
    tags = []
    rating = "Not found"

    # Collect tags from the tag elements - try multiple approaches
    try:
        # Try to find the sidebar first
        sidebar = driver.find_element(By.ID, "sidebar")
        
        # Look for all divs in sidebar that contain tag boxes
        tag_boxes = sidebar.find_elements(By.CSS_SELECTOR, ".roundbox.sidebox")
        
        # Find the one with "Tags" in it (usually has title or header text)
        for box in tag_boxes:
            try:
                # Check if this box contains tags by looking for the tag structure
                # Tags are typically in a div with multiple child divs containing spans
                tag_content_div = box.find_element(By.CSS_SELECTOR, "div:nth-child(2)")
                child_divs = tag_content_div.find_elements(By.CSS_SELECTOR, ":scope > div")
                
                # If we found child divs, this might be the tags box
                if len(child_divs) > 0:
                    for child_div in child_divs:
                        try:
                            # Get the span inside each child div
                            span_elem = child_div.find_element(By.TAG_NAME, "span")
                            tag_text = span_elem.text.strip()
                            
                            if tag_text and tag_text != "No tag edit access":
                                tags.append(tag_text)
                        except Exception:
                            # If no span found in this div, skip it
                            pass
                    
                    # If we found tags, break out of the loop
                    if tags:
                        break
            except Exception:
                continue
                
    except Exception as e:
        print(f"Warning: Could not find tags: {e}")

    # Find rating among the tags (either a pure digit or starts with *)
    for i, tag in enumerate(tags):
        if tag.isdigit():
            rating = tag
            tags.pop(i)
            break
        elif tag.startswith("*") and tag[1:].isdigit():
            rating = tag[1:]  # Remove the asterisk
            tags.pop(i)
            break

    # Only quit driver if it was created in this function
    if should_quit_driver:
        driver.quit()

    problem_data = {
        "statement": statement,
        "input_specification": input_spec,
        "output_specification": output_spec,
        "sample_tests": sample_tests,
        "note": note,  # The newly added note field
        "tags": tags,
        "rating": rating
    }

    # Clean up the text fields
    def clean_text(text):
        """Clean up text by converting LaTeX to Unicode and normalizing whitespace"""
        if not text or text == "Not found":
            return text
        
        # Convert common LaTeX commands to Unicode symbols
        latex_to_unicode = {
            r'\le': '≤',
            r'\ge': '≥',
            r'\ne': '≠',
            r'\times': '×',
            r'\cdot': '·',
            r'\ldots': '...',
            r'\dots': '...',
            r'\infty': '∞',
            r'\pm': '±',
            r'\to': '→',
            r'\gets': '←',
            r'\rightarrow': '→',
            r'\leftarrow': '←',
            r'\Rightarrow': '⇒',
            r'\Leftarrow': '⇐',
            r'\equiv': '≡',
            r'\approx': '≈',
            r'\subset': '⊂',
            r'\supset': '⊃',
            r'\in': '∈',
            r'\notin': '∉',
            r'\cup': '∪',
            r'\cap': '∩',
            r'\emptyset': '∅',
            r'\forall': '∀',
            r'\exists': '∃',
            r'\sum': '∑',
            r'\prod': '∏',
        }
        
        for latex, unicode_char in latex_to_unicode.items():
            text = text.replace(latex, unicode_char)
        
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        # Replace \n followed by \n with paragraph break
        text = text.replace('\n\n', '\n')
        
        # Clean up extra whitespace around newlines
        text = re.sub(r'\n +', '\n', text)
        text = re.sub(r' +\n', '\n', text)
        
        return text.strip()
    
    # Apply cleaning to all text fields
    problem_data['statement'] = clean_text(problem_data['statement'])
    problem_data['input_specification'] = clean_text(problem_data['input_specification'])
    problem_data['output_specification'] = clean_text(problem_data['output_specification'])
    problem_data['note'] = clean_text(problem_data['note'])
    
    # Save to JSON
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(problem_data, f, indent=4, ensure_ascii=False)

    return problem_data

def get_existing_problems():
    """Return set of problem IDs that already exist"""
    existing = set()
    if os.path.exists("problems"):
        for filename in os.listdir("problems"):
            if filename.endswith(".json"):
                # Extract problem ID (e.g., "2046-A" from "2046-A.json")
                problem_id = filename.replace(".json", "")
                existing.add(problem_id)
    return existing


def get_all_problems_from_page(driver, page_number):
    """Get list of all problem IDs and URLs from a specific page"""
    if page_number == 1:
        url = "https://codeforces.com/problemset?tags=1200-1800"
    else:
        url = f"https://codeforces.com/problemset/page/{page_number}?tags=1200-1800"
    
    print(f"\n📄 Loading page {page_number}...")
    driver.get(url)
    time.sleep(5)
    
    # Wait for table to load
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#pageContent > div.datatable"))
    )
    
    problems_on_page = []
    
    try:
        table = driver.find_element(By.CSS_SELECTOR, "#pageContent > div.datatable > div:nth-child(6) > table > tbody")
        rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # Skip header
        
        print(f"   Found {len(rows)} problem rows")
        
        for row in rows:
            try:
                problem_link = row.find_element(By.CSS_SELECTOR, "td.id a")
                problem_url = problem_link.get_attribute("href")
                
                # Extract contest ID and problem letter
                pattern = r'/problem/(\d+)/(\w+)'
                match = re.search(pattern, problem_url)
                if match:
                    contest_id = match.group(1)
                    problem_letter = match.group(2)
                    problem_id = f"{contest_id}-{problem_letter}"
                    problems_on_page.append({
                        'id': problem_id,
                        'url': problem_url
                    })
            except Exception:
                continue
        
        print(f"   ✅ Extracted {len(problems_on_page)} problem IDs")
        return problems_on_page
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return []


def scrape_multiple_problems(target_total=200, start_page=1, max_pages=10):
    """
    Scrape problems until we have target_total problems in the folder.
    OPTIMIZED: Collects all problem IDs first, then scrapes them one by one.
    """
    print(f"🚀 STARTING OPTIMIZED PROBLEM SCRAPER")
    print(f"   Target: {target_total} problems")
    print(f"   Starting from page: {start_page}")
    print("=" * 60)
    
    # Get existing problems
    existing_problems = get_existing_problems()
    print(f"\n📊 Currently have {len(existing_problems)} problems downloaded")
    
    if len(existing_problems) >= target_total:
        print(f"✅ Already have {len(existing_problems)} problems (target: {target_total})")
        return
    
    # Initialize Chrome WebDriver
    driver = init_webdriver()
    
    try:
        # PHASE 1: Collect all problem IDs from pages
        print(f"\n{'='*60}")
        print("PHASE 1: COLLECTING PROBLEM IDs")
        print(f"{'='*60}")
        
        all_problems = []
        page_number = start_page
        
        while page_number <= max_pages:
            problems_on_page = get_all_problems_from_page(driver, page_number)
            all_problems.extend(problems_on_page)
            
            page_number += 1
            
            # Stop if we have enough problems listed
            if len(all_problems) >= target_total * 2:  # Get extra to account for filtering
                print(f"\n   Collected enough problem IDs ({len(all_problems)})")
                break
        
        print(f"\n{'='*60}")
        print(f"✅ PHASE 1 COMPLETE: Collected {len(all_problems)} problem IDs")
        print(f"{'='*60}")
                    
        # PHASE 2: Filter out existing problems
        print(f"\nPHASE 2: FILTERING")
        problems_to_scrape = [p for p in all_problems if p['id'] not in existing_problems]
        
        # Limit to what we need
        needed = target_total - len(existing_problems)
        problems_to_scrape = problems_to_scrape[:needed]
        
        print(f"   Need to scrape: {len(problems_to_scrape)} problems")
        
        if not problems_to_scrape:
            print("\n✅ No new problems to scrape!")
            return
        
        # PHASE 3: Scrape problems one by one
        print(f"\n{'='*60}")
        print(f"PHASE 3: SCRAPING {len(problems_to_scrape)} PROBLEMS")
        print(f"{'='*60}\n")
        
        for idx, prob in enumerate(problems_to_scrape, 1):
            current_total = len(existing_problems) + idx
            print(f"\n[{idx}/{len(problems_to_scrape)}] Problem {current_total}/{target_total}: {prob['id']}")
            print(f"   URL: {prob['url']}")
            
            try:
                scrape_codeforces_problem(prob['url'], driver)
                print(f"   ✅ Successfully scraped {prob['id']}")
                except Exception as e:
                print(f"   ❌ Error: {e}")
            
            # Small delay between requests
            time.sleep(2)
        
        print(f"\n{'='*60}")
        print("✅ SCRAPING COMPLETE!")
        print(f"{'='*60}")

    except Exception as e:
        print(f"❌ Error in main scraping function: {e}")
    finally:
        driver.quit()
        # Final count
        final_existing = get_existing_problems()
        print(f"\n📊 Final count: {len(final_existing)} problems")
        print(f"{'='*60}")

# Example usage:
if __name__ == "__main__":
    target_total = 200  # Target total number of problems
    start_page = 1  # Start from page 1
    max_pages = 3  # Check first 3 pages (each has ~100 problems)
    scrape_multiple_problems(target_total=target_total, start_page=start_page, max_pages=max_pages)