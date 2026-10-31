USE hotel_booking_analytics;
-- Q11 Second distinct hotel revenue rank; return all ties using DENSE_RANK.
WITH totals AS (SELECT hotel_id,SUM(revenue) AS revenue FROM bookings GROUP BY hotel_id),
 ranked AS (SELECT *,DENSE_RANK() OVER(ORDER BY revenue DESC) AS revenue_rank FROM totals)
SELECT h.hotel_name,r.revenue FROM ranked r JOIN hotels h USING(hotel_id) WHERE revenue_rank=2;
-- Q12 Exactly three hotels within each region; stable ordering resolves ties.
WITH totals AS (SELECT h.region,h.hotel_id,h.hotel_name,SUM(b.revenue) AS revenue FROM bookings b JOIN hotels h USING(hotel_id) GROUP BY h.region,h.hotel_id,h.hotel_name),
 ranked AS (SELECT *,ROW_NUMBER() OVER(PARTITION BY region ORDER BY revenue DESC,hotel_id) AS position FROM totals)
SELECT * FROM ranked WHERE position<=3 ORDER BY region,position;
-- Q13 Customers with more than five completed stays.
SELECT customer_id,COUNT(*) AS completed_stays FROM bookings WHERE booking_status='Completed' GROUP BY customer_id HAVING COUNT(*)>5;
-- Q14 Average revenue per revenue-eligible customer, includes customers whose completed stays net to zero.
SELECT SUM(revenue)/NULLIF(COUNT(DISTINCT CASE WHEN booking_status='Completed' THEN customer_id END),0) AS average_revenue_per_customer FROM bookings;
-- Q15 Cancellation rate per channel: No Show remains a separate status in denominator.
SELECT c.channel_name,AVG(CASE WHEN booking_status='Cancelled' THEN 1.0 ELSE 0 END) AS cancellation_rate,COUNT(*) AS bookings FROM bookings b JOIN channels c USING(channel_id) GROUP BY c.channel_name;
-- Q16 Highest arrival month revenue. Group year AND month to avoid mixing years.
SELECT DATE_FORMAT(check_in_date,'%Y-%m') AS arrival_month,SUM(revenue) AS revenue FROM bookings GROUP BY arrival_month ORDER BY revenue DESC,arrival_month LIMIT 1;
-- Q17 Top five customers, deterministic ranking; RANK also reports tied revenues.
WITH totals AS (SELECT customer_id,SUM(revenue) AS revenue FROM bookings GROUP BY customer_id)
SELECT *,RANK() OVER(ORDER BY revenue DESC) AS revenue_rank FROM totals ORDER BY revenue DESC,customer_id LIMIT 5;
-- Q18 Hotels with completed-stay average revenue above overall completed-stay average.
SELECT h.hotel_name,AVG(b.revenue) AS abv FROM bookings b JOIN hotels h USING(hotel_id) WHERE b.booking_status='Completed' GROUP BY h.hotel_id,h.hotel_name HAVING AVG(b.revenue)>(SELECT AVG(revenue) FROM bookings WHERE booking_status='Completed');
-- Q19 Most profitable booking-level customer segment; do not assign static segment to customer dimension.
SELECT customer_segment,SUM(profit) AS profit FROM bookings GROUP BY customer_segment ORDER BY profit DESC,customer_segment LIMIT 1;
-- Q20 Channel with highest completed-stay ABV.
SELECT c.channel_name,AVG(b.revenue) AS abv FROM bookings b JOIN channels c USING(channel_id) WHERE b.booking_status='Completed' GROUP BY c.channel_name ORDER BY abv DESC,c.channel_name LIMIT 1;
-- Additional: calendar-complete monthly revenue and prior-month growth (no skipped empty months).
WITH monthly AS (SELECT d.year_month,COALESCE(SUM(b.revenue),0) AS revenue FROM dates d LEFT JOIN bookings b ON b.check_in_date=d.date GROUP BY d.year_month),
 lagged AS (SELECT *,LAG(revenue) OVER(ORDER BY `year_month`) AS previous_month FROM monthly)
SELECT *, (revenue-previous_month)/NULLIF(previous_month,0) AS mom FROM lagged ORDER BY `year_month`;
