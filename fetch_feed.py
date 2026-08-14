#!/usr/bin/env python3
"""Fetch recent BK iOS App Store reviews and write feed.txt as
ID|RATING|DATE|TITLE|BODY lines. Runs in GitHub Actions (open internet),
NOT in the cloud routine (whose egress blocks Apple)."""
import json, urllib.request
FEED="https://itunes.apple.com/us/rss/customerreviews/id=638323895/sortBy=mostRecent/json"
req=urllib.request.Request(FEED,headers={"User-Agent":"bk-review-triage"})
data=json.load(urllib.request.urlopen(req,timeout=60))
lines=[]
for x in data["feed"].get("entry",[]):
    if "im:rating" not in x: continue  # first entry is app metadata
    rid=x["id"]["label"].strip()
    rating=x["im:rating"]["label"].strip()
    date=x.get("updated",{}).get("label","")[:10]
    title=x["title"]["label"].replace("\n"," ").replace("|","/").strip()
    body=x["content"]["label"].replace("\n"," ").replace("|","/").strip()
    lines.append(f"{rid}|{rating}|{date}|{title}|{body}")
open("feed.txt","w").write("\n".join(lines)+"\n")
print(f"wrote {len(lines)} reviews to feed.txt")
