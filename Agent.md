# Agent Instructions

> This file is mirrored across `CLAUDE.md`, `AGENTS.md`, and `GEMINI.md` so the same instructions load in any AI environment.

---

## Architecture Overview

This is a **Hybrid Cloud System** for Singapore Pools lottery analysis. Heavy automation runs on GitHub Actions (x64), while the Oracle Cloud server (ARM64) only serves the frontend and API.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        GITHUB ACTIONS (x64)                              │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐                 │
│  │ scrape_4d.py │   │scrape_toto.py│   │ai_predictor.py│                │
│  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘                 │
│         └──────────────────┼──────────────────┘                         │
│                            ▼                                             │
│                    .tmp/singapore_pools.db                               │
│                    .tmp/ai_predictions.json                              │
│                            │ SCP                                         │
└────────────────────────────┼────────────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     ORACLE CLOUD (ARM64)                                 │
│                   https://singaporepools.win                             │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                        server.py (:8080)                          │   │
│  │  /api/4d  /api/toto  /api/analysis/4d  /api/predictions          │   │
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
│   └── daily-scraper.yml    # Automation: scrape + predict + deploy
├── .tmp/                     # DATA (synced between GHA ↔ Oracle)
│   ├── singapore_pools.db   # SQLite database (4D + Toto draws)
│   └── ai_predictions.json  # Cached AI predictions
├── app/                      # FRONTEND (served by server.py)
│   ├── index.html
│   ├── scripts/
│   │   ├── api.js           # Backend communication
│   │   ├── main.js          # Core UI logic
│   │   ├── charts.js        # Chart rendering
│   │   ├── predictions.js   # AI prediction display
│   │   └── translations.js  # i18n (EN/CN)
│   └── styles/main.css
├── execution/                # PYTHON BACKEND
│   ├── server.py            # REST API (runs on Oracle)
│   ├── database.py          # SQLite ORM
│   ├── scrape_4d.py         # Selenium scraper (runs on GHA)
│   ├── scrape_toto.py       # Selenium scraper (runs on GHA)
│   ├── ai_predictor.py      # Gemini API predictions (runs on GHA)
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
| `/api/predictions` | GET | Cached AI predictions |
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
| `GOOGLE_API_KEY` | Gemini API key |

**Flow:**
1. Checkout code
2. Install Chrome + Python deps
3. **Download** existing DB from Oracle via SCP
4. Run scrapers (`--limit 5`)
5. Generate AI predictions
6. **Upload** updated DB + predictions back to Oracle

---

## Common Commands

### Run Server Locally
```bash
python execution/server.py --port 8080
```

### Trigger Manual Scrape
Go to GitHub → Actions → "Daily Scraper & AI Prediction" → Run workflow

### Backfill Missing Draws
```bash
# Temporarily increase limit in workflow, or run multiple times
python execution/scrape_4d.py --limit 20
python execution/scrape_toto.py --limit 20
```

### Deploy Code Changes
```bash
git add . && git commit -m "feat: description" && git push
ssh oracle "cd Singaporepools && git pull && systemctl restart singaporepools"
```

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

## Version History

| Date | Change |
|------|--------|
| Feb 2026 | Fixed GHA workflow: Chrome install, direct SCP, file verification |
| Jan 2026 | Migrated scrapers to GHA, added AI predictions, relative API paths |
