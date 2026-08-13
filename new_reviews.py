#!/usr/bin/env python3
"""Print App Store reviews not yet logged in reviews.csv, as JSON lines.
Each line: {"id","date","rating","version","title","body"}."""
import csv, json, sys, urllib.request
FEED="https://itunes.apple.com/us/rss/customerreviews/id=638323895/sortBy=mostRecent/json"
seen=set()
try:
    with open("reviews.csv",newline="") as f:
        for r in csv.DictReader(f):
            if r.get("Review ID"): seen.add(r["Review ID"].strip())
except FileNotFoundError:
    pass
req=urllib.request.Request(FEED,headers={"User-Agent":"bk-review-triage"})
data=json.load(urllib.request.urlopen(req,timeout=30))
entries=data["feed"].get("entry",[])
# first entry is app metadata (has no im:rating)
out=[]
for x in entries:
    if "im:rating" not in x: continue
    rid=x["id"]["label"].strip()
    if rid in seen: continue
    out.append({"id":rid,"date":x.get("updated",{}).get("label","")[:10],
                "rating":x["im:rating"]["label"],
                "version":x.get("im:version",{}).get("label",""),
                "title":x["title"]["label"],
                "body":x["content"]["label"]})
for o in out: print(json.dumps(o,ensure_ascii=False))
print(f"# {len(out)} new review(s)",file=sys.stderr)
