-- Migration: Add Document Rejection Support
-- Date: 2026-02-17
-- Description: Adds rejection_reason column to user_kyc and PARTIALLY_REJECTED status

-- Add rejection_reason column to user_kyc table
ALTER TABLE user_kyc ADD COLUMN IF NOT EXISTS rejection_reason TEXT;

-- Add PARTIALLY_REJECTED status to lu_approval_status lookup table
INSERT INTO lu_approval_status (status_code) VALUES ('PARTIALLY_REJECTED')
ON CONFLICT (status_code) DO NOTHING;

-- Comment for documentation
COMMENT ON COLUMN user_kyc.rejection_reason IS 'Reason provided when document is rejected by tenant admin';

