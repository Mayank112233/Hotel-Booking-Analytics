USE hotel_booking_analytics;
-- Portable loading entry point: python python/load_database.py
-- Executes 01,02, this file, transactional dimension/fact refresh, then 07.
-- No server-local CSV paths or LOCAL INFILE permissions required.
-- Never disable foreign key checking. INSERT parameters are supplied by SQLAlchemy.
SELECT 'Load CSV tables with python/load_database.py (see README)' AS loading_instruction;
