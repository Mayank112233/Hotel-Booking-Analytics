USE hotel_booking_analytics;
-- Independent calculations from prices/dates, compared with the analytics KPI view.
WITH completed AS (
 SELECT *, (room_rate_cents*DATEDIFF(check_out_date,check_in_date)-discount_amount_cents)/100.0 AS earned
 FROM bookings WHERE booking_status='Completed'
), stays AS (
 SELECT customer_id,COUNT(*) AS n FROM completed GROUP BY customer_id
), expected AS (
 SELECT
 (SELECT COUNT(DISTINCT booking_id) FROM bookings) AS total_bookings,
 (SELECT COUNT(*) FROM completed) AS completed_bookings,
 (SELECT SUM(earned) FROM completed) AS total_revenue,
 (SELECT SUM(earned-estimated_cost_cents/100.0) FROM completed) AS total_profit,
 (SELECT AVG(earned) FROM completed) AS average_booking_value,
 (SELECT AVG(CASE WHEN booking_status='Cancelled' THEN 1.0000000000 ELSE 0 END) FROM bookings) AS cancellation_rate,
 (SELECT 1-SUM(estimated_cost_cents/100.0)/NULLIF(SUM(earned),0) FROM completed) AS profit_margin,
 (SELECT 1.0000000000*SUM(earned)/NULLIF(SUM(DATEDIFF(check_out_date,check_in_date)),0) FROM completed) AS average_daily_rate,
 (SELECT AVG(1.0000000000*DATEDIFF(check_out_date,check_in_date)) FROM completed) AS average_length_of_stay,
 (SELECT AVG(CASE WHEN n>1 THEN 1.0000000000 ELSE 0 END) FROM stays) AS repeat_customer_rate
)
SELECT ABS(e.total_bookings-k.total_bookings)<0.000001 AS total_bookings_pass,
 ABS(e.completed_bookings-k.completed_bookings)<0.000001 AS completed_bookings_pass,
 ABS(e.total_revenue-k.total_revenue)<0.000001 AS total_revenue_pass,
 ABS(e.total_profit-k.total_profit)<0.000001 AS total_profit_pass,
 ABS(e.average_booking_value-k.average_booking_value)<0.000001 AS average_booking_value_pass,
 ABS(e.cancellation_rate-k.cancellation_rate)<0.000001 AS cancellation_rate_pass,
 ABS(e.profit_margin-k.profit_margin)<0.000001 AS profit_margin_pass,
 ABS(e.average_daily_rate-k.average_daily_rate)<0.000001 AS average_daily_rate_pass,
 ABS(e.average_length_of_stay-k.average_length_of_stay)<0.000001 AS average_length_of_stay_pass,
 ABS(e.repeat_customer_rate-k.repeat_customer_rate)<0.000001 AS repeat_customer_rate_pass
FROM expected e CROSS JOIN vw_kpis k;
