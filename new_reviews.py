#!/usr/bin/env python3
"""Filter App Store review lines to only those NOT yet in reviews.csv.

Reads pipe-delimited lines from stdin: ID|RATING|DATE|TITLE|BODY
(produced by WebFetch on the App Store review feed).
Prints only lines whose ID is not already logged in reviews.csv.
The sandbox proxy blocks direct HTTP, so fetching is done via the
WebFetch tool by the agent; this script only does dedup."""
import csv, sys
seen=set()
try:
    with open("reviews.csv",newline="") as f:
        for r in csv.DictReader(f):
            if r.get("Review ID"): seen.add(r["Review ID"].strip())
except FileNotFoundError:
    pass
n=0
for line in sys.stdin:
    line=line.rstrip("\n")
    if not line.strip() or "|" not in line: continue
    rid=line.split("|",1)[0].strip()
    if rid and rid not in seen:
        print(line); n+=1
print(f"# {n} new review(s)",file=sys.stderr)
