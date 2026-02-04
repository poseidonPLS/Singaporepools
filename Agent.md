# Agent Instructions

> This file is mirrored across CLAUDE.md, AGENTS.md, and GEMINI.md so the same instructions load in any AI environment.

You operate within a **Hybrid Cloud Architecture** designed to circumvent ARM64 limitations on the Oracle Cloud Free Tier.

## The Hybrid Architecture

**1. Hosted Application (Oracle Cloud - ARM64)**
- **Role**: Serves the Frontend and API.
- **OS**: Ubuntu 24.04 (ARM64).
- **Files**: `execution/server.py`, `app/`, `.tmp/singapore_pools.db`.
- **Constraint**: Cannot run Selenium/Chromium reliably due to Snap/ARM64 sandbox issues.
- **Address**: `https://singaporepools.win`

**2. Automation & Scraping (GitHub Actions - x64)**
- **Role**: Runs heavy automation (Scraping + AI Prediction).
- **OS**: Ubuntu Latest (x64).
- **Workflow**: `.github/workflows/daily-scraper.yml`.
- **Process**:
    1.  Downloads DB from Oracle Server (to preserve history).
    2.  Scrapes new data (Selenium).
    3.  Generates AI Predictions (Gemini API).
    4.  Uploads updated DB + Predictions back to Oracle Server via SCP.

## Operating Principles

**1. "Set it and Forget it" Automation**
- Do NOT run scrapers manually on the server. They will fail.
- Automation is handled exclusively by **GitHub Actions**.
- Schedule:
    - **4D**: Wed, Sat, Sun @ 7:15 PM SGT.
    - **Toto**: Mon, Thu @ 10:15 PM SGT.

**2. Deterministic AI Layer**
- AI Predictions are **pre-computed** during the GitHub Action run.
- The Server (`server.py`) simply serves the cached `.tmp/ai_predictions.json`.
- This saves API tokens and ensures instant response times for users.

**3. Frontend Logic**
- The frontend (`api.js`) must use **relative paths** (`/api/...`) to function correctly in production.
- Never hardcode `localhost:8080`.

## File Organization

- `.tmp/` - **The Source of Truth**. Contains the SQLite DB and Predictions JSON. Synced between GHA and Server.
- `execution/` - Python scripts.
    - `server.py`: Runs on Oracle.
    - `scrape_*.py` & `ai_predictor.py`: Run on GitHub Actions.
- `.github/workflows/` - The automation logic.
- `app/` - Static frontend files.

## Common Execution Commands

**1. Run the API Server (Oracle Cloud)**
```bash
# SSH into correct server
# Run the server (usually running via systemd or screen)
python3 execution/server.py
```

**2. Trigger Manual Scrape/Update**
- Go to GitHub Repository -> **Actions** tab.
- Select **"Daily Scraper & AI Prediction"**.
- Click **"Run workflow"**.
- *This will scrape, predict, and auto-deploy the data to the live server.*

**3. Deploy Code Changes**
```bash
git add .
git commit -m "feat: description"
git push origin main
# Then pull on server
ssh oracle "cd Singaporepools && git pull && python3 execution/server.py"
```

## System History & Audit

### Feb 2026
- **GHA Workflow Fix**: Resolved `tar: Cowardly refusing to create an empty archive` error.
  - **Root Cause**: `appleboy/scp-action` requires files to exist; Selenium was failing silently due to missing Chrome.
  - **Fix**: Added explicit Chrome installation via `browser-actions/setup-chrome@v1`, replaced scp-action with direct SCP commands, added file verification step before upload.
- **Backfill Gaps**: If scheduled runs fail, manually trigger the workflow 2-3 times to catch up. The scraper deduplicates via `draw_number` unique constraint.

### Jan 2026
- **Migration to GitHub Actions**: Moved all scraping logic off the ARM64 server to GHA to fix `SessionNotCreatedException` errors.
- **Frontend API Fix**: Switched `api.js` to relative paths to fix Mixed Content errors on `singaporepools.win`.
- **Database Persistence**: Updated GHA workflow to *download* the existing DB before scraping to prevent overwriting history.
- **AI Integration**: Configured Gemini API key in GitHub Secrets for automated prediction generation.

## Troubleshooting

**GHA Workflow Fails with Empty Archive:**
1. Check if Chrome is installed (`browser-actions/setup-chrome@v1`).
2. Verify `.tmp/` contains files after scraper step (debug output shows this).
3. Ensure `ORACLE_SSH_KEY` and `ORACLE_HOST` secrets are set.

**Missing Draws After Outage:**
- Run workflow manually 2-3 times with `--limit 5`, or temporarily set `--limit 20` for one-shot backfill.
- Duplicates are automatically skipped.

## Summary

You manage a distributed system. **Logic lives on GitHub Actions, Presentation lives on Oracle.** Always respect this separation of concerns.
