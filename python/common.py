"""Shared contracts. Money is stored in integer cents for exact reconciliation."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / 'data' / 'processed'
STATUSES = ['Completed', 'Cancelled', 'No Show', 'Pending', 'Refunded']

def read_fact():
    return pd.read_csv(PROCESSED / 'bookings.csv', parse_dates=['booking_date','check_in_date','check_out_date'])

def kpis(d):
    c = d[d.booking_status.eq('Completed')]
    repeat = c.groupby('customer_id').size()
    revenue, profit = int(d.revenue_cents.sum()), int(d.profit_cents.sum())
    div = lambda a,b: a / b if b else None
    return dict(total_bookings=int(d.booking_id.nunique()), completed_bookings=len(c),
        cancelled_bookings=int(d.booking_status.eq('Cancelled').sum()),
        total_revenue=revenue/100, total_profit=profit/100,
        average_booking_value=div(revenue/100,len(c)),
        cancellation_rate=div(int(d.booking_status.eq('Cancelled').sum()),len(d)),
        profit_margin=div(profit,revenue), average_daily_rate=div(revenue/100,int(c.number_of_nights.sum())),
        average_length_of_stay=div(int(c.number_of_nights.sum()),len(c)),
        repeat_customer_rate=div(int((repeat>1).sum()),len(repeat)))

def save_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, default=str), encoding='utf-8')
