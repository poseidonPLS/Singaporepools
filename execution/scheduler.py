#!/usr/bin/env python3
"""
Script: scheduler.py
Version: 1.0.0
Purpose: Auto-schedule data scraping after lottery draws

Parses "Next Draw" time from Singapore Pools and schedules scraping
30 minutes after each draw to allow results to be posted.

Usage:
    python3 execution/scheduler.py         # Run scheduler
    python3 execution/scheduler.py --once  # Check once and exit
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# =============================================================================
# CONFIGURATION
# =============================================================================

URL_4D = "https://www.singaporepools.com.sg/en/product/Pages/4d_results.aspx"
URL_TOTO = "https://www.singaporepools.com.sg/en/product/Pages/toto_results.aspx"
DELAY_AFTER_DRAW = 30  # Minutes to wait after draw before scraping
CHECK_INTERVAL = 300  # Seconds between schedule checks (5 min)


# =============================================================================
# NEXT DRAW PARSER
# =============================================================================

def setup_driver():
    """Set up headless Chrome."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def parse_next_draw_time(html: str, game: str) -> datetime | None:
    """
    Parse the next draw date/time from page HTML.
    
    4D format: "Wed, 28 Jan 2026, 6.30pm"
    Toto format: "Next Draw Thu, 29 Jan 2026 , 9.30pm" (may be split across lines)
    """
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()
    
    # Remove extra whitespace and normalize  
    text = " ".join(text.split())
    
    # Pattern 1: Standard format - "Next Draw Wed, 28 Jan 2026, 6.30pm"
    pattern1 = r"Next\s*Draw\s*([A-Za-z]{3}),?\s*(\d{1,2})\s*([A-Za-z]{3})\s*(\d{4})\s*,?\s*(\d{1,2})\.(\d{2})\s*(am|pm)"
    match = re.search(pattern1, text, re.I)
    
    # Pattern 2: Toto format where date and time might be separate
    if not match:
        pattern2 = r"Next\s*Draw\s*([A-Za-z]{3}),?\s*(\d{1,2})\s*([A-Za-z]{3})\s*(\d{4})"
        time_pattern = r"(\d{1,2})\.(\d{2})\s*(am|pm)"
        
        date_match = re.search(pattern2, text, re.I)
        time_match = re.search(time_pattern, text[text.find("Next Draw"):] if "Next Draw" in text else text, re.I)
        
        if date_match and time_match:
            match = type('Match', (), {
                'groups': lambda: (
                    date_match.group(1), date_match.group(2), date_match.group(3), date_match.group(4),
                    time_match.group(1), time_match.group(2), time_match.group(3)
                )
            })()
    
    if match:
        groups = match.groups()
        _, day, month, year, hour, minute, ampm = groups
        
        months = {
            "jan": 1, "feb": 2, "mar": 3, "apr": 4,
            "may": 5, "jun": 6, "jul": 7, "aug": 8,
            "sep": 9, "oct": 10, "nov": 11, "dec": 12
        }
        
        hour = int(hour)
        if ampm.lower() == "pm" and hour != 12:
            hour += 12
        elif ampm.lower() == "am" and hour == 12:
            hour = 0
        
        try:
            return datetime(
                year=int(year),
                month=months.get(month.lower(), 1),
                day=int(day),
                hour=hour,
                minute=int(minute)
            )
        except ValueError:
            return None
    
    return None



def get_next_draw_times() -> dict:
    """Fetch next draw times for both 4D and Toto."""
    driver = None
    results = {"4d": None, "toto": None}
    
    try:
        driver = setup_driver()
        
        # Get 4D next draw
        print("   Checking 4D next draw time...")
        driver.get(URL_4D)
        time.sleep(2)
        results["4d"] = parse_next_draw_time(driver.page_source, "4d")
        
        # Get Toto next draw
        print("   Checking Toto next draw time...")
        driver.get(URL_TOTO)
        time.sleep(2)
        results["toto"] = parse_next_draw_time(driver.page_source, "toto")
        
    except Exception as e:
        print(f"   ⚠ Error fetching draw times: {e}")
    finally:
        if driver:
            driver.quit()
    
    return results


# =============================================================================
# SCHEDULER
# =============================================================================

def run_scraper(game: str):
    """Run the appropriate scraper and then generate AI predictions."""
    script = f"execution/scrape_{game}.py"
    
    print(f"\n🔄 Running {game.upper()} scraper...")
    
    # Import and run directly
    if game == "4d":
        from execution.scrape_4d import main as scrape_4d
        scrape_4d(headless=True, limit=5)  # Only get recent draws
    elif game == "toto":
        from execution.scrape_toto import main as scrape_toto
        scrape_toto(headless=True, limit=5)
    
    # Run AI prediction after scraping
    print(f"\n🤖 Generating AI prediction for {game.upper()}...")
    try:
        from execution.ai_predictor import generate_prediction
        generate_prediction(game)
    except Exception as e:
        print(f"   ⚠ AI prediction failed: {e}")


def calculate_scrape_time(draw_time: datetime) -> datetime:
    """Calculate when to scrape (draw time + delay)."""
    return draw_time + timedelta(minutes=DELAY_AFTER_DRAW)


def scheduler_loop():
    """Main scheduler loop."""
    print("🕐 Singapore Pools Auto-Update Scheduler")
    print(f"   Will scrape {DELAY_AFTER_DRAW} minutes after each draw")
    print(f"   Checking every {CHECK_INTERVAL // 60} minutes")
    print("   Press Ctrl+C to stop")
    print()
    
    last_4d_scrape = None
    last_toto_scrape = None
    
    while True:
        try:
            now = datetime.now()
            print(f"\n⏰ [{now.strftime('%Y-%m-%d %H:%M')}] Checking schedule...")
            
            # Get next draw times
            draw_times = get_next_draw_times()
            
            for game, draw_time in draw_times.items():
                if draw_time is None:
                    print(f"   {game.upper()}: Could not parse next draw time")
                    continue
                
                scrape_time = calculate_scrape_time(draw_time)
                last_scrape = last_4d_scrape if game == "4d" else last_toto_scrape
                
                print(f"   {game.upper()}: Next draw {draw_time.strftime('%Y-%m-%d %H:%M')}")
                print(f"         Scrape at {scrape_time.strftime('%Y-%m-%d %H:%M')}")
                
                # Check if we should scrape now
                if now >= scrape_time:
                    # Only scrape if we haven't already for this draw
                    if last_scrape is None or last_scrape < draw_time:
                        run_scraper(game)
                        
                        if game == "4d":
                            last_4d_scrape = now
                        else:
                            last_toto_scrape = now
                        
                        print(f"   ✅ {game.upper()} data updated!")
                    else:
                        now_str = now.strftime('%H:%M')
                        print(f"   {game.upper()}: Already scraped for this draw")
                else:
                    wait_mins = (scrape_time - now).total_seconds() / 60
                    print(f"   {game.upper()}: Waiting {wait_mins:.0f} minutes")
            
            # Wait before next check
            print(f"\n   Sleeping for {CHECK_INTERVAL // 60} minutes...")
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n\n👋 Scheduler stopped")
            break
        except Exception as e:
            print(f"\n⚠ Error: {e}")
            print(f"   Retrying in {CHECK_INTERVAL // 60} minutes...")
            time.sleep(CHECK_INTERVAL)


def check_once():
    """Check draw times once and print schedule."""
    print("🕐 Singapore Pools Draw Schedule")
    print()
    
    draw_times = get_next_draw_times()
    now = datetime.now()
    
    print(f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    for game, draw_time in draw_times.items():
        if draw_time:
            scrape_time = calculate_scrape_time(draw_time)
            status = "✅ Ready" if now >= scrape_time else f"⏳ In {(scrape_time - now).total_seconds() / 60:.0f} min"
            
            print(f"{game.upper()}:")
            print(f"  Next Draw:   {draw_time.strftime('%a, %d %b %Y, %I.%M%p')}")
            print(f"  Scrape Time: {scrape_time.strftime('%Y-%m-%d %H:%M')}")
            print(f"  Status:      {status}")
            print()
        else:
            print(f"{game.upper()}: Could not parse next draw time")
            print()


# =============================================================================
# ENTRYPOINT
# =============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto-update scheduler for Singapore Pools data")
    parser.add_argument("--once", action="store_true", help="Check schedule once and exit")
    parser.add_argument("--delay", type=int, default=DELAY_AFTER_DRAW, 
                        help=f"Minutes to wait after draw (default: {DELAY_AFTER_DRAW})")
    
    args = parser.parse_args()
    DELAY_AFTER_DRAW = args.delay
    
    if args.once:
        check_once()
    else:
        scheduler_loop()
