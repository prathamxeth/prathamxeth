#!/usr/bin/env python3
"""Fetch GitHub contribution calendar and flagship repository metadata via GraphQL."""

import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
import requests

USERNAME = os.getenv("GITHUB_USERNAME", "prathamxeth")
TOKEN = os.getenv("GITHUB_TOKEN")
FEATURED_REPOS = ["nexus-ide", "LiveScript", "PALZEE-ANDROID", "palzee-ios"]

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
            contributionLevel
          }
        }
      }
    }
    repositories(first: 30, ownerAffiliations: OWNER, privacy: PUBLIC, orderBy: {field: UPDATED_AT, direction: DESC}) {
      nodes {
        name
        description
        url
        stargazerCount
        forkCount
        primaryLanguage {
          name
          color
        }
        repositoryTopics(first: 6) {
          nodes {
            topic {
              name
            }
          }
        }
      }
    }
  }
}
"""


def compute_stats(weeks: list) -> dict:
    days = [d for w in weeks for d in w["contributionDays"]]
    days.sort(key=lambda x: x["date"])

    active_days = sum(1 for d in days if d["contributionCount"] > 0)
    busiest = max(days, key=lambda x: x["contributionCount"], default={"date": "N/A", "contributionCount": 0})

    longest_streak = 0
    running = 0
    for d in days:
        if d["contributionCount"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    current_streak = 0
    for idx, d in enumerate(reversed(days)):
        if d["contributionCount"] > 0:
            current_streak += 1
        elif idx == 0:
            continue
        else:
            break

    monthly_totals = defaultdict(int)
    for d in days:
        monthly_totals[d["date"][:7]] += d["contributionCount"]

    months = []
    for ym, count in sorted(monthly_totals.items())[-12:]:
        dt = datetime.strptime(ym, "%Y-%m")
        months.append({
            "ym": ym,
            "label": dt.strftime("%b").upper(),
            "count": count,
        })

    return {
        "active_days": active_days,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "busiest_day": {
            "date": busiest["date"],
            "count": busiest["contributionCount"],
        },
        "months": months,
    }


def main():
    if not TOKEN:
        print("Error: GITHUB_TOKEN environment variable is required.", file=sys.stderr)
        sys.exit(1)

    resp = requests.post(
        "https://api.github.com/graphql",
        json={"query": QUERY, "variables": {"login": USERNAME}},
        headers={"Authorization": f"Bearer {TOKEN}"},
        timeout=20,
    )
    resp.raise_for_status()
    payload = resp.json()
    if "errors" in payload:
        print(f"GraphQL errors: {payload['errors']}", file=sys.stderr)
        sys.exit(1)

    user = payload["data"]["user"]
    cal = user["contributionsCollection"]["contributionCalendar"]
    stats = compute_stats(cal["weeks"])

    repo_map = {r["name"].lower(): r for r in user["repositories"]["nodes"]}
    repos = []
    for name in FEATURED_REPOS:
        r = repo_map.get(name.lower())
        if r:
            repos.append({
                "name": r["name"],
                "description": r["description"] or "",
                "url": r["url"],
                "stars": r["stargazerCount"],
                "forks": r["forkCount"],
                "language": (r["primaryLanguage"] or {}).get("name", ""),
                "language_color": (r["primaryLanguage"] or {}).get("color", "#6366F1"),
                "topics": [t["topic"]["name"] for t in r["repositoryTopics"]["nodes"]],
            })

    out = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "username": USERNAME,
        "total_contributions": cal["totalContributions"],
        "weeks": cal["weeks"],
        "stats": stats,
        "featured_repos": repos,
    }

    os.makedirs("data", exist_ok=True)
    with open("data/contributions.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"Saved data/contributions.json ({cal['totalContributions']} contributions)")


if __name__ == "__main__":
    main()
