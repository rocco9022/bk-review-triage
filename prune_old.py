#!/usr/bin/env python3
"""Drop reviews.csv rows older than 40 days (rolling window).
Runs in the GitHub Action. Keeps the header. Dates are YYYY-MM-DD."""
import csv, datetime
CUTOFF = (datetime.datetime.utcnow().date() - datetime.timedelta(days=40)).isoformat()
rows=list(csv.reader(open("reviews.csv",encoding="utf-8")))
header,data=rows[0],rows[1:]
kept=[r for r in data if r and r[0] >= CUTOFF]
with open("reviews.csv","w",newline="",encoding="utf-8") as f:
    csv.writer(f).writerows([header]+kept)
print(f"cutoff {CUTOFF}: kept {len(kept)} of {len(data)} rows")
