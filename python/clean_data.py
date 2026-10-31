"""Preserve source; fail on invalid core records, never silently discard rows."""
import hashlib
import pandas as pd
import numpy as np
from common import ROOT, PROCESSED, STATUSES, save_json

def transform(source):
    d = pd.read_csv(source, keep_default_na=False)
    d = d.rename(columns={'checkin_date':'check_in_date','checkout_date':'check_out_date',
        'nights':'number_of_nights','cost':'estimated_cost','hotel':'hotel_name','country':'source_country'})
    for col in d.select_dtypes(include=['object','string']).columns:
        d[col] = d[col].str.strip()
    for col in ['booking_date','check_in_date','check_out_date']:
        d[col] = pd.to_datetime(d[col], errors='coerce')
    for col in ['room_rate','discount_amount','revenue','estimated_cost','profit']:
        d[col+'_cents'] = np.rint(pd.to_numeric(d[col],errors='raise')*100).astype('int64')
    d['total_booking_amount_cents'] = d.room_rate_cents*d.number_of_nights
    d['customer_segment'] = d.customer_segment.replace('', 'Unknown')
    hotels = d[['hotel_name','region']].drop_duplicates().sort_values(['hotel_name','region']).reset_index(drop=True)
    hotels['hotel_id'] = ['H%03d'%i for i in range(1,len(hotels)+1)]
    for col in ['city','country','hotel_category']: hotels[col] = 'Unknown'
    channels = pd.DataFrame({'channel_name':sorted(d.booking_channel.unique())})
    channels['channel_id'] = range(1,len(channels)+1)
    channels['commission_rate'] = np.nan
    customers = pd.DataFrame({'customer_id':sorted(d.customer_id.unique())})
    customers['customer_name'] = customers.customer_id  # identifier, not fabricated name
    customers['country'] = 'Unknown'
    customers['registration_date'] = None
    customers['customer_segment'] = 'Booking-level; see fact'
    d = d.merge(hotels[['hotel_name','region','hotel_id']],on=['hotel_name','region'],validate='many_to_one')
    d = d.merge(channels[['channel_id','channel_name']],left_on='booking_channel',right_on='channel_name',validate='many_to_one')
    d['number_of_guests'] = pd.NA
    completed = d.booking_status.eq('Completed')
    checks = {
        'duplicate_booking_id':d.booking_id.duplicated(keep=False),
        'missing_customer_reference':~d.customer_id.isin(customers.customer_id) | d.customer_id.eq(''),
        'missing_hotel_reference':~d.hotel_id.isin(hotels.hotel_id) | d.hotel_name.eq(''),
        'invalid_dates':d[['booking_date','check_in_date','check_out_date']].isna().any(axis=1) | (d.booking_date>d.check_in_date) | (d.check_out_date<=d.check_in_date),
        'nights_mismatch':d.number_of_nights.ne((d.check_out_date-d.check_in_date).dt.days),
        'lead_time_mismatch':d.lead_time_days.ne((d.check_in_date-d.booking_date).dt.days),
        'invalid_money':(d.room_rate_cents<=0) | (d.total_booking_amount_cents<0) | (d.discount_amount_cents<0) | (d.discount_amount_cents>d.total_booking_amount_cents) | (d.estimated_cost_cents<0),
        'invalid_status':~d.booking_status.isin(STATUSES),
        'missing_channel':~d.channel_id.isin(channels.channel_id) | d.booking_channel.eq(''),
        'revenue_discrepancy':d.revenue_cents.ne(np.where(completed,d.total_booking_amount_cents-d.discount_amount_cents,0)),
        'profit_discrepancy':d.profit_cents.ne(d.revenue_cents-d.estimated_cost_cents),
        'noncompleted_cost':~completed & d.estimated_cost_cents.ne(0),
        'unexpected_dates':~d.booking_date.between('2025-01-01','2026-08-31') | ~d.check_out_date.between('2025-01-02','2026-12-31'),
    }
    return d, hotels, customers, channels, checks

def main():
    source = ROOT/'data/raw/bookings_source.csv'
    d,h,c,ch,checks = transform(source)
    issues = {k:int(v.sum()) for k,v in checks.items()}
    bad = pd.Series(False,index=d.index)
    for mask in checks.values(): bad |= mask
    (ROOT/'reports').mkdir(exist_ok=True)
    save_json(ROOT/'reports/data_quality.json', {'rows_checked':len(d),'checks':issues,'invalid_rows':int(bad.sum()),
        'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'unavailable':{'registration_date':len(c),'commission_rate':len(ch),'number_of_guests':len(d)},
        'country_conflict_hotels':int((d.groupby('hotel_id').source_country.nunique()>1).sum()),
        'segment_changes_customers':int((d.groupby('customer_id').customer_segment.nunique()>1).sum())})
    if bad.any():
        d[bad].to_csv(ROOT/'reports/rejected_records.csv',index=False)
        raise ValueError('Core validation failed: raw preserved; see reports. Processed refresh aborted.')
    PROCESSED.mkdir(parents=True,exist_ok=True)
    money = ['room_rate','discount_amount','revenue','estimated_cost','profit','total_booking_amount']
    for col in money: d[col] = d[col+'_cents']/100
    columns = ['booking_id','customer_id','hotel_id','channel_id','booking_date','check_in_date','check_out_date',
        'room_type','booking_channel','booking_status','number_of_guests','number_of_nights','lead_time_days',
        'customer_segment','source_country'] + [x for col in money for x in [col,col+'_cents']]
    d[columns].to_csv(PROCESSED/'bookings.csv',index=False,date_format='%Y-%m-%d')
    for name,frame in [('hotels',h),('customers',c),('channels',ch)]: frame.to_csv(PROCESSED/f'{name}.csv',index=False)
    dates = pd.DataFrame({'date':pd.date_range('2024-01-01','2027-12-31')})
    dates['date_key'] = dates.date.dt.strftime('%Y%m%d').astype(int)
    dates['year'] = dates.date.dt.year; dates['month_number']=dates.date.dt.month
    dates['month_name']=dates.date.dt.strftime('%B'); dates['year_month']=dates.date.dt.strftime('%Y-%m')
    dates['quarter']=dates.date.dt.quarter
    dates.to_csv(PROCESSED/'dates.csv',index=False,date_format='%Y-%m-%d')
    text = '# Data quality report\n\nSource: supplied HRS practice CSV; provenance and currency unverified. Never actual HP performance.\n\n'
    text += f'{len(d):,} rows checked; {int(bad.sum())} invalid rows. No rows removed. Whitespace trimmed; money converted to integer cents; original file retained byte-for-byte.\n\n'
    text += '| Check | Issues |\n|---|---:|\n'+''.join(f'|{k}|{v}|\n' for k,v in issues.items())
    text += '\nRegistration dates unavailable: cannot validate; not imputed. Guest counts, city, category and commissions unavailable. Customer name uses ID only.\n\n'
    text += 'Country varies within hotels and is retained as ambiguous source_country on fact; do not interpret it as verified hotel/customer nationality. Segment is booking-level because customer IDs span segments. Hotel location/category unknown. No currency conversion is possible: all monetary totals assume a common unspecified source unit (CU). Costs are source estimates, not audited expenses.\n\n'
    text += f"| Non-blocking source limitation | Affected entities | Action |\n|---|---:|---|\n|Multiple country labels per hotel|{int((d.groupby('hotel_id').source_country.nunique()>1).sum())}|Keep ambiguous source_country on fact; hotel country Unknown|\n|Multiple segments per customer|{int((d.groupby('customer_id').customer_segment.nunique()>1).sum())}|Retain segment at booking grain|\n|Unavailable registration date|{len(c)}|Null; validation not possible|\n|Unavailable commission rate|{len(ch)}|Null; no invented ROI|\n|Unavailable guest count|{len(d)}|Null; no guest-based metric|\n\n"
    text += 'Source dates 2025–2026 retained instead of fabricating 2023–2025 history. Allowed booking-date contract: 2025-01-01 through 2026-08-31; checkout through 2026-12-31. Update contract deliberately for new extracts. Future registration dates must be <= booking date if supplied. See data_quality.json for exact counts and source hash.\n'
    (ROOT/'reports/data_quality_report.md').write_text(text,encoding='utf-8')
    print(f'Validated and exported {len(d)} bookings; {sum(issues.values())} core issues')

if __name__=='__main__': main()
