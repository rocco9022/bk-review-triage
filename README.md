# BK Review Triage

Automated UX/UI review triage for the Burger King app (design team).

## Flow
1. **GitHub Action** (`.github/workflows/fetch-reviews.yml`, daily 11:00 UTC) fetches recent reviews from **both stores** — iOS (Apple RSS) and Android (Google Play via `google-play-scraper`) — and writes them to `feed.txt` (`ID|RATING|DATE|TITLE|BODY`, one per line).
2. **Cloud routine** (daily 12:00 UTC) classifies each NEW review. Only **UX/UI issues** are kept; operational (food, delivery, staff, condiments) and generic/unclear reviews are dropped. Every processed id is recorded in `processed_ids.txt` so nothing is re-evaluated.
3. A **Google Sheet** live-imports `reviews.csv` via `=IMPORTDATA(<raw url>)`.

## Files
- `reviews.csv` — UX/UI issues only. Columns: `Fecha, Plataforma, Área, Severidad, Recurrente, Resumen, Comentario original, Link`.
- `processed_ids.txt` — every review id ever evaluated (dedup ledger).
- `feed.txt` — latest fetched reviews (input for the routine).
- `new_reviews.py` — prints feed lines whose id is not in processed_ids.txt.
- `fetch_feed.py` — fetches iOS + Android into feed.txt.

## Área (functional buckets)
Pagos y checkout · Flujo de pedido · Menú y ofertas · Rewards/Loyalty · Cuenta/Login · Performance/Crashes · Navegación/UI · Ubicación/Tienda · Personalización · Otro

## Severidad
High = blocks a purchase/core flow · Medium = noticeable friction · Low = minor annoyance.

## Recurrente
"Sí" if the same problem/area was already logged before, else "No".
