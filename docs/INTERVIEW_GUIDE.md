# Interview walkthrough

Use this as a route through the repository. Explain the code and choices in your own words, and run the examples before the interview.

## A one-minute introduction

“This project analyzes 6,000 hotel reservations to understand revenue, estimated profitability, channel cancellations and booking demand. Python validates the source and produces five related tables. MySQL provides the relational database, business queries and independent KPI checks. Power BI imports the cleaned CSV tables through Power Query and uses DAX for four interactive report pages. I checked the results by comparing exported Power BI metrics with Python and a verified MySQL baseline.”

Be clear that this is a practice dataset. Revenue figures are analytical results, not business impact you produced for an employer. The source does not identify a currency, so amounts are labeled CU.

## Suggested order: 10–15 minutes

| Stop | Open | Explain or demonstrate |
|---|---|---|
|1. Business question|README.md|Who would use the report and what decisions it supports|
|2. Evidence|reports/business_insights.md|Two observed findings and a recommendation; distinguish association from causation|
|3. Source data|data/raw/bookings_source.csv|One reservation per row; IDs, dates, statuses, amounts and missing attributes|
|4. Preparation|python/clean_data.py|Type conversion, exact money checks, dimensions, issue reporting and raw-data preservation|
|5. Database|sql/02_create_tables.sql|Primary/foreign keys, CHECK constraints, integer cents and generated monetary columns|
|6. Analysis|sql/05_business_queries.sql and sql/06_advanced_queries.sql|Show one grouped query, one HAVING query and one window-function query|
|7. Reporting model|powerbi/data_model.md and powerbi/dax_measures.dax|Star schema, date roles, filter context and KPI denominators|
|8. Working report|powerbi/Hotel Booking Analytics.pbix|Walk through the four pages and apply a month/channel filter|
|9. Verification|tests/test_pipeline.py and reports/powerbi_mysql_reconciliation.json|Explain the known-answer fixture, corruption checks and independent reconciliation|

## 1. Explain the source before discussing charts

The source contains 6,000 bookings, 799 customer IDs, 21 hotels, five channels and five regions. Booking dates cover January 2025 through August 2026; arrival dates extend later. Each fact row represents one reservation. One room per booking is an assumption because room quantity is unavailable.

Show one completed row and one cancelled row. Explain that completed stays contribute realized room revenue, while noncompleted bookings contribute zero revenue and cost under the current contract. No Show is a separate status from Cancelled.

Two important source problems influenced the design:

- The same customer ID can occur in different segments. Segment is therefore a booking attribute, not a fixed customer-dimension attribute.
- The same hotel appears under multiple country labels. The original label is retained as source_country on the booking fact. Physical hotel country, city and category are not fabricated.

Registration dates, guest counts and channel commissions are unavailable. Unknown or null is more accurate than an invented value.

## 2. Explain the Python pipeline

Start at python/pipeline.py. It runs cleaning, optionally loads MySQL, reconciles KPIs and generates the analytical report. If a subprocess fails, the pipeline stops rather than continuing with unverified outputs.

In clean_data.py, explain these steps:

1. Read the preserved raw file and standardize names and whitespace.
2. Parse dates and convert money to integer cents.
3. Derive gross booking amount and stable dimension IDs.
4. Check IDs, required references, dates, nights, lead time, status and financial consistency.
5. Write a quality summary. Reject invalid core rows with a report and abort; never silently discard them.
6. Export bookings.csv, hotels.csv, customers.csv, channels.csv and dates.csv.

For money, show that 129.37 CU is stored as 12,937 cents. This avoids tiny floating-point discrepancies in reconciliation. For a completed stay:

```text
Gross amount = nightly room rate × nights
Realized revenue = gross amount − discount
Estimated profit = realized revenue − estimated cost
```

The current source passes 13 core checks with no rows removed. That does not mean all source attributes are trustworthy; the country/segment limitations remain documented.

## 3. Explain the database

The database is hotel_booking_analytics. The loader reads credentials from environment variables or an untracked .env file. It uses SQLAlchemy and MySQL Connector, with parameterized inserts.

- A primary key identifies each booking uniquely.
- Foreign keys require customers, hotels, channels and dates to exist.
- CHECK constraints reject invalid date and financial relationships.
- Indexes support common arrival-date, hotel and channel/status filters.
- Monetary decimal columns are generated from the authoritative cent columns.

Data refresh deletes and reloads the dedicated project's tables inside a transaction. A failed insert rolls back that data refresh. Schema creation is separate because MySQL DDL implicitly commits.

The supplied MySQL integration evidence came from a disposable real MySQL 8.0.44 instance. The test-server files were removed after verification. A MySQL server is not kept running for the dashboard.

## 4. Three SQL examples to demonstrate

**Channel cancellation rate:** explain the numerator and denominator. Cancelled bookings are divided by every selected booking, including No Show. Show Q15 in sql/06_advanced_queries.sql.

**Repeat stays:** show Q13. WHERE selects completed stays before grouping; HAVING filters customers after their completed bookings are counted.

**Second-highest hotel revenue:** show Q11. First aggregate revenue per hotel, then apply DENSE_RANK. A rank of two means the second distinct revenue level and returns all ties. Contrast this with ROW_NUMBER in Q12, which returns exactly three positions per region using a deterministic tie breaker.

For monthly trends, explain why grouping by year and month is necessary: January 2025 and January 2026 must remain separate periods.

## 5. Explain the actual Power BI data connection

The delivered report imports the five processed CSV files. It does not query MySQL during normal dashboard use. MySQL is a parallel analysis and validation branch.

The only dashboard file at the top level of powerbi is Hotel Booking Analytics.pbix. The separate powerbi/source folder contains its editable PBIP project, report definitions and semantic model. Keep that folder intact: its components reference each other. It is source code for the dashboard, not another duplicate presentation file.

In Desktop, open Transform data. The pDataFolder parameter points to data/processed. Each M query reads a CSV with File.Contents and Csv.Document, promotes headers, replaces empty strings with nulls and applies data types. The booking query also creates lead-time bands.

Import mode stores a copy of the data in the PBIX. It can therefore be presented without access to MySQL or the original files. Refresh needs the processed CSV folder. On another computer, update pDataFolder first.

The relationship model has FactBookings in the center, connected to hotels, customers, channels and dates. Filters flow from the dimensions to the fact.

The active date relationship uses check_in_date, so normal revenue charts report arrivals in the selected period. Booking Demand uses the inactive booking_date relationship through USERELATIONSHIP and disables the arrival-date relationship for that measure. It counts when reservations were created rather than when guests arrive.

## 6. Explain DAX using filter context

Open powerbi/dax_measures.dax. Explain these measures first:

```dax
Total Revenue = DIVIDE(SUM(FactBookings[revenue_cents]), 100)

Average Booking Value = DIVIDE([Total Revenue], [Completed Bookings])

Cancellation Rate = DIVIDE([Cancelled Bookings], [Total Bookings])
```

Selecting a channel changes the set of booking rows used by these calculations. That is filter context. Power Query prepares rows during refresh; DAX measures calculate results for the current report selection.

ADR divides realized room revenue by completed room nights. It is different from the average quoted room rate. Repeat Customer Rate is the share of completed customers with more than one completed stay within the selected history; it is not lifetime loyalty.

Prior-month/year comparisons require one selected month. With the whole history selected, comparison cards are intentionally blank. DIVIDE returns blank for a zero or missing denominator.

## 7. A reliable live demonstration

1. Open the finished PBIX on Executive Overview. Clear the slicers.
2. Point out 6,000 bookings, 4,686 completed stays, revenue of 1,940,329.12 CU and estimated profit of 545,217.39 CU. Cards may abbreviate amounts using K or M.
3. Select July 2026 in Arrival month. There should be 329 bookings and revenue of 115,995.16 CU.
4. Open Revenue and Profitability. The month selection should persist. Revenue MoM is +15.06%; YoY is −4.33%.
5. Select Direct in Channel, then return to the overview. Expect 73 bookings and 25,580.18 CU revenue.
6. Clear the selections. Explain that these checks confirm both calculations and filter propagation.
7. Show Customer Analytics and Operations. Explain the lead-time distribution and the difference between booking-date demand and arrival-date revenue.

Use bottom page tabs. Header navigator buttons use Ctrl+click in Desktop edit mode. Some detailed bar charts and tables scroll.

## 8. Discuss findings without overstating them

- Europe leads source-region revenue: 821,688.54 CU.
- Corporate Portal has the highest observed cancellation rate: 369 cancellations from 2,026 bookings, or 18.21%.
- Munich Business Hotel contributes the most source-estimated profit: 48,600.03 CU.

A reasonable recommendation is to investigate channel cancellations by segment, lead time and policy before changing acquisition spending. Channel differences do not prove that the channel causes cancellations. Commission data is missing, so acquisition ROI cannot be calculated.

## 9. Explain how correctness was tested

The ten Python tests cover key uniqueness, foreign keys, join grain, dates, exact financial calculations, a hand-calculated KPI fixture, no-completed-stay cases, filtered reconciliation, repeatable transformation and deliberate corruptions.

Real MySQL verification executed the schema, loader, business queries, independent KPI checks and invalid-write rejection checks. All eleven baseline KPIs also match an actual Power BI CSV export. This is stronger evidence than checking that a chart merely looks reasonable.

Open reports/powerbi_kpi_export.csv and reports/powerbi_mysql_reconciliation.json to show the actual values. The MySQL comparison uses the verified stored integration baseline for the same dataset.

## Questions to prepare for

| Question | Point to explain |
|---|---|
|Why a star schema?|Clear fact grain, reusable dimensions and predictable filtering|
|Why keep segment on the fact?|The source assigns different segments to the same customer ID|
|Why use cents?|Exact money checks and consistent SQL/Python reconciliation|
|Why not calculate occupancy or RevPAR?|Available-room inventory and room-night capacity are missing|
|Why does the report work without MySQL?|The delivered PBIX uses CSV import mode and contains embedded data|
|How is a refresh performed?|Run Python to rebuild processed CSVs, then Refresh in Desktop|
|Why is profit estimated?|The dataset supplies estimated costs, not audited operating expenses|
|What would you improve next?|Verify currency/geography, obtain reference attributes and capacity data, then consider Service refresh|
|What is not implemented?|Power BI Service publication, scheduled refresh, a refund cash ledger and night-level revenue recognition|
|How was the report built?|Native PBIP source defines TMDL/M/DAX and PBIR visuals; it was opened, refreshed and checked in Desktop, then saved as PBIX|

## Before the interview

Run the tests, open the PBIX, confirm the filtered example, and practice explaining one SQL window query without reading a script. Describe the tooling and assistance you used accurately if asked. Be ready to explain the assumptions and limitations as confidently as the dashboard features.
