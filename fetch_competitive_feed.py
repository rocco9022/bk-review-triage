#!/usr/bin/env python3
"""Fetch recent reviews from competitor apps (iOS + Android) and write
competitive_feed.txt as COMPETITOR|ID|RATING|DATE|BODY lines.

Competitors tracked:
  McDonald's  iOS: 922103212       Android: com.mcdonalds.mobileapp
  Wendy's     iOS: 540518599       Android: com.wendys.nutritiontool
  Taco Bell   iOS: 1098818919      Android: com.tacobell.android
  Domino's    iOS: 436491861       Android: com.dominospizza
  Starbucks   iOS: 331177714       Android: com.starbucks.mobilecard

Runs in GitHub Actions (open internet).
NOT in the cloud routine (egress blocked).
"""
import json, urllib.request

IOS_APPS = [
    ("McDonalds",  "922103212"),
    ("Wendys",     "540518599"),
    ("TacoBell",   "1098818919"),
    ("Dominos",    "436491861"),
    ("Starbucks",  "331177714"),
]

ANDROID_APPS = [
    ("McDonalds",  "com.mcdonalds.mobileapp"),
    ("Wendys",     "com.wendys.nutritiontool"),
    ("TacoBell",   "com.tacobell.android"),
    ("Dominos",    "com.dominospizza"),
    ("Starbucks",  "com.starbucks.mobilecard"),
]

def clean(s):
    return (s or "").replace("\n", " ").replace("|", "/").strip()

lines = []

# --- iOS: Apple RSS ---
for name, app_id in IOS_APPS:
    url = f"https://itunes.apple.com/us/rss/customerreviews/id={app_id}/sortBy=mostRecent/json"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "bk-competitive-triage"})
        data = json.load(urllib.request.urlopen(req, timeout=60))
        count = 0
        for x in data["feed"].get("entry", []):
            if "im:rating" not in x:
                continue
            lines.append("|".join([
                name,
                x["id"]["label"].strip(),
                x["im:rating"]["label"].strip(),
                x.get("updated", {}).get("label", "")[:10],
                clean(x["content"]["label"]),
            ]))
            count += 1
        print(f"iOS {name}: {count} reviews")
    except Exception as e:
        print(f"iOS {name} fetch failed: {e}")

# --- Android: Google Play ---
try:
    from google_play_scraper import reviews, Sort
    for name, pkg in ANDROID_APPS:
        try:
            n0 = len(lines)
            res, _ = reviews(pkg, lang="en", country="us",
                             sort=Sort.NEWEST, count=40)
            for r in res:
                lines.append("|".join([
                    name,
                    r["reviewId"],
                    str(r["score"]),
                    str(r["at"])[:10],
                    clean(r["content"]),
                ]))
            print(f"Android {name}: {len(lines)-n0} reviews")
        except Exception as e:
            print(f"Android {name} fetch failed: {e}")
except ImportError as e:
    print(f"google-play-scraper not available: {e}")

open("competitive_feed.txt", "w").write("\n".join(lines) + "\n")
print(f"wrote {len(lines)} total competitive reviews to competitive_feed.txt")
