# Power BI Desktop delivery verification

Executed 31 October 2026 using the installed Power BI Desktop. A separate native project was created in powerbi. The unused original blank report was removed during repository cleanup; the finished PBIX and native source are retained.

## Delivered report

- Four visible pages: Executive Overview, Revenue and Profitability, Customers and Cancellations, Operational Performance.
- Native PBIP under powerbi/source, with TMDL semantic model and PBIR report definitions, five CSV import tables, six relationships, 23 DAX measures and 64 visuals/controls including navigation, synchronized slicers and source notes.
- `powerbi/Hotel Booking Analytics.pbix` was saved by Power BI Desktop with embedded DataModel. Its ZIP integrity check passed; the original native PBIP remains available for source control. The finished PBIX is left open in Desktop on the unfiltered overview.
- A temporary KPI validation page was used for export and removed from the finished report. Its unused draft template was removed during repository cleanup; the actual exported CSV and reconciliation evidence remain. It is not a fifth dashboard page.
- Power Query CSV refresh succeeded in Desktop; all pages rendered actual data. Screenshots are actual Desktop captures, not mockups.

## Quantitative acceptance

The actual unfiltered Desktop export is `powerbi_kpi_export.csv`. All 11 exported baseline measures passed `validate_kpis.py --powerbi-csv reports/powerbi_kpi_export.csv`. They also match the stored results from the earlier successful real MySQL 8.0.44 integration run; see `powerbi_mysql_reconciliation.json`. This is comparison with the verified stored MySQL baseline, not a claim that a new production MySQL connection was used by Desktop.

| Check | Expected source calculation | Desktop observation | Result |
|---|---:|---:|---|
|All bookings|6,000|6,000|Pass|
|Completed stays|4,686|4,686|Pass|
|Revenue|1,940,329.12 CU|1,940,329.12 in exported CSV|Pass|
|Profit|545,217.39 CU|545,217.39 in exported CSV|Pass|
|July 2026 bookings|329|329|Pass|
|July 2026 revenue|115,995.16 CU|116.00K CU (display rounding)|Pass|
|July 2026 revenue MoM|15.056175%|15.06%|Pass|
|July 2026 revenue YoY|-4.325114%|-4.33%|Pass|
|July 2026 Direct bookings|73|73|Pass|
|July 2026 Direct revenue|25,580.18 CU|25.58K CU|Pass|

The month selection propagated from the overview to profitability; channel selection also propagated across pages. All test selections were cleared before delivery. Header and bottom-tab navigation were inspected. Use Ctrl+click for header navigation in Desktop edit mode. Prior-month/year measures now require a single selected month to avoid misleading 0% comparisons over the entire date table. Multiple months and missing/zero prior revenue yield blank comparison ratios.

## Technical checks

The report JSON definitions passed development-time validation with zero errors. After Desktop saved the project, 24 visuals referenced Microsoft's 2.14.0 visual schema URL, which returned HTTP 404. Those 24 were checked for compatible structure against the published 2.4.0 schema; the remaining files used their exact published schemas. The one-time validation tools, schema downloads and verbose schema-validation output were subsequently removed from the portfolio. Desktop itself accepted and rendered the actual definitions. Native TMDL parsing, DAX execution and M refresh were verified by opening/refreshing the actual report in Desktop, not inferred from JSON syntax alone.

The model retains the original en-IN locale, with explicit en-US CSV parsing for dates/decimals. Initial locale incompatibility and an undersized navigator container were corrected. Money labels and card sizes were refined during actual rendering. The corporate theme uses blue, white and gray; Unknown hotel category remains visible and explicitly qualified.

## Limits

No Power BI Service publication, workspace upload or scheduled refresh was performed. No exhaustive screen-reader or every-filter-combination test is claimed. Top-ten and customer detail visuals can scroll. Practice-data provenance, currency, cost estimates and missing reference attributes retain the limitations in data_quality_report.md. Relocating the project requires updating pDataFolder before CSV refresh.

Official format references: [PBIR projects](https://learn.microsoft.com/en-us/power-bi/developer/embedded/projects-enhanced-report-format), [TMDL](https://learn.microsoft.com/en-us/analysis-services/tmdl/tmdl-overview). The shipped PBIP contains the editable report and semantic model; no separate schema cache is needed to open it in Desktop.
