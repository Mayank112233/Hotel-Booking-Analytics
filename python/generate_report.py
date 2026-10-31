"""Evidence tables and report, with observed findings separated from recommendations."""
import pandas as pd
from common import ROOT, PROCESSED, read_fact, kpis

def table(d):
    return '| '+' | '.join(d.columns)+' |\n|'+'|'.join(['---']*len(d.columns))+'|\n'+''.join('| '+' | '.join(str(x) for x in row)+' |\n' for row in d.itertuples(index=False,name=None))

def main():
    d=read_fact().merge(pd.read_csv(PROCESSED/'hotels.csv')[['hotel_id','hotel_name','region']],on='hotel_id',validate='many_to_one')
    c=d[d.booking_status.eq('Completed')].copy(); m=kpis(d)
    regions=d.groupby('region',as_index=False).agg(revenue=('revenue','sum'),profit=('profit','sum'),bookings=('booking_id','size')).sort_values('revenue',ascending=False)
    channels=d.groupby('booking_channel',as_index=False).agg(bookings=('booking_id','size'),cancelled=('booking_status',lambda x:x.eq('Cancelled').sum()),revenue=('revenue','sum'))
    channels['cancellation_rate']=channels.cancelled/channels.bookings
    channels=channels.merge(c.groupby('booking_channel',as_index=False).agg(completed=('booking_id','size')),how='left')
    channels['abv']=channels.revenue/channels.completed
    hotels=d.groupby('hotel_name',as_index=False).agg(profit=('profit','sum'),revenue=('revenue','sum'),bookings=('booking_id','size')).sort_values('profit',ascending=False)
    segments=c.groupby('customer_segment',as_index=False).agg(abv=('revenue','mean'),revenue=('revenue','sum'),completed=('booking_id','size')).sort_values('abv',ascending=False)
    d['arrival_month']=d.check_in_date.dt.strftime('%Y-%m')
    monthly=d.groupby('arrival_month',as_index=False).agg(bookings=('booking_id','size'),revenue=('revenue','sum'),profit=('profit','sum'),cancelled=('booking_status',lambda x:x.eq('Cancelled').sum()))
    monthly['cancellation_rate']=monthly.cancelled/monthly.bookings
    demand=d.assign(booking_month=d.booking_date.dt.strftime('%Y-%m')).groupby('booking_month',as_index=False).agg(bookings=('booking_id','size'))
    for name,frame in [('regions',regions),('channels',channels),('hotels',hotels),('segments',segments),('monthly',monthly),('booking_demand',demand)]:
        frame.to_csv(ROOT/f'reports/{name}.csv',index=False,float_format='%.8f')
    highest=channels.sort_values('cancellation_rate',ascending=False).iloc[0]
    peak=monthly.sort_values('revenue',ascending=False).iloc[0]
    source_max=d.booking_date.max().date()
    body=f'''# Hotel booking business insights

Source: user-supplied HRS practice dataset, 6,000 records. Provenance is unverified; these are practice results, never actual HP performance. Monetary values use unspecified source currency units (CU), with an assumed common currency. Profit uses estimated costs.

## Observed findings

- Realized revenue: {m['total_revenue']:,.2f} CU; estimated profit: {m['total_profit']:,.2f} CU; margin: {m['profit_margin']:.2%}.
- {m['completed_bookings']:,} completed stays; cancellation rate {m['cancellation_rate']:.2%}; completed-stay ABV {m['average_booking_value']:.2f} CU.
- {regions.iloc[0]['region']} leads revenue at {regions.iloc[0]['revenue']:,.2f} CU ({regions.iloc[0]['revenue']/m['total_revenue']:.2%} of total).
- {highest['booking_channel']} has the highest cancellation rate: {highest['cancellation_rate']:.2%}, based on {highest['bookings']} bookings and {highest['cancelled']} cancellations.
- {hotels.iloc[0]['hotel_name']} contributes the most estimated profit: {hotels.iloc[0]['profit']:,.2f} CU.
- {segments.iloc[0]['customer_segment']} has highest completed-stay ABV: {segments.iloc[0]['abv']:,.2f} CU. Segments describe bookings, not fixed customer traits.
- Peak observed arrival-month revenue is {peak['arrival_month']}: {peak['revenue']:,.2f} CU on {peak['bookings']} reservations.
- Repeat-customer rate within selected history: {m['repeat_customer_rate']:.2%}; ADR {m['average_daily_rate']:.2f} CU; mean completed length of stay {m['average_length_of_stay']:.2f} nights.

## Regional evidence

{table(regions.round(2))}

## Channel evidence

{table(channels.round(4))}

## Profit contributors

{table(hotels.head(10).round(2))}

## Segment evidence

{table(segments.round(2))}

## Demand and seasonality

{table(monthly.round(4))}

Booking demand is exported separately using booking_date; revenue uses check_in_date. Booking dates end {source_max}; later arrival months represent a censored booking pipeline. Compare complete matching months across years before interpreting seasonality. One full year and a partial second year cannot establish a stable recurring seasonal pattern. Full-year 2025 versus partial 2026 totals are not comparable.

## Hypotheses to investigate

Channel cancellation differences may reflect customer mix, lead times, or policies. No causal effect is established. Peak-month demand may reflect source-generation patterns; no real-world forecasting claim is justified.

## Recommendations and stakeholder decisions

Review the highest-cancellation channel using segment and lead-time breakdowns; test reminders or flexible terms with a controlled comparison before changing policy. Compare completed ABV and estimated margin alongside cancellation volume before reallocating acquisition spend. Commission data is missing, so this project cannot calculate channel acquisition ROI.

Use leading-profit hotels as a shortlist for cost and rate review, rather than assuming high volume implies efficiency. Use arrival-month demand, lead-time bands and room-type counts for staffing scenarios; room inventory is absent, so neither occupancy nor RevPAR is available. Obtain capacity data before making room-allocation decisions.

## Operational risks and limits

Country attribution, hotel category, guest counts and registration dates are unresolved. Do not infer physical hotel geography from source_country or names. Category reporting is a single Unknown bucket until reference data is supplied. Revenue assigned to arrival month is a portfolio convention; revenue is not allocated across individual nights. Cancelled, No Show, Pending and Refunded have zero realized revenue and cost under the current data contract; actual fees/refund cash movements require a separate ledger. Repeat rate is period-based, not lifetime loyalty. No numerical uplift from recommendations is claimed.

## Evidence

Calculated by python/generate_report.py from data/processed/bookings.csv. Exact group aggregates are saved beside this report. KPI reconciliation and quality results are separate machine-readable artifacts.
'''
    (ROOT/'reports/business_insights.md').write_text(body,encoding='utf-8')
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import seaborn as sns
        sns.set_theme(style='whitegrid',palette=['#145DA0','#64748B'])
        fig,ax=plt.subplots(figsize=(12,5))
        ax.plot(monthly.arrival_month,monthly.revenue,marker='o',label='Revenue')
        ax.plot(monthly.arrival_month,monthly.profit,marker='s',label='Estimated profit')
        ax.set(title='Practice data: arrival-month revenue and estimated profit',ylabel='Source currency units (CU)',xlabel='Arrival month')
        ax.tick_params(axis='x',rotation=60); ax.legend(); fig.tight_layout()
        ax.set_ylim(bottom=0)
        ax.axvspan(19.5,21.5,color='#E2E8F0',alpha=.7)
        ax.text(.99,.95,'Later arrivals: booking history ends Aug 2026',transform=ax.transAxes,ha='right',va='top',fontsize=9)
        fig.savefig(ROOT/'screenshots/monthly_performance.png',dpi=160); plt.close(fig)
    except ImportError:
        print('Chart not generated: install matplotlib and seaborn. Analytical CSVs/report are complete.')
    print('Business report and evidence aggregates refreshed.')

if __name__=='__main__': main()
