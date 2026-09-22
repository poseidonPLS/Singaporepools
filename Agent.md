# Agent Instructions

> This file is mirrored across `CLAUDE.md`, `AGENTS.md`, and `GEMINI.md` so the same instructions load in any AI environment.

---

## Architecture Overview

Everything runs on **racknerd2** (x64) since 2026-09-22: a systemd timer scrapes new draws into
SQLite, and `server.py` serves the API and the static frontend at https://singaporepools.win
(Cloudflare-proxied, nginx in front).

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          RACKNERD2 (x64)                                │
│                                                                         │
│  sites-sp-scrape.timer → run_scrape.sh                                  │
│      scrape_4d.py + scrape_toto.py (Selenium, Google Chrome deb)        │
│                            │                                            │
│                            ▼                                            │
│                    .tmp/singapore_pools.db                              │
│                            │                                            │
│  sites-singaporepools.service                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                  server.py (127.0.0.1:8080)                      │   │
│  │  /api/4d  /api/toto  /api/analysis/4d  /api/analysis/toto        │   │
│  │  app/ (static): index.html → main.js, api.js, charts.js, ...     │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                            ▲                                            │
│              nginx ← Cloudflare ← https://singaporepools.win            │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
Singaporepools/
├── .tmp/                     # DATA (lives on the server; never deployed)
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
│   ├── server.py            # REST API + static frontend
│   ├── database.py          # SQLite ORM
│   ├── scrape_4d.py         # Selenium scraper (run by the server timer)
│   ├── scrape_toto.py       # Selenium scraper (run by the server timer)
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

## Scheduled Scraping

**Timer:** `sites-sp-scrape.timer` → `sites-sp-scrape.service` on racknerd2, running
`/home/sites/Singaporepools/run_scrape.sh` (server-side, not in this repo).

**Schedule (SGT):**
- **4D**: Wed, Sat, Sun @ 7:15 PM
- **Toto**: Mon, Thu @ 10:15 PM

Scrapers run with `--limit 5` against the live DB; duplicates are skipped. The old GitHub
Actions workflow (scrape on GHA, SCP the DB to Oracle) was deleted in v1.1.1.

---

## Common Commands

### Run Server Locally
```bash
python execution/server.py --port 8080
```

### Trigger Manual Scrape
```bash
ssh -t racknerd2 'sudo systemctl start sites-sp-scrape.service'   # needs Don's sudo
```

### Backfill Missing Draws
```bash
# Run on the server as `sites`, or trigger the timer's service several times
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

### Scraper Fails on racknerd2
- Check the service log: `journalctl -u sites-sp-scrape.service` (on racknerd2)
- Chrome must be the **Google Chrome deb**, never the Chromium snap — snap confinement fails on
  that box, and the scrapers prefer `/snap/bin/chromium` if it exists.

### Missing Draws After Outage
- Trigger a manual scrape 2-3× (deduplication handles overlap)
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

1. **Never deploy or scrape on Oracle** — it hosts unrelated A-Tec production now
2. **Never hardcode localhost** — Frontend uses relative `/api/` paths
3. **Never overwrite the server's `.tmp/` DB** — it is the only copy of the scraped history
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
| Sep 2026 | v1.1.1 — Deleted the obsolete GitHub Actions scraper; docs now describe the racknerd2 timer + `deploy-site`. |
| Sep 2026 | v1.1.0 — Removed Gemini AI prediction entirely (button, API route, scheduler hook, `ai_predictor.py`); site uses its six local strategies only. |
| Feb 2026 | Replaced AI predictions endpoint with local generation logic; Migrated to PM2 deploying. |
| Feb 2026 | Fixed GHA workflow: Chrome install, direct SCP, file verification |
| Jan 2026 | Migrated scrapers to GHA, added AI predictions, relative API paths |
