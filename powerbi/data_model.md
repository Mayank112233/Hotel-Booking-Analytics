# Semantic model contract

Status: native PBIP report built and refreshed in Power BI Desktop using processed CSVs. Baseline DAX export reconciled; see reports/powerbi_verification.md. MySQL views are an alternative source, not imported alongside the CSVs.

| Table | CSV / MySQL view | Grain and key |
|---|---|---|
|FactBookings|bookings.csv / vw_fact_bookings|One booking; booking_id|
|DimHotels|hotels.csv / vw_dim_hotels|One source hotel name and region; hotel_id|
|DimCustomers|customers.csv / vw_dim_customers|One customer identifier; customer_id|
|DimChannels|channels.csv / vw_dim_channels|One booking channel; channel_id|
|DimDate|dates.csv / vw_dim_date|One date, 2024-01-01–2027-12-31; date|

Create single-direction 1:* relationships from each dimension key to the corresponding fact key. DimDate[date] -> FactBookings[check_in_date] is active. Add inactive relationships to booking_date and check_out_date. Mark DimDate as the date table using date; disable Auto date/time. Sort month_name by month_number; use year_month for chronological monthly axes. Date columns are Date, IDs are Text except channel_id (Whole Number). Money cents and nights are Whole Number; displayed money columns are Fixed Decimal. Hide keys and cents from report users. Never summarize IDs.

Fact-level customer_segment deliberately preserves changes within customer IDs; do not build a segment relationship through DimCustomers. source_country is an ambiguous source label, not verified geography. DimHotels country, city and hotel_category are Unknown; DimCustomers country is Unknown, customer_name is an identifier, and registration_date is null. Guest counts and commission rates are null. No invented reference data is used.

Bookings assume one room per reservation because no room-count field exists. Realized revenue is discounted room revenue for Completed only; all other statuses have zero revenue and cost in the current contract. Profit uses the supplied estimated cost; it is not audited net profit. Refunded rows would be zero net room revenue, not a cash-flow ledger. Any future noncompleted cost or refund-fee change requires contract and tests to change together.

All revenue is attributed to arrival date, including multi-month stays. Operational Booking Demand switches the date role to booking_date. Repeat Customer Rate counts customers with >1 completed stay within the current report filters, not lifetime repeat guests. Hotel/channel/segment filters also affect the eligible customer population. Cancellation rate uses Cancelled / all selected bookings; No Show is separate.

CU = unspecified common source currency unit; cross-country totals rely on the explicit common-currency assumption. Do not show dollar symbols. No room inventory means no occupancy or RevPAR.

Official references checked for implementation: [date table guidance](https://learn.microsoft.com/en-us/power-bi/guidance/model-date-tables), [Auto date/time guidance](https://learn.microsoft.com/en-us/power-bi/guidance/auto-date-time), [time intelligence](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-time-intelligence).
