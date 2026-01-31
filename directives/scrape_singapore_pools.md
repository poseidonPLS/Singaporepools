# Scrape Singapore Pools Data

## Purpose
Collect 3 years of historical data from Singapore Pools for 4D and Toto analysis.

## Prerequisites
- Python 3.10+
- Chrome browser installed
- Dependencies installed: `pip install -r requirements.txt`

## Running the Scrapers

### 4D Results
```bash
cd /Users/don/Desktop/Singaporepools

# Scrape all available 4D draws (headless)
python execution/scrape_4d.py

# Scrape with visible browser (for debugging)
python execution/scrape_4d.py --visible

# Limit to first 50 draws
python execution/scrape_4d.py --limit 50
```

### Toto Results  
```bash
# Scrape all available Toto draws
python execution/scrape_toto.py

# With visible browser
python execution/scrape_toto.py --visible

# Limit draws
python execution/scrape_toto.py --limit 50
```

## Rate Limiting
- Default delay: 0.5 seconds between requests
- Be respectful of Singapore Pools servers

## Data Storage
Results are stored in `.tmp/singapore_pools.db` (SQLite)

## Error Handling
- Duplicate draws are automatically skipped
- Failed draws are logged but don't stop scraping
- Output JSON written to `.tmp/scrape_*_results.json`

## Edge Cases
- Website structure may change — update selectors in scrapers
- Draw dropdowns may be paginated — handle pagination if needed
