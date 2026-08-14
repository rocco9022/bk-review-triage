#!/usr/bin/env python3
"""Fetch recent BK reviews from BOTH stores and write feed.txt as
ID|RATING|DATE|TITLE|BODY lines. Runs in GitHub Actions (open internet),
NOT in the cloud routine (whose egress blocks the stores).
  iOS  : Apple RSS customer reviews feed (App Store id 638323895)
  Android: Google Play (package com.emn8.mobilem8.nativeapp.bk) via google-play-scraper
Review IDs are unique per store, so they never collide across sources."""
import json, urllib.request

def clean(s):
    return (s or "").replace("\n", " ").replace("|", "/").strip()

lines = []

# --- iOS: Apple RSS ---
IOS = "https://itunes.apple.com/us/rss/customerreviews/id=638323895/sortBy=mostRecent/json"
try:
    req = urllib.request.Request(IOS, headers={"User-Agent": "bk-review-triage"})
    data = json.load(urllib.request.urlopen(req, timeout=60))
    for x in data["feed"].get("entry", []):
        if "im:rating" not in x:
            continue  # first entry is app metadata
        lines.append("|".join([
            x["id"]["label"].strip(),
            x["im:rating"]["label"].strip(),
            x.get("updated", {}).get("label", "")[:10],
            clean(x["title"]["label"]),
            clean(x["content"]["label"]),
        ]))
    print(f"iOS: {len(lines)} reviews")
except Exception as e:
    print(f"iOS fetch failed: {e}")

# --- Android: Google Play ---
try:
    from google_play_scraper import reviews, Sort
    n0 = len(lines)
    res, _ = reviews("com.emn8.mobilem8.nativeapp.bk", lang="en", country="us",
                     sort=Sort.NEWEST, count=100)
    for r in res:
        lines.append("|".join([
            r["reviewId"],
            str(r["score"]),
            str(r["at"])[:10],
            "",                      # Play reviews have no title
            clean(r["content"]),
        ]))
    print(f"Android: {len(lines)-n0} reviews")
except Exception as e:
    print(f"Android fetch failed: {e}")

open("feed.txt", "w").write("\n".join(lines) + "\n")
print(f"wrote {len(lines)} total reviews to feed.txt")
