USE hotel_booking_analytics;
-- All issue counts should be zero; registration_unavailable is informational.
SELECT 'duplicate_booking_id' AS check_name, COUNT(*) AS issues FROM
 (SELECT booking_id FROM bookings GROUP BY booking_id HAVING COUNT(*)>1) x
UNION ALL SELECT 'missing_customer', COUNT(*) FROM bookings b LEFT JOIN customers c USING(customer_id) WHERE c.customer_id IS NULL
UNION ALL SELECT 'missing_hotel', COUNT(*) FROM bookings b LEFT JOIN hotels h USING(hotel_id) WHERE h.hotel_id IS NULL
UNION ALL SELECT 'missing_channel', COUNT(*) FROM bookings b LEFT JOIN channels c USING(channel_id) WHERE c.channel_id IS NULL
UNION ALL SELECT 'invalid_dates', COUNT(*) FROM bookings WHERE booking_date>check_in_date OR check_out_date<=check_in_date OR number_of_nights<>DATEDIFF(check_out_date,check_in_date)
UNION ALL SELECT 'negative_money', COUNT(*) FROM bookings WHERE room_rate_cents<=0 OR total_booking_amount_cents<0 OR estimated_cost_cents<0
UNION ALL SELECT 'invalid_status', COUNT(*) FROM bookings WHERE booking_status NOT IN ('Completed','Cancelled','No Show','Pending','Refunded')
UNION ALL SELECT 'revenue_discrepancy', COUNT(*) FROM bookings WHERE revenue_cents<>CASE WHEN booking_status='Completed' THEN total_booking_amount_cents-discount_amount_cents ELSE 0 END
UNION ALL SELECT 'profit_discrepancy', COUNT(*) FROM bookings WHERE profit_cents<>revenue_cents-estimated_cost_cents
UNION ALL SELECT 'invalid_registration', COUNT(*) FROM bookings b JOIN customers c USING(customer_id) WHERE c.registration_date>b.booking_date
UNION ALL SELECT 'unexpected_dates', COUNT(*) FROM bookings WHERE booking_date NOT BETWEEN '2025-01-01' AND '2026-08-31' OR check_out_date>'2026-12-31';
SELECT COUNT(*) AS registration_unavailable FROM customers WHERE registration_date IS NULL;
