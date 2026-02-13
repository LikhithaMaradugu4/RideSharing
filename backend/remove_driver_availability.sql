-- SQL Script to remove driver_work_availability functionality
-- Run this script to drop the driver_work_availability table

-- Drop the table and sequence
DROP TABLE IF EXISTS driver_work_availability CASCADE;
DROP SEQUENCE IF EXISTS driver_work_availability_id_seq CASCADE;

-- Verify removal
-- SELECT table_name FROM information_schema.tables WHERE table_name = 'driver_work_availability';
