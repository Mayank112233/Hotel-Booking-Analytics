# Data quality report

Source: supplied HRS practice CSV; provenance and currency unverified. Never actual HP performance.

6,000 rows checked; 0 invalid rows. No rows removed. Whitespace trimmed; money converted to integer cents; original file retained byte-for-byte.

| Check | Issues |
|---|---:|
|duplicate_booking_id|0|
|missing_customer_reference|0|
|missing_hotel_reference|0|
|invalid_dates|0|
|nights_mismatch|0|
|lead_time_mismatch|0|
|invalid_money|0|
|invalid_status|0|
|missing_channel|0|
|revenue_discrepancy|0|
|profit_discrepancy|0|
|noncompleted_cost|0|
|unexpected_dates|0|

Registration dates unavailable: cannot validate; not imputed. Guest counts, city, category and commissions unavailable. Customer name uses ID only.

Country varies within hotels and is retained as ambiguous source_country on fact; do not interpret it as verified hotel/customer nationality. Segment is booking-level because customer IDs span segments. Hotel location/category unknown. No currency conversion is possible: all monetary totals assume a common unspecified source unit (CU). Costs are source estimates, not audited expenses.

| Non-blocking source limitation | Affected entities | Action |
|---|---:|---|
|Multiple country labels per hotel|21|Keep ambiguous source_country on fact; hotel country Unknown|
|Multiple segments per customer|786|Retain segment at booking grain|
|Unavailable registration date|799|Null; validation not possible|
|Unavailable commission rate|5|Null; no invented ROI|
|Unavailable guest count|6000|Null; no guest-based metric|

Source dates 2025–2026 retained instead of fabricating 2023–2025 history. Allowed booking-date contract: 2025-01-01 through 2026-08-31; checkout through 2026-12-31. Update contract deliberately for new extracts. Future registration dates must be <= booking date if supplied. See data_quality.json for exact counts and source hash.
