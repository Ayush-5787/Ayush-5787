"""
fetch_contributions.py — real contribution data, no GraphQL API, no token.

GitHub serves your contribution calendar as public HTML at
https://github.com/users/<username>/contributions -- the same fragment the
profile page itself uses. We fetch it, parse the day cells, and write
data/contributions.json with raw days plus a few derived stats.

Usage:
    python scripts/fetch_contributions.py [username]

If no username is given, GITHUB_USERNAME env var is used, falling back to
the constant below.
"""
import json
import os
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

DEFAULT_USERNAME = "your-username"  # <-- change me, or pass as CLI arg / env var
OUT_PATH = Path("data/contributions.json")

HEADERS = {"User-Agent": "Mozilla/5.0 (profile-readme-bot)"}


def fetch_html(username: str) -> str:
    url = f"https://github.com/users/{username}/contributions"
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.text


def parse_days(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    cells = soup.select("td.ContributionCalendar-day[data-date]")

    # tooltip text ("5 contributions on September 21st.") is the only place
    # the exact count lives; it's linked to its cell via the `for` attribute
    tooltip_by_id = {}
    for tip in soup.select("tool-tip[for]"):
        tooltip_by_id[tip.get("for")] = tip.get_text(strip=True)

    days = []
    for cell in cells:
        cell_id = cell.get("id")
        tooltip = tooltip_by_id.get(cell_id, "")
        match = re.search(r"(\d+|No)\s+contributions?", tooltip)
        if match:
            count = 0 if match.group(1) == "No" else int(match.group(1))
        else:
            count = 0

        days.append(
            {
                "date": cell.get("data-date"),
                "level": int(cell.get("data-level", 0)),
                "count": count,
            }
        )

    days.sort(key=lambda d: d["date"])
    return days


def compute_stats(days: list[dict]) -> dict:
    total = sum(d["count"] for d in days)

    # streaks (consecutive days with count > 0), evaluated in date order
    longest = current = 0
    running = 0
    today = date.today().isoformat()
    for d in days:
        if d["count"] > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0
    # current streak: walk backwards from the most recent day that has data
    current = 0
    for d in reversed(days):
        if d["date"] > today:
            continue
        if d["count"] > 0:
            current += 1
        else:
            break

    best_day = max(days, key=lambda d: d["count"], default=None)

    monthly: dict[str, int] = {}
    for d in days:
        month_key = d["date"][:7]  # YYYY-MM
        monthly[month_key] = monthly.get(month_key, 0) + d["count"]

    return {
        "total_contributions": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best_day,
        "monthly_totals": monthly,
    }


def main() -> None:
    username = (
        sys.argv[1]
        if len(sys.argv) > 1
        else os.environ.get("GITHUB_USERNAME", DEFAULT_USERNAME)
    )

    print(f"Fetching contributions for {username}...")
    html = fetch_html(username)
    days = parse_days(html)

    if not days:
        raise RuntimeError(
            "No contribution cells parsed -- GitHub may have changed its "
            "markup, or the username has no public calendar."
        )

    stats = compute_stats(days)

    payload = {
        "username": username,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "days": days,
        **stats,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2))
    print(
        f"Wrote {OUT_PATH}: {stats['total_contributions']} total, "
        f"streak {stats['current_streak']} (longest {stats['longest_streak']})"
    )


if __name__ == "__main__":
    main()