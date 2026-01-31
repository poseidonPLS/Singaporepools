#!/usr/bin/env python3
"""
Script: scrape_4d.py
Version: 1.0.0
Purpose: Scrape 3 years of Singapore Pools 4D results

Usage:
    python execution/scrape_4d.py [--limit N] [--headless]

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

# =============================================================================
# CONFIGURATION
# =============================================================================

URL_4D_RESULTS = "https://www.singaporepools.com.sg/en/product/Pages/4d_results.aspx"
WAIT_TIMEOUT = 10
DELAY_BETWEEN_DRAWS = 0.5  # Seconds between requests (be nice to the server)


# =============================================================================
# CORE FUNCTIONS
# =============================================================================

def setup_driver(headless: bool = True) -> webdriver.Chrome:
    """
    Set up Chrome WebDriver with appropriate options.
    
    Args:
        headless: Run browser without GUI
        
    Returns:
        Configured Chrome WebDriver instance
    """
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
    
    # Linux/Snap compatibility
    if Path("/snap/bin/chromium").exists():
        options.binary_location = "/snap/bin/chromium"
    
    service = None
    if Path("/snap/bin/chromium.chromedriver").exists():
        service = Service(executable_path="/snap/bin/chromium.chromedriver")
    else:
        try:
            service = Service(ChromeDriverManager().install())
        except Exception:
            pass # Fallback to default path
            
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def get_draw_dates(driver: webdriver.Chrome) -> list[dict]:
    """
    Get all available draw dates from the dropdown.
    
    Returns:
        List of dicts with 'value' and 'text' for each option
    """
    wait = WebDriverWait(driver, WAIT_TIMEOUT)
    
    # Wait for the dropdown to be present
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


def parse_4d_results(driver: webdriver.Chrome) -> list[dict]:
    """
    Parse 4D results from the current page state.
    Uses the correct Singapore Pools CSS class names.
    
    Returns:
        List of draw result dictionaries
    """
    soup = BeautifulSoup(driver.page_source, "html.parser")
    results = []
    
    # Find all result tables with the correct class
    # Singapore Pools uses: table.table-striped.orange-header for main prizes
    draw_tables = soup.find_all("table", class_="table-striped")
    
    for table in draw_tables:
        try:
            result = parse_single_draw_table(table, soup)
            if result:
                results.append(result)
        except Exception as e:
            print(f"  ⚠ Error parsing draw table: {e}")
            continue
    
    return results


def parse_single_draw_table(table, soup) -> dict | None:
    """
    Parse a single 4D draw result table using correct Singapore Pools selectors.
    
    Correct class names:
    - th.drawDate: "Sun, 25 Jan 2026"
    - th.drawNumber: "Draw No. 5436"
    - td.tdFirstPrize: "4025"
    - td.tdSecondPrize: "3634"
    - td.tdThirdPrize: "3473"
    - tbody.tbodyStarterPrizes: contains starter numbers
    - tbody.tbodyConsolationPrizes: contains consolation numbers
    """
    result = {}
    
    # Find draw date
    draw_date_elem = table.find("th", class_="drawDate")
    if draw_date_elem:
        date_text = draw_date_elem.get_text().strip()
        result["draw_date"] = parse_date(date_text)
    
    # Find draw number
    draw_number_elem = table.find("th", class_="drawNumber")
    if draw_number_elem:
        text = draw_number_elem.get_text().strip()
        # Extract the number from "Draw No. 5436"
        match = re.search(r"(\d+)", text)
        if match:
            result["draw_number"] = match.group(1)
    
    # Find main prizes
    first_prize = table.find("td", class_="tdFirstPrize")
    second_prize = table.find("td", class_="tdSecondPrize")
    third_prize = table.find("td", class_="tdThirdPrize")
    
    if first_prize:
        result["first_prize"] = first_prize.get_text().strip()
    if second_prize:
        result["second_prize"] = second_prize.get_text().strip()
    if third_prize:
        result["third_prize"] = third_prize.get_text().strip()
    
    # Find starter prizes - look in the same container/parent
    parent = table.parent
    starters = []
    starter_tbody = parent.find("tbody", class_="tbodyStarterPrizes") if parent else None
    if starter_tbody:
        for td in starter_tbody.find_all("td"):
            text = td.get_text().strip()
            if re.match(r"^\d{4}$", text):
                starters.append(text)
    
    # Find consolation prizes
    consolation = []
    consolation_tbody = parent.find("tbody", class_="tbodyConsolationPrizes") if parent else None
    if consolation_tbody:
        for td in consolation_tbody.find_all("td"):
            text = td.get_text().strip()
            if re.match(r"^\d{4}$", text):
                consolation.append(text)
    
    result["starters"] = starters[:10]
    result["consolation"] = consolation[:10]
    
    # Validate we have minimum required data
    if result.get("first_prize") and result.get("draw_number"):
        return result
    return None


def parse_alternative_layout(soup) -> list[dict]:
    """Parse using alternative page layout (card-based)."""
    results = []
    
    # Look for draw cards or containers
    draw_containers = soup.find_all("div", class_=re.compile(r"(draw|result|table)", re.I))
    
    for container in draw_containers:
        result = {}
        text = container.get_text()
        
        # Extract draw number
        draw_match = re.search(r"Draw\s*(?:No\.?)?\s*(\d+)", text, re.I)
        if draw_match:
            result["draw_number"] = draw_match.group(1)
        
        # Extract date
        date_match = re.search(r"(\d{1,2})\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*(\d{4})", text, re.I)
        if date_match:
            result["draw_date"] = parse_date(date_match.group(0))
        
        # Find prize numbers - look for labeled sections
        first_match = re.search(r"1st\s*Prize[:\s]*(\d{4})", text, re.I)
        second_match = re.search(r"2nd\s*Prize[:\s]*(\d{4})", text, re.I)
        third_match = re.search(r"3rd\s*Prize[:\s]*(\d{4})", text, re.I)
        
        if first_match:
            result["first_prize"] = first_match.group(1)
        if second_match:
            result["second_prize"] = second_match.group(1)
        if third_match:
            result["third_prize"] = third_match.group(1)
        
        # Extract starters and consolation
        starter_match = re.search(r"Starter\s*(?:Prizes?)?[:\s]*((?:\d{4}[\s,]*)+)", text, re.I)
        consolation_match = re.search(r"Consolation\s*(?:Prizes?)?[:\s]*((?:\d{4}[\s,]*)+)", text, re.I)
        
        if starter_match:
            result["starters"] = re.findall(r"\d{4}", starter_match.group(1))[:10]
        else:
            result["starters"] = []
            
        if consolation_match:
            result["consolation"] = re.findall(r"\d{4}", consolation_match.group(1))[:10]
        else:
            result["consolation"] = []
        
        if result.get("first_prize") and result.get("draw_number"):
            results.append(result)
    
    return results


def parse_date(date_str: str) -> str:
    """Convert date string to YYYY-MM-DD format."""
    months = {
        "jan": "01", "feb": "02", "mar": "03", "apr": "04",
        "may": "05", "jun": "06", "jul": "07", "aug": "08",
        "sep": "09", "oct": "10", "nov": "11", "dec": "12"
    }
    
    match = re.search(r"(\d{1,2})\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*(\d{4})", date_str, re.I)
    if match:
        day = match.group(1).zfill(2)
        month = months.get(match.group(2).lower(), "01")
        year = match.group(3)
        return f"{year}-{month}-{day}"
    return date_str


def scrape_all_draws(driver: webdriver.Chrome, db: Database, limit: int | None = None) -> dict:
    """
    Scrape all available 4D draws.
    
    Args:
        driver: Selenium WebDriver
        db: Database instance
        limit: Optional limit on number of draws to scrape
        
    Returns:
        Summary statistics dict
    """
    print("🎲 Starting 4D results scraper...")
    print(f"   URL: {URL_4D_RESULTS}")
    
    # Navigate to results page
    driver.get(URL_4D_RESULTS)
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
            
            time.sleep(DELAY_BETWEEN_DRAWS)  # Wait for content to load
            
            # Parse results
            results = parse_4d_results(driver)
            
            for result in results:
                if all(k in result for k in ["draw_number", "draw_date", "first_prize"]):
                    inserted = db.insert_4d_draw(
                        draw_number=result["draw_number"],
                        draw_date=result.get("draw_date", ""),
                        first=result["first_prize"],
                        second=result.get("second_prize", ""),
                        third=result.get("third_prize", ""),
                        starters=result.get("starters", []),
                        consolation=result.get("consolation", [])
                    )
                    
                    if inserted:
                        stats["inserted"] += 1
                    else:
                        stats["duplicates"] += 1
            
            stats["processed"] += 1
            
            # Progress update
            if (i + 1) % 10 == 0:
                print(f"   Progress: {i + 1}/{len(draw_options)} draws processed")
                
        except Exception as e:
            print(f"   ⚠ Error processing draw {option['text']}: {e}")
            stats["errors"] += 1
            continue
    
    return stats


def main(headless: bool = True, limit: int | None = None) -> dict:
    """
    Main execution function.
    
    Args:
        headless: Run browser in headless mode
        limit: Limit number of draws to scrape
        
    Returns:
        Execution results dict
    """
    driver = None
    
    try:
        driver = setup_driver(headless=headless)
        
        with Database() as db:
            initial_count = db.get_4d_draws_count()
            print(f"   Initial DB count: {initial_count} draws")
            
            stats = scrape_all_draws(driver, db, limit=limit)
            
            final_count = db.get_4d_draws_count()
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
    parser = argparse.ArgumentParser(description="Scrape Singapore Pools 4D results")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of draws to scrape")
    parser.add_argument("--headless", action="store_true", default=True, help="Run browser in headless mode")
    parser.add_argument("--visible", action="store_true", help="Show browser window (not headless)")
    parser.add_argument("--output", default=".tmp/scrape_4d_results.json", help="Output file path")
    
    args = parser.parse_args()
    
    # Ensure .tmp directory exists
    Path(".tmp").mkdir(exist_ok=True)
    
    # Execute
    headless = not args.visible
    result = main(headless=headless, limit=args.limit)
    
    # Write output
    with open(args.output, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"\n📄 Output written to {args.output}")
    sys.exit(0 if result["status"] == "success" else 1)
