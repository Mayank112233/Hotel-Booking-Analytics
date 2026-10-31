# KPI dictionary and reconciliation

All KPIs respect the current arrival-date, hotel, region, channel and booking-segment filters. The SQL view returns the unfiltered baseline. Unit CU means unspecified common source currency. Every requested KPI has an executable calculation in `sql/07_analytics_views.sql` (vw_kpis), and matching DAX in dax_measures.dax.

| KPI / SQL column | DAX measure | Definition and interpretation | Independent validation |
|---|---|---|---|
|total_bookings|Total Bookings|Distinct booking IDs, all statuses; demand volume|Raw unique booking_id count|
|completed_bookings|Completed Bookings|Completed rows; fulfilled stays|Raw status count|
|total_revenue|Total Revenue|Sum realized room revenue, Completed only; scale of earned room sales|Sum (rate * nights - discount) over completed rows|
|total_profit|Total Profit|Revenue minus source estimated cost; estimated contribution|Raw completed net room amounts less cost|
|average_booking_value|Average Booking Value|Revenue / completed bookings; value per fulfilled stay|Mean completed revenue|
|cancellation_rate|Cancellation Rate|Cancelled / all bookings; lost reservation share|Raw cancelled count / raw row count|
|profit_margin|Profit Margin|Profit / revenue; source estimated contribution ratio|1 - completed cost / completed revenue|
|average_daily_rate|Average Daily Rate|Realized room revenue / completed room nights; discounted revenue per occupied room-night|Weighted completed net nightly rate|
|average_length_of_stay|Average Length of Stay|Completed nights / completed bookings; stay duration|Mean date difference on completed rows|
|repeat_customer_rate|Repeat Customer Rate|Customers with >1 completed stay / customers with >=1 completed stay, within selected history|Completed bookings grouped by customer_id|

Cancelled Bookings is an additional baseline count. Cancelled, No Show, Pending and Refunded rows contribute zero realized revenue and estimated cost in this source contract. No Show is not Cancelled. Zero denominators yield NULL/blank; do not imply a zero performance rate when there is no eligible population. Guest and room counts are absent; one room per reservation is an assumption. No occupancy or RevPAR is calculated.

Run `sql/08_kpi_validation.sql` after views to independently validate all ten KPIs from booking money and dates. Run `python python/validate_kpis.py --mysql` for Python/MySQL reconciliation. The Python test suite also uses a handcrafted known-answer fixture, no-completed-stay subsets, and channel/month filters. Read reports/kpi_reconciliation.json for the actual backend used. It is never acceptable to label SQLite checks as MySQL checks.

Power BI reconciliation requires actual Desktop execution and an unfiltered one-row CSV export with baseline column names. `--powerbi-csv` compares all 11 fields; date-shift measures additionally need monthly Desktop spot checks. The report build guide contains the acceptance steps. No DAX execution is claimed before that export exists.
