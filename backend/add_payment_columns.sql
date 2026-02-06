-- Add missing columns to payment table for CASH-ONLY payment confirmation
-- These columns are required by the Payment model for our cash payment system

-- Add confirmed_by_driver_id column (references app_user.user_id)
-- This tracks which driver confirmed they received the cash payment
ALTER TABLE payment 
ADD COLUMN confirmed_by_driver_id bigint REFERENCES app_user(user_id);

-- Add confirmed_at column for timestamp when driver confirms cash received
ALTER TABLE payment 
ADD COLUMN confirmed_at timestamp with time zone;

-- Verify the payment table structure
\d payment;