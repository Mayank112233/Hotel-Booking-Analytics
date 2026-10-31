USE hotel_booking_analytics;
-- Import these into Power BI; avoid merging dimensions back into the fact.
CREATE OR REPLACE VIEW vw_fact_bookings AS
SELECT b.*,DATEDIFF(check_in_date,booking_date) AS booking_lead_days,
 CASE WHEN lead_time_days<7 THEN '00-06' WHEN lead_time_days<14 THEN '07-13' WHEN lead_time_days<30 THEN '14-29' ELSE '30+' END AS lead_time_band
FROM bookings b;
CREATE OR REPLACE VIEW vw_dim_hotels AS SELECT * FROM hotels;
CREATE OR REPLACE VIEW vw_dim_customers AS SELECT * FROM customers;
CREATE OR REPLACE VIEW vw_dim_channels AS SELECT * FROM channels;
CREATE OR REPLACE VIEW vw_dim_date AS SELECT * FROM dates;
CREATE OR REPLACE VIEW vw_monthly_performance AS
SELECT d.year_month,COUNT(b.booking_id) AS total_bookings,
 SUM(CASE WHEN b.booking_status='Completed' THEN 1 ELSE 0 END) AS completed_bookings,
 COALESCE(SUM(b.revenue),0) AS revenue,COALESCE(SUM(b.profit),0) AS profit,
 SUM(CASE WHEN b.booking_status='Cancelled' THEN 1 ELSE 0 END)/NULLIF(COUNT(b.booking_id),0) AS cancellation_rate
FROM dates d LEFT JOIN bookings b ON b.check_in_date=d.date GROUP BY d.year_month;
CREATE OR REPLACE VIEW vw_kpis AS
SELECT COUNT(*) AS total_bookings,
 SUM(CASE WHEN booking_status='Completed' THEN 1 ELSE 0 END) AS completed_bookings,
 SUM(CASE WHEN booking_status='Cancelled' THEN 1 ELSE 0 END) AS cancelled_bookings,
 SUM(revenue) AS total_revenue,SUM(profit) AS total_profit,
 1.0000000000*SUM(revenue)/NULLIF(SUM(CASE WHEN booking_status='Completed' THEN 1 ELSE 0 END),0) AS average_booking_value,
 1.0000000000*SUM(CASE WHEN booking_status='Cancelled' THEN 1 ELSE 0 END)/NULLIF(COUNT(*),0) AS cancellation_rate,
 1.0000000000*SUM(profit)/NULLIF(SUM(revenue),0) AS profit_margin,
 1.0000000000*SUM(revenue)/NULLIF(SUM(CASE WHEN booking_status='Completed' THEN number_of_nights ELSE 0 END),0) AS average_daily_rate,
 AVG(CASE WHEN booking_status='Completed' THEN 1.0000000000*number_of_nights END) AS average_length_of_stay,
 (SELECT AVG(CASE WHEN stays>1 THEN 1.0000000000 ELSE 0 END) FROM (SELECT customer_id,COUNT(*) AS stays FROM bookings WHERE booking_status='Completed' GROUP BY customer_id) counts) AS repeat_customer_rate
FROM bookings;
