"""Reconcile exact analytics-view SQL against Python. SQLite is an explicit local fallback."""
import argparse
import json
import math
import sqlite3
import pandas as pd
from common import ROOT, read_fact, kpis, save_json

def local_sql(d):
    conn=sqlite3.connect(':memory:')
    d.to_sql('bookings',conn,index=False)
    # MySQL vw_kpis query is portable to SQLite; cast integer aggregates to REAL
    # only in SQLite because SQLite integer division differs from MySQL division.
    sql=(ROOT/'sql/07_analytics_views.sql').read_text().split('CREATE OR REPLACE VIEW vw_kpis AS')[1].strip().rstrip(';')
    sql=sql.replace('SUM(revenue)/','1.0*SUM(revenue)/').replace('SUM(profit)/','1.0*SUM(profit)/')
    sql=sql.replace("SUM(CASE WHEN booking_status='Cancelled' THEN 1 ELSE 0 END)/", "1.0*SUM(CASE WHEN booking_status='Cancelled' THEN 1 ELSE 0 END)/")
    out=pd.read_sql_query(sql,conn).iloc[0].to_dict()
    conn.close()
    return out

def compare(expected, actual):
    return {k:{'python':v,'sql':None if pd.isna(actual[k]) else float(actual[k]),
        'passed':(pd.isna(actual[k]) if v is None else math.isclose(v,float(actual[k]),rel_tol=1e-9,abs_tol=1e-7))} for k,v in expected.items()}

def main():
    p=argparse.ArgumentParser(); p.add_argument('--mysql',action='store_true'); p.add_argument('--powerbi-csv',type=str)
    args=p.parse_args(); d=read_fact(); expected=kpis(d)
    if args.mysql:
        from load_database import engine
        from sqlalchemy import text
        with engine().connect() as conn:
            conn.execute(text('USE hotel_booking_analytics'))
            actual=pd.read_sql_query(text('SELECT * FROM vw_kpis'),conn).iloc[0].to_dict()
        backend='MySQL 8'
    else: actual=local_sql(d); backend='SQLite portable KPI SQL (not MySQL integration)'
    result={'backend':backend,'checks':compare(expected,actual),'powerbi':'NOT RUN: export required'}
    if args.powerbi_csv:
        # One-row unfiltered CSV; names must match kpi_baseline.csv. Ratios as decimals, not percent strings.
        exported=pd.read_csv(args.powerbi_csv).iloc[0].to_dict()
        result['powerbi']=compare(expected,exported)
    save_json(ROOT/'reports/kpi_reconciliation.json',result)
    pd.DataFrame([expected]).to_csv(ROOT/'reports/kpi_baseline.csv',index=False)
    assert all(x['passed'] for x in result['checks'].values()),result
    if isinstance(result['powerbi'],dict): assert all(x['passed'] for x in result['powerbi'].values())
    print(f'{len(expected)} KPI checks passed: {backend}')

if __name__=='__main__': main()
