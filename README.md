# BK Review Triage

Backing store for the Burger King **iOS** App Store review triage tracker used by the design team.

- `reviews.csv` — one row per classified review. Columns: `Date, Summary, Category, Severity, Review ID, Review Link`.
- `new_reviews.py` — prints App Store reviews not yet in `reviews.csv` (JSON lines).

A Google Sheet live-imports `reviews.csv` via `=IMPORTDATA(<raw csv url>)`.

## Classification
- **UX/UI ISSUE** — concrete, nameable app/interface problem a designer can act on. Severity: High (blocks a purchase/core flow) / Medium (noticeable friction) / Low (minor annoyance).
- **OPERATIONAL** — store ops (food cold, wrong order, delivery, staff, quality). No severity.
- **UNCLEAR** — ambiguous or too little detail; not forced into the other two. No severity.

Borderline UX/UI vs Operational: choose UX/UI only if there's a concrete interface problem ("charged me twice" = UX/UI; "food was cold" = Operational). Do not reclassify existing rows.
