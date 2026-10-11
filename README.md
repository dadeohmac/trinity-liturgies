# Trinity Liturgies

An unofficial phone-friendly viewer for the live stream and archived liturgies of [Trinity Episcopal Church on Capitol Square](https://www.trinitycolumbus.org), Columbus, Ohio. All videos belong to the church; this app only links to them.

**Open it:** https://dadeohmac.github.io/trinity-liturgies/. On iPhone, open it in Safari and tap Share → Add to Home Screen.

## How it works

- `index.html` is the whole app: it shows the Sunday 10:30 live stream card, the newest recording, and every archived service grouped by church year. Videos play inside the app and remember where you stopped (kept per device in browser storage).
- `services.json` is the service list. `scripts/scrape.py` (Python stdlib only) builds it from the church's [archive page](https://www.trinitycolumbus.org/archive-of-live-stream-liturgies) and [live stream page](https://www.trinitycolumbus.org/live-stream-liturgy). It converts Dropbox share links into direct-play links and refuses to write if it parses fewer than 10 services.
- `.github/workflows/refresh.yml` runs the scraper every Monday and Thursday and commits `services.json` when it changes. Run it by hand from the Actions tab ("Refresh archive" → Run workflow), or locally with `python3 scripts/scrape.py`.
