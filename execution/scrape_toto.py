#!/usr/bin/env python3
"""
Script: scrape_toto.py
Version: 1.0.0
Purpose: Scrape 3 years of Singapore Pools Toto results

Usage:
    python execution/scrape_toto.py [--limit N] [--headless]

Notes:
    - Uses Selenium to navigate the Singapore Pools website
    - Iterates through the draw history dropdown
    - Stores results in SQLite database
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from execution.database import Database

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# =============================================================================
# CONFIGURATION
# =============================================================================

URL_TOTO_RESULTS = "https://www.singaporepools.com.sg/en/product/Pages/toto_results.aspx"
WAIT_TIMEOUT = 10
DELAY_BETWEEN_DRAWS = 0.5  # Seconds between requests


# =============================================================================
# CORE FUNCTIONS
# =============================================================================

def setup_driver(headless=True):
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument("--headless=new")
    
    # Golden Configuration for Oracle Cloud / Linux
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Try using system-installed chromedriver (common on Snaps) or fallback to manager
    service = None
    if Path("/snap/bin/chromium.chromedriver").exists():
        service = Service(executable_path="/snap/bin/chromium.chromedriver")
        if Path("/snap/bin/chromium").exists():
             chrome_options.binary_location = "/snap/bin/chromium"
    else:
        # Fallback to webdriver_manager
        try:
            service = Service(ChromeDriverManager().install())
        except Exception:
            pass 

    if service:
        driver = webdriver.Chrome(service=service, options=chrome_options)
    else:
        driver = webdriver.Chrome(options=chrome_options)
        
    return driver


def get_draw_dates(driver: webdriver.Chrome) -> list[dict]:
    """Get all available draw dates from the dropdown."""
    wait = WebDriverWait(driver, WAIT_TIMEOUT)
    
    dropdown = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "selectDrawList"))
    )
    
    select = Select(dropdown)
    options = []
    
    for option in select.options:
        options.append({
            "value": option.get_attribute("value"),
            "text": option.text.strip(),
        })
    
    return options


def parse_toto_results(driver: webdriver.Chrome) -> list[dict]:
    """Parse Toto results from the current page state."""
    soup = BeautifulSoup(driver.page_source, "html.parser")
    results = []
    
    # Try multiple parsing strategies
    result = parse_toto_layout(soup)
    if result:
        results.append(result)
    
    return results


def parse_toto_layout(soup) -> dict | None:
    """
    Parse Toto results using correct Singapore Pools selectors.
    
    Correct class names:
    - th.drawDate: "Mon, 26 Jan 2026"
    - th.drawNumber: "Draw No. 4151"
    - td.win1 through td.win6: winning numbers
    - td.additional: additional number
    """
    result = {}
    
    # Find the main results table
    table = soup.find("table", class_="table-striped")
    if not table:
        return None
    
    # Find draw date
    draw_date_elem = table.find("th", class_="drawDate")
    if draw_date_elem:
        date_text = draw_date_elem.get_text().strip()
        result["draw_date"] = parse_date(date_text)
    
    # Find draw number
    draw_number_elem = table.find("th", class_="drawNumber")
    if draw_number_elem:
        text = draw_number_elem.get_text().strip()
        match = re.search(r"(\d+)", text)
        if match:
            result["draw_number"] = match.group(1)
    
    # Find winning numbers using specific class names win1-win6
    winning_numbers = []
    for i in range(1, 7):
        win_cell = soup.find("td", class_=f"win{i}")
        if win_cell:
            num_text = win_cell.get_text().strip()
            if num_text.isdigit():
                winning_numbers.append(int(num_text))
    
    # Find additional number
    additional_cell = soup.find("td", class_="additional")
    additional_number = None
    if additional_cell:
        add_text = additional_cell.get_text().strip()
        if add_text.isdigit():
            additional_number = int(add_text)
    
    result["winning_numbers"] = winning_numbers
    result["additional_number"] = additional_number
    result["prize_pool"] = None  # Can be added later if needed
    
    # Validate we have minimum required data
    if result.get("winning_numbers") and len(result["winning_numbers"]) == 6 and result.get("draw_number"):
        return result
    return None


def parse_date(date_str: str) -> str:
    """Convert date string to YYYY-MM-DD format."""
    months = {
        "jan": "01", "feb": "02", "mar": "03", "apr": "04",
        "may": "05", "jun": "06", "jul": "07", "aug": "08",
        "sep": "09", "oct": "10", "nov": "11", "dec": "12"
    }
    
    match = re.search(
        r"(\d{1,2})\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*(\d{4})",
        date_str, re.I
    )
    if match:
        day = match.group(1).zfill(2)
        month = months.get(match.group(2).lower(), "01")
        year = match.group(3)
        return f"{year}-{month}-{day}"
    return date_str


def scrape_all_draws(driver: webdriver.Chrome, db: Database, limit: int | None = None) -> dict:
    """Scrape all available Toto draws."""
    print("🎰 Starting Toto results scraper...")
    print(f"   URL: {URL_TOTO_RESULTS}")
    
    # Navigate to results page
    driver.get(URL_TOTO_RESULTS)
    time.sleep(2)  # Wait for initial load
    
    # Get all available draw dates
    draw_options = get_draw_dates(driver)
    total_draws = len(draw_options)
    
    if limit:
        draw_options = draw_options[:limit]
    
    print(f"   Found {total_draws} draws in dropdown, processing {len(draw_options)}")
    
    stats = {
        "total_found": total_draws,
        "processed": 0,
        "inserted": 0,
        "duplicates": 0,
        "errors": 0,
    }
    
    for i, option in enumerate(draw_options):
        try:
            # Select draw from dropdown
            wait = WebDriverWait(driver, WAIT_TIMEOUT)
            dropdown = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "selectDrawList"))
            )
            select = Select(dropdown)
            select.select_by_value(option["value"])
            
            time.sleep(DELAY_BETWEEN_DRAWS)
            
            # Parse results
            results = parse_toto_results(driver)
            
            for result in results:
                if (result.get("winning_numbers") and 
                    len(result["winning_numbers"]) == 6 and
                    result.get("additional_number") and
                    result.get("draw_number")):
                    
                    inserted = db.insert_toto_draw(
                        draw_number=result["draw_number"],
                        draw_date=result.get("draw_date", ""),
                        winning_numbers=result["winning_numbers"],
                        additional_number=result["additional_number"],
                        prize_pool=result.get("prize_pool")
                    )
                    
                    if inserted:
                        stats["inserted"] += 1
                    else:
                        stats["duplicates"] += 1
            
            stats["processed"] += 1
            
            if (i + 1) % 10 == 0:
                print(f"   Progress: {i + 1}/{len(draw_options)} draws processed")
                
        except Exception as e:
            print(f"   ⚠ Error processing draw {option['text']}: {e}")
            stats["errors"] += 1
            continue
    
    return stats


def main(headless: bool = True, limit: int | None = None) -> dict:
    """Main execution function."""
    driver = None
    
    try:
        driver = setup_driver(headless=headless)
        
        with Database() as db:
            initial_count = db.get_toto_draws_count()
            print(f"   Initial DB count: {initial_count} draws")
            
            stats = scrape_all_draws(driver, db, limit=limit)
            
            final_count = db.get_toto_draws_count()
            print(f"\n✅ Scraping complete!")
            print(f"   Processed: {stats['processed']}")
            print(f"   New inserts: {stats['inserted']}")
            print(f"   Duplicates skipped: {stats['duplicates']}")
            print(f"   Errors: {stats['errors']}")
            print(f"   Total in DB: {final_count}")
            
            return {
                "status": "success",
                "stats": stats,
                "total_in_db": final_count,
            }
            
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        return {
            "status": "error",
            "error": str(e),
        }
        
    finally:
        if driver:
            driver.quit()


# =============================================================================
# CLI ENTRYPOINT
# =============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Singapore Pools Toto results")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of draws to scrape")
    parser.add_argument("--headless", action="store_true", default=True, help="Run browser in headless mode")
    parser.add_argument("--visible", action="store_true", help="Show browser window")
    parser.add_argument("--output", default=".tmp/scrape_toto_results.json", help="Output file path")
    
    args = parser.parse_args()
    
    Path(".tmp").mkdir(exist_ok=True)
    
    headless = not args.visible
    result = main(headless=headless, limit=args.limit)
    
    with open(args.output, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"\n📄 Output written to {args.output}")
    sys.exit(0 if result["status"] == "success" else 1)
