#!/usr/bin/env python3
"""Filter competitive_feed.txt lines to reviews NOT yet processed.

Reads pipe lines COMPETITOR|ID|RATING|DATE|BODY from stdin.
Dedups against competitive_processed_ids.txt.
Prints only unprocessed lines."""
import sys

seen = set()
try:
    for l in open("competitive_processed_ids.txt"):
        l = l.strip()
        if l:
            seen.add(l)
except FileNotFoundError:
    pass

n = 0
for line in sys.stdin:
    line = line.rstrip("\n")
    if not line.strip() or "|" not in line:
        continue
    parts = line.split("|", 2)
    if len(parts) < 2:
        continue
    rid = parts[1].strip()  # field 1 is the review ID (field 0 is competitor name)
    if rid and rid not in seen:
        print(line)
        n += 1

print(f"# {n} new competitive review(s)", file=sys.stderr)
