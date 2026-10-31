import unittest
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'python'))
from common import read_fact, kpis
from clean_data import transform
from validate_kpis import local_sql, compare

class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=read_fact()
        cls.raw=ROOT/'data/raw/bookings_source.csv'

    def test_primary_keys(self):
        for file,key in [('bookings','booking_id'),('hotels','hotel_id'),('customers','customer_id'),('channels','channel_id'),('dates','date')]:
            frame=pd.read_csv(ROOT/f'data/processed/{file}.csv')
            self.assertTrue(frame[key].is_unique); self.assertFalse(frame[key].isna().any())

    def test_foreign_keys_and_join_grain(self):
        for file,key in [('hotels','hotel_id'),('customers','customer_id'),('channels','channel_id')]:
            dim=pd.read_csv(ROOT/f'data/processed/{file}.csv')
            self.assertTrue(self.d[key].isin(dim[key]).all())
            self.assertEqual(len(self.d.merge(dim,on=key,validate='many_to_one')),len(self.d))

    def test_dates(self):
        d=self.d
        self.assertTrue((d.booking_date<=d.check_in_date).all())
        self.assertTrue((d.check_out_date>d.check_in_date).all())
        self.assertTrue(d.number_of_nights.eq((d.check_out_date-d.check_in_date).dt.days).all())
        self.assertTrue(d.lead_time_days.eq((d.check_in_date-d.booking_date).dt.days).all())

    def test_money(self):
        d=self.d; c=d.booking_status.eq('Completed')
        self.assertTrue(d.loc[c,'revenue_cents'].eq(d.loc[c,'total_booking_amount_cents']-d.loc[c,'discount_amount_cents']).all())
        self.assertTrue(d.loc[~c,'revenue_cents'].eq(0).all())
        self.assertTrue(d.profit_cents.eq(d.revenue_cents-d.estimated_cost_cents).all())

    def test_kpi_fixture_statuses_and_denominators(self):
        fixture=pd.DataFrame({'booking_id':list('abcde'),'customer_id':['x','x','y','z','q'],
            'booking_status':['Completed','Completed','Cancelled','Pending','Refunded'],
            'revenue_cents':[10000,20000,0,0,0],'profit_cents':[2000,6000,0,0,0],'number_of_nights':[2,3,1,1,1]})
        got=kpis(fixture)
        fixture['revenue']=fixture.revenue_cents/100
        fixture['profit']=fixture.profit_cents/100
        expected={'total_bookings':5,'completed_bookings':2,'cancelled_bookings':1,'total_revenue':300,'total_profit':80,
            'average_booking_value':150,'cancellation_rate':.2,'profit_margin':80/300,'average_daily_rate':60,
            'average_length_of_stay':2.5,'repeat_customer_rate':1}
        self.assertEqual(got,expected)
        self.assertTrue(all(x['passed'] for x in compare(expected,local_sql(fixture)).values()))

    def test_zero_denominators(self):
        d=self.d[self.d.booking_status.eq('Cancelled')]
        got=kpis(d)
        for k in ['average_booking_value','average_daily_rate','average_length_of_stay','repeat_customer_rate','profit_margin']:
            self.assertIsNone(got[k])
        self.assertTrue(all(x['passed'] for x in compare(got,local_sql(d)).values()))

    def test_python_sql_reconciliation(self):
        self.assertTrue(all(x['passed'] for x in compare(kpis(self.d),local_sql(self.d)).values()))

    def test_filtered_reconciliation(self):
        for d in [self.d[self.d.booking_channel.eq('Direct')],self.d[self.d.check_in_date.dt.strftime('%Y-%m').eq('2025-04')]]:
            self.assertTrue(all(x['passed'] for x in compare(kpis(d),local_sql(d)).values()))

    def test_transform_reproducibility(self):
        first=transform(self.raw); second=transform(self.raw)
        for a,b in zip(first[:4],second[:4]): pd.testing.assert_frame_equal(a,b)
        self.assertEqual(len(first[0]),len(pd.read_csv(self.raw)))
        self.assertTrue(all(not x.any() for x in first[4].values()))

    def test_corruptions_detected_not_deleted(self):
        d=pd.read_csv(self.raw); d.loc[1,'booking_id']=d.loc[0,'booking_id']; d.loc[2,'revenue']+=1
        d.loc[3,'checkout_date']=d.loc[3,'checkin_date']; d.loc[4,'booking_channel']=''
        d.loc[5,'booking_status']='Invalid'
        with TemporaryDirectory(dir=ROOT) as folder:
            self.assertEqual(Path(folder).resolve().parent,ROOT.resolve())
            path=Path(folder)/'bad.csv'; d.to_csv(path,index=False)
            cleaned,*_,checks=transform(path)
        self.assertEqual(len(cleaned),len(d))
        for k in ['duplicate_booking_id','revenue_discrepancy','invalid_dates','missing_channel','invalid_status']:
            self.assertTrue(checks[k].any(),k)

if __name__=='__main__': unittest.main()
