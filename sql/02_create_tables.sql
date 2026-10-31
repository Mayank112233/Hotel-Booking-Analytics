USE hotel_booking_analytics;
CREATE TABLE IF NOT EXISTS hotels (
 hotel_id VARCHAR(8) PRIMARY KEY, hotel_name VARCHAR(120) NOT NULL,
 region VARCHAR(50) NOT NULL, city VARCHAR(80) NOT NULL,
 country VARCHAR(80) NOT NULL, hotel_category VARCHAR(50) NOT NULL,
 UNIQUE KEY uq_hotel (hotel_name,region)
);
CREATE TABLE IF NOT EXISTS customers (
 customer_id VARCHAR(20) PRIMARY KEY, customer_name VARCHAR(80) NOT NULL,
 country VARCHAR(80) NOT NULL, registration_date DATE NULL,
 customer_segment VARCHAR(50) NOT NULL
);
CREATE TABLE IF NOT EXISTS channels (
 channel_id INT PRIMARY KEY, channel_name VARCHAR(50) NOT NULL UNIQUE,
 commission_rate DECIMAL(6,5) NULL,
 CHECK (commission_rate IS NULL OR commission_rate BETWEEN 0 AND 1)
);
CREATE TABLE IF NOT EXISTS dates (
 date DATE PRIMARY KEY, date_key INT NOT NULL UNIQUE, year INT NOT NULL,
 month_number INT NOT NULL, month_name VARCHAR(12) NOT NULL,
 `year_month` CHAR(7) NOT NULL, quarter INT NOT NULL
);
CREATE TABLE IF NOT EXISTS bookings (
 booking_id VARCHAR(20) PRIMARY KEY,
 customer_id VARCHAR(20) NOT NULL, hotel_id VARCHAR(8) NOT NULL, channel_id INT NOT NULL,
 booking_date DATE NOT NULL, check_in_date DATE NOT NULL, check_out_date DATE NOT NULL,
 room_type VARCHAR(30) NOT NULL, booking_status VARCHAR(12) NOT NULL,
 number_of_guests INT NULL, number_of_nights INT NOT NULL, lead_time_days INT NOT NULL,
 customer_segment VARCHAR(50) NOT NULL, source_country VARCHAR(80) NOT NULL,
 room_rate_cents BIGINT NOT NULL, total_booking_amount_cents BIGINT NOT NULL,
 discount_amount_cents BIGINT NOT NULL, revenue_cents BIGINT NOT NULL,
 estimated_cost_cents BIGINT NOT NULL, profit_cents BIGINT NOT NULL,
 room_rate DECIMAL(14,2) GENERATED ALWAYS AS (room_rate_cents / 100.0) STORED,
 total_booking_amount DECIMAL(14,2) GENERATED ALWAYS AS (total_booking_amount_cents / 100.0) STORED,
 discount_amount DECIMAL(14,2) GENERATED ALWAYS AS (discount_amount_cents / 100.0) STORED,
 revenue DECIMAL(14,2) GENERATED ALWAYS AS (revenue_cents / 100.0) STORED,
 estimated_cost DECIMAL(14,2) GENERATED ALWAYS AS (estimated_cost_cents / 100.0) STORED,
 profit DECIMAL(14,2) GENERATED ALWAYS AS (profit_cents / 100.0) STORED,
 FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
 FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id),
 FOREIGN KEY (channel_id) REFERENCES channels(channel_id),
 FOREIGN KEY (check_in_date) REFERENCES dates(date),
 FOREIGN KEY (booking_date) REFERENCES dates(date),
 FOREIGN KEY (check_out_date) REFERENCES dates(date),
 CHECK (booking_status IN ('Completed','Cancelled','No Show','Pending','Refunded')),
 CHECK (booking_date <= check_in_date AND check_out_date > check_in_date),
 CHECK (number_of_nights = DATEDIFF(check_out_date,check_in_date)),
 CHECK (lead_time_days = DATEDIFF(check_in_date,booking_date)),
 CHECK (number_of_guests IS NULL OR number_of_guests > 0),
 CHECK (room_rate_cents > 0 AND estimated_cost_cents >= 0),
 CHECK (total_booking_amount_cents = room_rate_cents * number_of_nights),
 CHECK (discount_amount_cents BETWEEN 0 AND total_booking_amount_cents),
 CHECK (revenue_cents = CASE WHEN booking_status='Completed' THEN total_booking_amount_cents-discount_amount_cents ELSE 0 END),
 CHECK (booking_status='Completed' OR estimated_cost_cents=0),
 CHECK (profit_cents = revenue_cents-estimated_cost_cents),
 INDEX ix_arrival (check_in_date), INDEX ix_booking_date (booking_date),
 INDEX ix_status_channel (booking_status,channel_id), INDEX ix_hotel_arrival (hotel_id,check_in_date)
);
