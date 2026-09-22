# Agent Instructions

> This file is mirrored across `CLAUDE.md`, `AGENTS.md`, and `GEMINI.md` so the same instructions load in any AI environment.

---

## Architecture Overview

This is a **Hybrid Cloud System** for Singapore Pools lottery analysis. Heavy automation runs on GitHub Actions (x64), while the Oracle Cloud server (ARM64) only serves the frontend and API.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        GITHUB ACTIONS (x64)                              │
│           ┌──────────────┐   ┌──────────────┐                            │
│           │ scrape_4d.py │   │scrape_toto.py│                            │
│           └──────┬───────┘   └──────┬───────┘                            │
│                  └────────┬─────────┘                                    │
│                            ▼                                             │
│                    .tmp/singapore_pools.db                               │
│                            │ SCP                                         │
└────────────────────────────┼────────────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     ORACLE CLOUD (ARM64)                                 │
│                   https://singaporepools.win                             │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                        server.py (:8080)                          │   │
│  │  /api/4d  /api/toto  /api/analysis/4d  /api/analysis/toto        │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                        app/ (Static)                              │   │
│  │  index.html → main.js, api.js, charts.js, predictions.js         │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
Singaporepools/
├── .github/workflows/
│   └── daily-scraper.yml    # Automation: scrape + upload DB
├── .tmp/                     # DATA (synced between GHA ↔ Oracle)
│   └── singapore_pools.db   # SQLite database (4D + Toto draws)
├── app/                      # FRONTEND (served by server.py)
│   ├── index.html
│   ├── scripts/
│   │   ├── api.js           # Backend communication
│   │   ├── main.js          # Core UI logic
│   │   ├── charts.js        # Chart rendering
│   │   ├── predictions.js   # Local number-generation strategies
│   │   └── translations.js  # i18n (EN/CN)
│   └── styles/main.css
├── execution/                # PYTHON BACKEND
│   ├── server.py            # REST API (runs on Oracle)
│   ├── database.py          # SQLite ORM
│   ├── scrape_4d.py         # Selenium scraper (runs on GHA)
│   ├── scrape_toto.py       # Selenium scraper (runs on GHA)
│   └── analysis/            # Statistical analysis modules
├── requirements.txt          # Python dependencies
└── .env.example              # Environment variable template
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/4d` | GET | All 4D draw results (JSON array) |
| `/api/toto` | GET | All Toto draw results (JSON array) |
| `/api/analysis/4d` | GET | 4D statistical analysis |
| `/api/analysis/toto` | GET | Toto frequency/gap analysis |
| `/*` | GET | Static files from `app/` |

**Frontend Note:** `api.js` uses **relative paths** (`/api/...`). Never hardcode `localhost:8080`.

---

## Database Schema

**SQLite:** `.tmp/singapore_pools.db`

```sql
-- 4D Draws
CREATE TABLE draws_4d (
    id INTEGER PRIMARY KEY,
    draw_number TEXT UNIQUE NOT NULL,
    draw_date DATE NOT NULL,
    first_prize TEXT NOT NULL,
    second_prize TEXT NOT NULL,
    third_prize TEXT NOT NULL,
    starters TEXT NOT NULL,      -- JSON array
    consolation TEXT NOT NULL    -- JSON array
);

-- Toto Draws
CREATE TABLE draws_toto (
    id INTEGER PRIMARY KEY,
    draw_number TEXT UNIQUE NOT NULL,
    draw_date DATE NOT NULL,
    winning_numbers TEXT NOT NULL, -- JSON array [6 numbers]
    additional_number INTEGER NOT NULL,
    prize_pool TEXT               -- JSON (optional)
);
```

**Deduplication:** `draw_number` is unique. Re-scraping skips duplicates automatically.

---

## GitHub Actions Workflow

**File:** `.github/workflows/daily-scraper.yml`

**Schedule:**
- **4D**: Wed, Sat, Sun @ 7:15 PM SGT (`15 11 * * 0,3,6` UTC)
- **Toto**: Mon, Thu @ 10:15 PM SGT (`15 14 * * 1,4` UTC)

**Secrets Required:**
| Secret | Description |
|--------|-------------|
| `ORACLE_HOST` | Server IP/hostname |
| `ORACLE_SSH_KEY` | Private SSH key (PEM format) |

**Flow:**
1. Checkout code
2. Install Chrome + Python deps
3. **Download** existing DB from Oracle via SCP
4. Run scrapers (`--limit 5`)
5. **Upload** updated DB back to Oracle

---

## Common Commands

### Run Server Locally
```bash
python execution/server.py --port 8080
```

### Trigger Manual Scrape
Go to GitHub → Actions → "Daily Scraper" → Run workflow

### Backfill Missing Draws
```bash
# Temporarily increase limit in workflow, or run multiple times
python execution/scrape_4d.py --limit 20
python execution/scrape_toto.py --limit 20
```

### Deploy Code Changes
```bash
# 1. Push to GitHub main
git push origin main
# 2. Deploy on racknerd2 (needs Don's sudo) — pulls origin/main, restarts, health-checks
ssh -t racknerd2 'sudo deploy-site singaporepools'
# Roll back: ssh -t racknerd2 'sudo deploy-site singaporepools --rollback'
```
Production runs on **racknerd2** as `sites-singaporepools.service` (since 2026-09-22). The old
`ssh oracle` + pm2 recipe is dead — Oracle now hosts unrelated production, never deploy there.

---

## Troubleshooting

### GHA Fails with "empty archive"
- **Cause:** Scrapers failed, no files created
- **Fix:** Chrome installation added via `browser-actions/setup-chrome@v1`
- **Debug:** Check "Run Scrapers" step output for errors

### Missing Draws After Outage
- Run workflow manually 2-3× (deduplication handles overlap)
- Or temporarily set `--limit 20` for one-shot backfill

### Frontend Not Updating
- Browser cache. Hard refresh: `Cmd+Shift+R`
- Verify API returns data: `curl https://singaporepools.win/api/4d`

### Scraper CSS Selectors
The scrapers rely on these Singapore Pools classes:
- `.selectDrawList` — Date dropdown
- `.drawDate`, `.drawNumber` — Draw metadata
- `.tdFirstPrize`, `.tdSecondPrize`, `.tdThirdPrize` — Main prizes
- Tables with "Starter Prizes" / "Consolation Prizes" headers

If scraping breaks, verify these selectors haven't changed.

---

## Key Constraints

1. **Never run scrapers on Oracle** — ARM64 + Snap sandbox = Selenium crash
2. **Never hardcode localhost** — Frontend uses relative `/api/` paths
3. **Always download DB before scraping** — Preserves historical data
4. **Scrapers are idempotent** — Safe to re-run; duplicates skipped

---

## Versioning Standards
Always update the numbers for version `X.Y.Z` on every update when generating or updating files:
- **X**: Major change of the project structure or capabilities.
- **Y**: Minor feature upgrade.
- **Z**: Bug fixes, text updates, or minor tweaks.

---

## Version History

| Date | Change |
|------|--------|
| Sep 2026 | v1.1.0 — Removed Gemini AI prediction entirely (button, API route, scheduler hook, `ai_predictor.py`); site uses its six local strategies only. |
| Feb 2026 | Replaced AI predictions endpoint with local generation logic; Migrated to PM2 deploying. |
| Feb 2026 | Fixed GHA workflow: Chrome install, direct SCP, file verification |
| Jan 2026 | Migrated scrapers to GHA, added AI predictions, relative API paths |
