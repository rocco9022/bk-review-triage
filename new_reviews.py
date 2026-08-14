#!/usr/bin/env python3
"""Filter feed lines to reviews NOT yet processed.

Reads pipe lines ID|RATING|DATE|TITLE|BODY from stdin (from feed.txt).
Dedups against processed_ids.txt (every review id ever evaluated,
whether or not it ended up in reviews.csv). Prints only unprocessed lines.
This keeps the routine from re-classifying operational/unclear reviews
every day even though they are not stored in reviews.csv."""
import sys
seen=set()
try:
    for l in open("processed_ids.txt"):
        l=l.strip()
        if l: seen.add(l)
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
