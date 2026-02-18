-- Migration: Add rejection_reason column to fleet_document table
-- This enables per-document rejection with reasons (matching UserKYC pattern)

ALTER TABLE fleet_document ADD COLUMN IF NOT EXISTS rejection_reason TEXT;
