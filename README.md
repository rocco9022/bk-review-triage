# BK Review Triage

Backing store for the Burger King app review triage tracker (design team).
Source: the Slack **#app-reviews-bk** channel (appbot mirror of App Store +
Google Play reviews), read via the Slack MCP connector — this bypasses the
cloud egress allowlist, so no domain allowlisting is required.

- `reviews.csv` — one row per classified review. Columns: `Date, Summary, Category, Severity, Review ID, Review Link`. `Review ID` is the appbot review id (dedup key).
- `new_reviews.py` — stdin filter: given `ID|RATING|DATE|TITLE|BODY` lines, prints only those not already in reviews.csv.

A Google Sheet live-imports `reviews.csv` via `=IMPORTDATA(<raw csv url>)`.

## Classification
- **UX/UI ISSUE** — concrete, nameable app/interface problem. Severity High/Medium/Low.
- **OPERATIONAL** — store ops (food, wrong/missing items, waits, staff). No severity.
- **UNCLEAR** — ambiguous / generic praise / off-topic. No severity.
Borderline UX/UI vs Operational: UX/UI only for a concrete interface problem. Never reclassify existing rows.
