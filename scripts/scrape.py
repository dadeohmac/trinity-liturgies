#!/usr/bin/env python3
"""Rebuild services.json from Trinity Columbus's public live-stream pages.

Stdlib only, so it runs as-is in GitHub Actions. Writes nothing if the
archive page can't be parsed, so a site redesign never empties the app.
"""
import datetime
import html
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ARCHIVE = "https://www.trinitycolumbus.org/archive-of-live-stream-liturgies"
LIVE = "https://www.trinitycolumbus.org/live-stream-liturgy"
OUT = Path(__file__).resolve().parent.parent / "services.json"
MONTHS = {m: i for i, m in enumerate(
    "january february march april may june july august september october november december".split(), 1)}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (trinity-liturgies app)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def text_date(t):
    """'September 6, 2026 - …' -> date; tolerates typos like 'ebruary' or '20206'."""
    m = re.match(r"\s*([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4,5})", t)
    if not m:
        return None
    word = m.group(1).lower()
    mo = MONTHS.get(word) or next((v for k, v in MONTHS.items() if k.endswith(word) and len(word) >= 4), None)
    yr = m.group(3)
    yr = int(yr[:2] + yr[-2:]) if len(yr) == 5 else int(yr)
    try:
        return datetime.date(yr, mo, int(m.group(2))) if mo else None
    except ValueError:
        return None


def file_date(url):
    """Dropbox filenames start with YYMMDD, e.g. 260906-Pentecost-15.mp4."""
    m = re.search(r"/(\d{2})(\d{2})(\d{2})[^/]*\.(?:mp4|mov|m4v)", url, flags=re.I)
    if not m:
        return None
    try:
        return datetime.date(2000 + int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def direct(url):
    """Dropbox share link -> direct-play link (raw=1, no session token)."""
    p = urllib.parse.urlsplit(url)
    q = [(k, v) for k, v in urllib.parse.parse_qsl(p.query) if k not in ("st", "dl", "raw")] + [("raw", "1")]
    return urllib.parse.urlunsplit((p.scheme, p.netloc, p.path, urllib.parse.urlencode(q), ""))


def archive():
    page = get(ARCHIVE)
    services, unavailable = [], []
    # Each entry is a <p> holding the date/title text, linked when a video exists.
    for p in re.findall(r"<p[^>]*>(.*?)</p>", page, flags=re.S):
        text = html.unescape(re.sub(r"<[^>]+>", "", p)).strip()
        if not re.match(r"[A-Za-z]+\s+\d{1,2},?\s+\d{4}", text):
            continue
        title = text.split(" - ", 1)[1].strip() if " - " in text else text
        # Tolerates junk before the URL inside href and .mov/.m4v files.
        link = re.search(r'href="[^"]*?(https://www\.dropbox\.com/[^"\s]+\.(?:mp4|mov|m4v)[^"\s]*)"', p, flags=re.I)
        d = (file_date(link.group(1)) if link else None) or text_date(text)
        if not d:
            continue
        if link:
            services.append({"date": d.isoformat(), "title": title, "url": direct(html.unescape(link.group(1)))})
        else:
            unavailable.append({"date": d.isoformat(), "title": re.sub(r"\s*\(not available\)", "", title)})
    services.sort(key=lambda s: s["date"], reverse=True)
    return services, unavailable


def latest_facebook():
    """The stream page embeds the most recent Facebook broadcast."""
    m = re.search(r"facebook\.com/plugins/video\.php\?href=([^&\"]+)", get(LIVE))
    return urllib.parse.unquote(m.group(1)) if m else None


def main():
    services, unavailable = archive()
    if len(services) < 10:
        sys.exit(f"Only parsed {len(services)} services; leaving services.json untouched.")
    try:
        fb = latest_facebook()
    except Exception as e:  # the archive is what matters; the live embed is a bonus
        print("live page:", e)
        fb = None
    data = {"services": services, "unavailable": unavailable, "latestFacebook": fb}
    old = json.loads(OUT.read_text()) if OUT.exists() else {}
    old.pop("checked", None)
    if old == data:
        print("No change.")
        return
    data["checked"] = datetime.date.today().isoformat()
    OUT.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
    print(f"Wrote {len(services)} services, {len(unavailable)} unavailable.")


if __name__ == "__main__":
    main()
