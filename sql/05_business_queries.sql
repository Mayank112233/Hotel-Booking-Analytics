USE hotel_booking_analytics;
-- Q1 Total bookings: distinct identifiers protect the intended booking grain.
SELECT COUNT(DISTINCT booking_id) AS total_bookings FROM bookings;
-- Q2 Completed bookings: excludes cancelled, no-show, pending and refunded.
SELECT COUNT(*) AS completed_bookings FROM bookings WHERE booking_status='Completed';
-- Q3 Total realized room revenue, in unspecified source currency units (CU).
SELECT SUM(revenue) AS total_revenue FROM bookings;
-- Q4 Profit: source revenue less source estimated costs.
SELECT SUM(profit) AS total_profit FROM bookings;
-- Q5 ABV: realized revenue per completed stay, not per all reservations.
SELECT SUM(revenue)/NULLIF(SUM(CASE WHEN booking_status='Completed' THEN 1 ELSE 0 END),0) AS average_booking_value FROM bookings;
-- Q6 Which channels contribute revenue? Costs do not include invented commission.
SELECT c.channel_name,SUM(b.revenue) AS revenue FROM bookings b JOIN channels c USING(channel_id) GROUP BY c.channel_name ORDER BY revenue DESC;
-- Q7 Booking demand by region: includes all statuses.
SELECT h.region,COUNT(*) AS bookings FROM bookings b JOIN hotels h USING(hotel_id) GROUP BY h.region ORDER BY bookings DESC;
-- Q8 Highest source-country label by revenue. Ambiguous geography, NOT verified hotel/customer country.
SELECT source_country,SUM(revenue) AS revenue FROM bookings GROUP BY source_country ORDER BY revenue DESC,source_country LIMIT 1;
-- Q9 Most booked hotel; deterministic tie breaker.
SELECT h.hotel_name,COUNT(*) AS bookings FROM bookings b JOIN hotels h USING(hotel_id) GROUP BY h.hotel_id,h.hotel_name ORDER BY bookings DESC,h.hotel_id LIMIT 1;
-- Q10 Mean quoted nightly rate by room type, all statuses; differs from realized ADR.
SELECT room_type,AVG(room_rate) AS mean_quoted_rate FROM bookings GROUP BY room_type;
