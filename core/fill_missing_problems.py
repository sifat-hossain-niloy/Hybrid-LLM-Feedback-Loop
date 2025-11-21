"""
Script to fill in any missing problems from Codeforces pages 1-2 (1200-1800 rating)
"""
import os
import re
import time
from problem_scraper import init_webdriver, scrape_codeforces_problem
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_existing_problems():
    """Return set of problem IDs that already exist"""
    existing = set()
    if os.path.exists("problems"):
        for filename in os.listdir("problems"):
            if filename.endswith(".json"):
                problem_id = filename.replace(".json", "")
                existing.add(problem_id)
    return existing


def get_all_problems_from_page(driver, page_number):
    """Get list of all problem IDs from a specific page"""
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
            except Exception as e:
                continue
        
        print(f"   ✅ Extracted {len(problems_on_page)} problem IDs")
        return problems_on_page
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return []


def fill_missing_problems(pages_to_check=[1, 2]):
    """Find and scrape missing problems from specified pages"""
    
    print("🔍 FILLING MISSING PROBLEMS FROM PAGES 1-2")
    print("=" * 60)
    
    # Get existing problems
    existing = get_existing_problems()
    print(f"\n📊 Currently have {len(existing)} problems downloaded")
    
    # Initialize driver
    driver = init_webdriver()
    
    all_missing = []
    
    try:
        # Check each page
        for page_num in pages_to_check:
            problems_on_page = get_all_problems_from_page(driver, page_num)
            
            # Find missing problems
            missing_from_page = []
            for prob in problems_on_page:
                if prob['id'] not in existing:
                    missing_from_page.append(prob)
            
            print(f"\n   📋 Page {page_num}: {len(missing_from_page)} missing problems")
            if missing_from_page:
                print("   Missing IDs:", ", ".join([p['id'] for p in missing_from_page[:10]]))
                if len(missing_from_page) > 10:
                    print(f"   ... and {len(missing_from_page) - 10} more")
            
            all_missing.extend(missing_from_page)
        
        print(f"\n" + "=" * 60)
        print(f"📊 TOTAL MISSING: {len(all_missing)} problems")
        print("=" * 60)
        
        if not all_missing:
            print("\n✅ No missing problems! Pages 1-2 are complete.")
            return
        
        # Scrape missing problems
        print(f"\n🚀 Starting to scrape {len(all_missing)} missing problems...\n")
        
        for idx, prob in enumerate(all_missing, 1):
            print(f"\n[{idx}/{len(all_missing)}] Scraping {prob['id']}...")
            print(f"   URL: {prob['url']}")
            
            try:
                scrape_codeforces_problem(prob['url'], driver)
                print(f"   ✅ Successfully scraped {prob['id']}")
            except Exception as e:
                print(f"   ❌ Error scraping {prob['id']}: {e}")
            
            # Small delay between requests
            time.sleep(2)
        
        print(f"\n" + "=" * 60)
        print(f"✅ COMPLETE! Scraped {len(all_missing)} missing problems")
        
        # Final count
        final_existing = get_existing_problems()
        print(f"📊 Final count: {len(final_existing)} problems")
        print("=" * 60)
    
    finally:
        driver.quit()


if __name__ == "__main__":
    # Check and fill missing problems from pages 1 and 2
    fill_missing_problems(pages_to_check=[1, 2])

