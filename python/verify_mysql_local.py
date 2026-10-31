"""Optional real MySQL integration against a disposable localhost instance.

Never touches an existing server. Requires a local MySQL 8 mysqld binary.
The disposable directory stays ignored for inspection after shutdown.
"""
import argparse
import os
import secrets
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
import mysql.connector
from sqlalchemy import text
import pandas as pd
from common import ROOT, read_fact, kpis, save_json
from load_database import statements
from validate_kpis import compare

def main():
    p=argparse.ArgumentParser();p.add_argument('--mysqld',required=True);args=p.parse_args()
    binary=Path(args.mysqld).resolve()
    folder=Path(tempfile.mkdtemp(prefix='mysql-test-',dir=ROOT)).resolve()
    assert folder.parent==ROOT.resolve()
    with socket.socket() as s: s.bind(('127.0.0.1',0)); port=s.getsockname()[1]
    base=[str(binary),'--no-defaults',f'--basedir={binary.parent.parent}',f'--datadir={folder}',
          f'--innodb-undo-directory={folder}',f'--innodb-data-home-dir={folder}']
    subprocess.run([*base,'--initialize-insecure'],check=True,capture_output=True)
    log=(folder/'server-console.log').open('w')
    process=subprocess.Popen([*base,f'--port={port}','--bind-address=127.0.0.1','--mysqlx=0','--console'],
        stdout=log,stderr=log,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    password=secrets.token_urlsafe(24)
    result={'backend':'MySQL','query_files':{},'constraint_checks':{},'status':'failed'}
    conn=None
    try:
        for _ in range(60):
            try:
                conn=mysql.connector.connect(host='127.0.0.1',port=port,user='root',password='',connection_timeout=2);break
            except mysql.connector.Error as exc:
                last_error=str(exc);time.sleep(.25)
        if conn is None: raise RuntimeError('Disposable MySQL connection failed: '+last_error)
        cursor=conn.cursor();cursor.execute('SELECT VERSION()'); result['version']=cursor.fetchone()[0]
        cursor.execute("ALTER USER 'root'@'localhost' IDENTIFIED BY %s",(password,));conn.commit();conn.close()
        os.environ.update(MYSQL_HOST='127.0.0.1',MYSQL_PORT=str(port),MYSQL_USER='root',MYSQL_PASSWORD=password)
        subprocess.run([sys.executable,str(ROOT/'python/load_database.py')],check=True)
        from load_database import engine
        with engine().connect() as db:
            db.execute(text('USE hotel_booking_analytics'))
            for name in ['04_data_validation.sql','05_business_queries.sql','06_advanced_queries.sql','08_kpi_validation.sql']:
                rows=[]
                for query in statements(ROOT/'sql'/name):
                    r=db.execute(text(query))
                    if r.returns_rows:
                        fetched=[dict(x) for x in r.mappings().all()]
                        rows.append(fetched)
                result['query_files'][name]=rows
                if name.startswith('04'):
                    assert all(int(x['issues'])==0 for x in rows[0]),rows[0]
                if name.startswith('08'):
                    assert all(int(x)==1 for x in rows[0] for x in x.values()),rows[0]
            actual=dict(db.execute(text('SELECT * FROM vw_kpis')).mappings().one())
            result['kpi_checks']=compare(kpis(read_fact()),actual)
            assert all(x['passed'] for x in result['kpi_checks'].values())
            # Match monthly/region/channel subsets against Python; view aggregate semantics stay identical.
            d=read_fact()
            expression=(ROOT/'sql/07_analytics_views.sql').read_text().split('CREATE OR REPLACE VIEW vw_kpis AS')[1].strip().rstrip(';')
            # For repeat's nested query, use a temporary view and replace all table references.
            result['filtered_checks']={}
            for label,predicate,subset in [
                ('Direct',"booking_channel_placeholder",d[d.booking_channel.eq('Direct')]),
                ('April2025',"check_in_date BETWEEN '2025-04-01' AND '2025-04-30'",d[d.check_in_date.dt.strftime('%Y-%m').eq('2025-04')])]:
                if label=='Direct': predicate="channel_id=(SELECT channel_id FROM channels WHERE channel_name='Direct')"
                db.execute(text(f'CREATE OR REPLACE VIEW test_subset AS SELECT * FROM bookings WHERE {predicate}'))
                got=dict(db.execute(text(expression.replace('FROM bookings','FROM test_subset'))).mappings().one())
                checks=compare(kpis(subset),got);assert all(x['passed'] for x in checks.values())
                result['filtered_checks'][label]=checks
            # Concrete constraint rejection tests run in transactions, always rollback.
            for label,query in [('primary_key',"INSERT INTO channels SELECT * FROM channels LIMIT 1"),
                ('foreign_key',"UPDATE bookings SET customer_id='ORPHAN' WHERE booking_id='BKG000001'"),
                ('revenue_check',"UPDATE bookings SET revenue_cents=revenue_cents+1 WHERE booking_id='BKG000001'"),
                ('date_check',"UPDATE bookings SET check_out_date=check_in_date WHERE booking_id='BKG000001'")]:
                try: db.execute(text(query)); db.rollback(); raise AssertionError(f'{label} accepted invalid data')
                except Exception as exc:
                    db.rollback()
                    if isinstance(exc,AssertionError):raise
                    result['constraint_checks'][label]='rejected'
        subprocess.run([sys.executable,str(ROOT/'python/validate_kpis.py'),'--mysql'],check=True)
        result['status']='passed'
        print('Real MySQL validation, 21 business/advanced queries, 11 KPIs, 2 filtered contexts and 4 constraint rejections passed.')
    finally:
        save_json(ROOT/'reports/mysql_integration.json',result)
        try:
            conn=mysql.connector.connect(host='127.0.0.1',port=port,user='root',password=password)
            conn.cmd_shutdown();conn.close()
        except mysql.connector.Error: process.terminate()
        process.wait(timeout=30);log.close()

if __name__=='__main__':main()
