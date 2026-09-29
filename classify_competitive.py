#!/usr/bin/env python3
"""Classify new competitor reviews for UX feature signals using Claude API.

Reads competitive_feed.txt, filters against competitive_processed_ids.txt,
sends unprocessed reviews to Claude for classification, and appends confirmed
UX features to competitive_tracker.csv.

Runs in GitHub Actions (open internet + ANTHROPIC_API_KEY secret).
"""
import csv, json, os, subprocess, sys, urllib.request
from datetime import date

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
if not API_KEY:
    print("ANTHROPIC_API_KEY not set — skipping classification")
    sys.exit(0)

# --- Get unprocessed reviews ---
try:
    result = subprocess.run(
        ["python3", "new_competitive.py"],
        stdin=open("competitive_feed.txt"),
        capture_output=True, text=True, check=True,
    )
    new_lines = [l for l in result.stdout.splitlines() if l.strip() and not l.startswith("#")]
    print(result.stderr.strip())
except FileNotFoundError:
    print("competitive_feed.txt not found — nothing to classify")
    sys.exit(0)

if not new_lines:
    print("No new competitive reviews to classify")
    sys.exit(0)

print(f"Classifying {len(new_lines)} new reviews...")

# Batch reviews for Claude (max 200 per call to stay under token limits)
BATCH = 200

SYSTEM = """You are a competitive UX intelligence analyst for Burger King's product team.
You receive raw app store reviews from competitor apps (McDonald's, Wendy's, Taco Bell, Domino's, Starbucks, Chipotle, Subway, Chick-fil-A).
Your job: identify reviews that clearly describe a NEW UX feature or product capability — something the app added, changed, or launched.
Ignore: complaints, praise without feature content, bugs, delivery issues, price comments.

For each feature found, output a JSON object (one per line, no array wrapper):
{
  "date": "DD.Mon.YYYY",
  "type": "Confirmed",
  "competitor": "Name",
  "feature": "Clear one-sentence description of the feature",
  "category": one of ["Ordering flow","Personalization","Loyalty/Rewards","Checkout","Navigation/UI","Other"],
  "confidence": "Confirmed",
  "source": "App Store reviews",
  "link": "",
  "notes": "Brief insight on competitive relevance to BK",
  "alert": "Yes or empty string"
}

Use today's date for date. Only output JSON lines — no prose, no explanation.
If no features found in the batch, output nothing."""

def call_claude(reviews_text):
    payload = json.dumps({
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 2000,
        "system": SYSTEM,
        "messages": [{"role": "user", "content": reviews_text}],
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.load(resp)
    return data["content"][0]["text"]

# --- Process in batches ---
new_rows = []
today = date.today().strftime("%d.%b.%Y")

for i in range(0, len(new_lines), BATCH):
    batch = new_lines[i:i+BATCH]
    reviews_text = "\n".join(batch)
    try:
        output = call_claude(reviews_text)
        for line in output.splitlines():
            line = line.strip()
            if not line or not line.startswith("{"):
                continue
            try:
                feat = json.loads(line)
                feat.setdefault("date", today)
                new_rows.append(feat)
            except json.JSONDecodeError:
                pass
    except Exception as e:
        print(f"Claude API error on batch {i//BATCH+1}: {e}")

print(f"Found {len(new_rows)} new UX features")

# --- Append to competitive_reviews.csv and re-sort by date desc ---
COLS = ["Date","Type","Competitor","Feature","Category","Confidence","Sentiment","Rating","Source","Link","Notes","Alert"]

def parse_date(d):
    from datetime import datetime
    for fmt in ("%d.%b.%Y", "%b.%Y", "%d.%B.%Y"):
        try:
            return datetime.strptime(d.strip(), fmt)
        except ValueError:
            pass
    return datetime.min

# Read existing rows
existing = []
if os.path.exists("competitive_reviews.csv"):
    with open("competitive_reviews.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            existing.append(row)

# Append new rows
for r in new_rows:
    existing.append({
        "Date": r.get("date",""), "Type": r.get("type","Confirmed"),
        "Competitor": r.get("competitor",""), "Feature": r.get("feature",""),
        "Category": r.get("category",""), "Confidence": r.get("confidence","Confirmed"),
        "Sentiment": r.get("sentiment",""), "Rating": r.get("rating",""),
        "Source": r.get("source","App Store reviews"), "Link": r.get("link",""),
        "Notes": r.get("notes",""), "Alert": r.get("alert",""),
    })

# Always sort by date descending and rewrite
existing.sort(key=lambda r: parse_date(r.get("Date","")), reverse=True)

with open("competitive_reviews.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=COLS, extrasaction="ignore")
    w.writeheader()
    w.writerows(existing)

if new_rows:
    print(f"Appended {len(new_rows)} rows to competitive_reviews.csv")

# --- Update processed IDs ledger ---
new_ids = []
for line in new_lines:
    parts = line.split("|", 2)
    if len(parts) >= 2:
        rid = parts[1].strip()
        if rid:
            new_ids.append(rid)

with open("competitive_processed_ids.txt", "a") as f:
    for rid in new_ids:
        f.write(rid + "\n")

print(f"Marked {len(new_ids)} reviews as processed")
