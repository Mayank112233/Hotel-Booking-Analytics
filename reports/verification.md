# Execution and verification record

Date: 31 October 2026. Source file reused; no synthetic replacement generated. See data_quality.json for SHA-256. Update: Power BI Desktop authoring, refresh and baseline DAX export reconciliation are now complete; see powerbi_verification.md for the current delivery record. Temporary MySQL server directories and authoring caches were subsequently removed during repository cleanup. The verified source, results and finished report remain.

## Executed commands

Executed from the parent workspace using its `.venv/Scripts/python.exe` (scripts are path-independent):

```powershell
python Hotel-Booking-Analytics/python/pipeline.py
python -m unittest discover -s Hotel-Booking-Analytics/tests -v
python Hotel-Booking-Analytics/python/verify_mysql_local.py --mysqld "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqld.exe"
python Hotel-Booking-Analytics/python/generate_report.py
python Hotel-Booking-Analytics/python/run_tests.py
```

The environment's normal `python` alias was unavailable. A bundled Python 3.12 runtime created the workspace venv; its pip installed the dependencies into that venv. Exact installed versions are in requirements.lock.txt. Standard clean-environment commands are in README.

## Final verification

| Check | Result | Evidence |
|---|---|---|
|Core source data rules|13 checks, 6,000 rows, zero invalid rows|data_quality.json|
|Unittest suite|10 passed, zero final failures|test_results.txt|
|Primary/foreign keys and join grain|Passed in Python; database constraints verified|test_results.txt / mysql_integration.json|
|Financial calculations|Exact cent checks passed|data_quality.json / test_results.txt|
|Reproducibility|Two transforms identical; no row loss|test_results.txt|
|MySQL engine|Real MySQL 8.0.44 temporary instance|mysql_integration.json|
|SQL schema, loading and views|Executed successfully on MySQL|mysql_integration.json|
|Business SQL|10 basic + 10 advanced questions + monthly growth executed|mysql_integration.json query_files|
|MySQL quality query|All 11 issue counts zero; 799 registrations explicitly unavailable|mysql_integration.json|
|Independent SQL KPI validation|All 10 requested KPIs passed|mysql_integration.json, 08 query|
|Python/MySQL KPI reconciliation|11 measures passed|mysql_integration.json / kpi_reconciliation.json|
|Filtered reconciliation|Direct channel and April 2025 arrival context passed, all 11 measures each|mysql_integration.json|
|Database rejection checks|Duplicate key, orphan customer, bad revenue and invalid dates rejected|mysql_integration.json|
|Business reports|Generated from processed data; evidence CSVs saved|business_insights.md|
|Static figure|Rendered and visually inspected; labels and legend readable|screenshots/monthly_performance.png|
|Power BI Desktop / DAX / M|Executed in Desktop; 11 exported KPIs reconciled|powerbi_verification.md / powerbi_kpi_export.csv|

Local validation also reconciled all 11 baseline KPI values using portable SQL in SQLite. MySQL evidence is separately identified and uses the actual server. Actual Power BI results are preserved in powerbi_kpi_export.csv and compared to the stored verified MySQL baseline in powerbi_mysql_reconciliation.json.

## Errors found and fixed

The initial two unit-test errors were a temporary-directory permission issue and a handcrafted fixture missing display money columns. Tests now use an owned workspace temporary directory and the corrected fixture. MySQL testing found a reserved YEAR_MONTH identifier, a statement separator embedded in a display string, and SQLAlchemy inspection without a default database. All were corrected before the final passing MySQL run. Ratio precision was explicitly raised to avoid MySQL integer-division precision truncation.

MySQL sandboxed startup/connection attempts failed. The passing isolated integration run used local execution outside the sandbox, a separate test directory, a temporary port and ephemeral credentials. The test server was shut down afterward. No existing user database was modified. Ignored test directories retain their own temporary server files for inspection; no credentials appear in committed code or reports.

## Remaining manual work

The four pages, native model, M refresh, baseline DAX export, month/channel filter checks and July 2026 time-intelligence checks are complete. Power BI Service publishing and scheduled refresh remain optional future work. Exhaustive accessibility testing has not been performed. Obtain missing reference attributes if category/location analysis is needed. Registration quality cannot be verified without registration data. The existing practice dataset's provenance and currency remain unverified.
