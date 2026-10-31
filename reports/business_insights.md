# Hotel booking business insights

Source: user-supplied HRS practice dataset, 6,000 records. Provenance is unverified; these are practice results, never actual HP performance. Monetary values use unspecified source currency units (CU), with an assumed common currency. Profit uses estimated costs.

## Observed findings

- Realized revenue: 1,940,329.12 CU; estimated profit: 545,217.39 CU; margin: 28.10%.
- 4,686 completed stays; cancellation rate 16.82%; completed-stay ABV 414.07 CU.
- Europe leads revenue at 821,688.54 CU (42.35% of total).
- Corporate Portal has the highest cancellation rate: 18.21%, based on 2026 bookings and 369 cancellations.
- Munich Business Hotel contributes the most estimated profit: 48,600.03 CU.
- Corporate has highest completed-stay ABV: 477.74 CU. Segments describe bookings, not fixed customer traits.
- Peak observed arrival-month revenue is 2025-07: 121,238.88 CU on 321 reservations.
- Repeat-customer rate within selected history: 98.50%; ADR 137.04 CU; mean completed length of stay 3.02 nights.

## Regional evidence

| region | revenue | profit | bookings |
|---|---|---|---|
| Europe | 821688.54 | 231078.24 | 2411 |
| North America | 487245.44 | 137920.2 | 1310 |
| Asia Pacific | 301612.13 | 83743.04 | 1185 |
| Middle East | 217847.85 | 60965.98 | 624 |
| Latin America | 111935.16 | 31509.93 | 470 |


## Channel evidence

| booking_channel | bookings | cancelled | revenue | cancellation_rate | completed | abv |
|---|---|---|---|---|---|---|
| Corporate Portal | 2026 | 369 | 612032.04 | 0.1821 | 1554 | 393.843 |
| Direct | 1289 | 219 | 418788.25 | 0.1699 | 998 | 419.6275 |
| Mobile App | 1088 | 160 | 378055.05 | 0.1471 | 872 | 433.5494 |
| Partner | 852 | 146 | 285065.21 | 0.1714 | 669 | 426.1064 |
| Travel Agency | 745 | 115 | 246388.57 | 0.1544 | 593 | 415.4951 |


## Profit contributors

| hotel_name | profit | revenue | bookings |
|---|---|---|---|
| Munich Business Hotel | 48600.03 | 173570.99 | 498 |
| HRS Berlin Central | 48357.85 | 171937.12 | 486 |
| Paris Executive | 46244.47 | 166697.27 | 510 |
| Milan Business Suites | 45488.01 | 160874.28 | 460 |
| Amsterdam City Stay | 42387.88 | 148608.88 | 457 |
| Toronto Corporate Hotel | 30419.73 | 107419.1 | 284 |
| Chicago Executive | 28094.13 | 97392.05 | 251 |
| New York Business Inn | 27562.05 | 98051.69 | 268 |
| Austin Business Stay | 26137.09 | 93956.15 | 259 |
| San Francisco Central | 25707.2 | 90426.45 | 248 |


## Segment evidence

| customer_segment | abv | revenue | completed |
|---|---|---|---|
| Corporate | 477.74 | 840830.78 | 1760 |
| Enterprise | 437.3 | 379573.5 | 868 |
| SME | 355.27 | 397189.26 | 1118 |
| Individual | 343.34 | 322735.58 | 940 |


## Demand and seasonality

| arrival_month | bookings | revenue | profit | cancelled | cancellation_rate |
|---|---|---|---|---|---|
| 2025-01 | 170 | 54071.87 | 15370.02 | 27 | 0.1588 |
| 2025-02 | 247 | 73699.02 | 20991.78 | 37 | 0.1498 |
| 2025-03 | 303 | 91948.84 | 25427.45 | 44 | 0.1452 |
| 2025-04 | 285 | 87164.54 | 24607.0 | 43 | 0.1509 |
| 2025-05 | 336 | 101974.95 | 28525.33 | 49 | 0.1458 |
| 2025-06 | 311 | 107731.46 | 30360.02 | 57 | 0.1833 |
| 2025-07 | 321 | 121238.88 | 33589.43 | 40 | 0.1246 |
| 2025-08 | 302 | 107141.68 | 29431.75 | 53 | 0.1755 |
| 2025-09 | 266 | 83338.49 | 23643.47 | 47 | 0.1767 |
| 2025-10 | 309 | 93239.18 | 26247.51 | 58 | 0.1877 |
| 2025-11 | 282 | 89988.3 | 24577.77 | 45 | 0.1596 |
| 2025-12 | 312 | 111390.96 | 31358.69 | 37 | 0.1186 |
| 2026-01 | 309 | 94601.07 | 26713.9 | 65 | 0.2104 |
| 2026-02 | 278 | 80604.19 | 23302.52 | 50 | 0.1799 |
| 2026-03 | 307 | 103973.11 | 28252.4 | 45 | 0.1466 |
| 2026-04 | 292 | 83116.88 | 23600.91 | 62 | 0.2123 |
| 2026-05 | 298 | 98259.58 | 27323.06 | 49 | 0.1644 |
| 2026-06 | 309 | 100816.11 | 28751.82 | 62 | 0.2006 |
| 2026-07 | 329 | 115995.16 | 33350.43 | 57 | 0.1733 |
| 2026-08 | 304 | 100021.55 | 28731.28 | 55 | 0.1809 |
| 2026-09 | 123 | 37225.7 | 10235.76 | 26 | 0.2114 |
| 2026-10 | 7 | 2787.6 | 825.09 | 1 | 0.1429 |


Booking demand is exported separately using booking_date; revenue uses check_in_date. Booking dates end 2026-08-31; later arrival months represent a censored booking pipeline. Compare complete matching months across years before interpreting seasonality. One full year and a partial second year cannot establish a stable recurring seasonal pattern. Full-year 2025 versus partial 2026 totals are not comparable.

## Hypotheses to investigate

Channel cancellation differences may reflect customer mix, lead times, or policies. No causal effect is established. Peak-month demand may reflect source-generation patterns; no real-world forecasting claim is justified.

## Recommendations and stakeholder decisions

Review the highest-cancellation channel using segment and lead-time breakdowns; test reminders or flexible terms with a controlled comparison before changing policy. Compare completed ABV and estimated margin alongside cancellation volume before reallocating acquisition spend. Commission data is missing, so this project cannot calculate channel acquisition ROI.

Use leading-profit hotels as a shortlist for cost and rate review, rather than assuming high volume implies efficiency. Use arrival-month demand, lead-time bands and room-type counts for staffing scenarios; room inventory is absent, so neither occupancy nor RevPAR is available. Obtain capacity data before making room-allocation decisions.

## Operational risks and limits

Country attribution, hotel category, guest counts and registration dates are unresolved. Do not infer physical hotel geography from source_country or names. Category reporting is a single Unknown bucket until reference data is supplied. Revenue assigned to arrival month is a portfolio convention; revenue is not allocated across individual nights. Cancelled, No Show, Pending and Refunded have zero realized revenue and cost under the current data contract; actual fees/refund cash movements require a separate ledger. Repeat rate is period-based, not lifetime loyalty. No numerical uplift from recommendations is claimed.

## Evidence

Calculated by python/generate_report.py from data/processed/bookings.csv. Exact group aggregates are saved beside this report. KPI reconciliation and quality results are separate machine-readable artifacts.
