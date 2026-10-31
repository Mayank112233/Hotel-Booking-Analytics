"""MySQL transactional refresh; schema DDL runs separately and is not transactional."""
import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, URL
from common import ROOT, PROCESSED

def engine(database=True):
    load_dotenv(ROOT/'.env')
    if not os.getenv('MYSQL_USER') or not os.getenv('MYSQL_PASSWORD'):
        raise RuntimeError('Set MYSQL_USER and MYSQL_PASSWORD in environment or .env; no credentials are guessed.')
    return create_engine(URL.create('mysql+mysqlconnector',username=os.environ['MYSQL_USER'],
        password=os.environ['MYSQL_PASSWORD'],host=os.getenv('MYSQL_HOST','127.0.0.1'),
        port=int(os.getenv('MYSQL_PORT','3306')),database='hotel_booking_analytics' if database else None),pool_pre_ping=True)

def statements(path):
    # Project SQL has no stored programs or semicolons inside literals.
    source='\n'.join(line for line in path.read_text(encoding='utf-8').splitlines() if not line.lstrip().startswith('--'))
    return [s.strip() for s in source.split(';') if s.strip()]

def main():
    e=engine(database=False)
    with e.connect() as conn:
        for name in ['01_create_database.sql','02_create_tables.sql','03_load_data.sql']:
            for s in statements(ROOT/'sql'/name): conn.execute(text(s))
        conn.commit()
    e.dispose()
    e=engine()
    with e.begin() as conn:
        conn.execute(text('USE hotel_booking_analytics'))
        for table in ['bookings','dates','channels','customers','hotels']:
            conn.execute(text(f'DELETE FROM {table}'))
        for table in ['hotels','customers','channels','dates','bookings']:
            frame=pd.read_csv(PROCESSED/f'{table}.csv')
            if table=='bookings':
                frame=frame.drop(columns=['booking_channel','room_rate','total_booking_amount','discount_amount','revenue','estimated_cost','profit'])
            # SQLAlchemy sends missing values as SQL NULL, preserves declared table constraints.
            frame.to_sql(table,conn,if_exists='append',index=False,chunksize=500,method='multi')
    with e.connect() as conn:
        conn.execute(text('USE hotel_booking_analytics'))
        for s in statements(ROOT/'sql/07_analytics_views.sql'): conn.execute(text(s))
        conn.commit()
    print('MySQL schema, transactional data refresh, and analytics views complete.')

if __name__=='__main__': main()
