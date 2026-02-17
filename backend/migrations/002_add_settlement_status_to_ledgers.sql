-- Migration: Add settlement_status to platform_ledger, tenant_ledger, fleet_ledger
-- Date: 2024
-- Purpose: Track settlement status for all ledger types so that when driver settles,
--          we can mark all related ledger entries (driver, platform, tenant, fleet) as settled.

-- ================================================================
-- STEP 1: Create the ledger tables if they don't exist
-- ================================================================

-- Platform Ledger Table
CREATE TABLE IF NOT EXISTS platform_ledger (
    entry_id BIGSERIAL PRIMARY KEY,
    trip_id BIGINT REFERENCES trip(trip_id),
    currency CHAR(3) NOT NULL,
    amount NUMERIC(12,2) NOT NULL,
    entry_type TEXT NOT NULL,  -- CREDIT / DEBIT
    reason TEXT,
    settlement_status TEXT DEFAULT 'unsettled',  -- unsettled | settled
    created_on TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Tenant Ledger Table
CREATE TABLE IF NOT EXISTS tenant_ledger (
    entry_id BIGSERIAL PRIMARY KEY,
    tenant_id BIGINT NOT NULL REFERENCES tenant(tenant_id),
    trip_id BIGINT REFERENCES trip(trip_id),
    currency CHAR(3) NOT NULL,
    amount NUMERIC(12,2) NOT NULL,
    entry_type TEXT NOT NULL,
    reason TEXT,
    settlement_status TEXT DEFAULT 'unsettled',  -- unsettled | settled
    created_on TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Fleet Ledger Table
CREATE TABLE IF NOT EXISTS fleet_ledger (
    entry_id BIGSERIAL PRIMARY KEY,
    fleet_id BIGINT NOT NULL REFERENCES fleet(fleet_id),
    trip_id BIGINT REFERENCES trip(trip_id),
    currency CHAR(3) NOT NULL,
    amount NUMERIC(12,2) NOT NULL,
    entry_type TEXT NOT NULL,
    reason TEXT,
    settlement_status TEXT DEFAULT 'unsettled',  -- unsettled | settled
    created_on TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- ================================================================
-- STEP 2: Add settlement_status column if tables already exist
-- ================================================================

-- Add settlement_status to platform_ledger if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'platform_ledger' AND column_name = 'settlement_status'
    ) THEN
        ALTER TABLE platform_ledger ADD COLUMN settlement_status TEXT DEFAULT 'unsettled';
    END IF;
END $$;

-- Add settlement_status to tenant_ledger if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'tenant_ledger' AND column_name = 'settlement_status'
    ) THEN
        ALTER TABLE tenant_ledger ADD COLUMN settlement_status TEXT DEFAULT 'unsettled';
    END IF;
END $$;

-- Add settlement_status to fleet_ledger if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'fleet_ledger' AND column_name = 'settlement_status'
    ) THEN
        ALTER TABLE fleet_ledger ADD COLUMN settlement_status TEXT DEFAULT 'unsettled';
    END IF;
END $$;

-- ================================================================
-- STEP 3: Create indexes for better query performance
-- ================================================================

-- Index on platform_ledger for faster settlement status queries
CREATE INDEX IF NOT EXISTS idx_platform_ledger_trip_status 
ON platform_ledger(trip_id, settlement_status);

-- Index on tenant_ledger for faster settlement status queries
CREATE INDEX IF NOT EXISTS idx_tenant_ledger_trip_status 
ON tenant_ledger(trip_id, settlement_status);

CREATE INDEX IF NOT EXISTS idx_tenant_ledger_tenant_status 
ON tenant_ledger(tenant_id, settlement_status);

-- Index on fleet_ledger for faster settlement status queries
CREATE INDEX IF NOT EXISTS idx_fleet_ledger_trip_status 
ON fleet_ledger(trip_id, settlement_status);

CREATE INDEX IF NOT EXISTS idx_fleet_ledger_fleet_status 
ON fleet_ledger(fleet_id, settlement_status);

-- ================================================================
-- STEP 4: Create driver_wallet table if not exists
-- ================================================================

CREATE TABLE IF NOT EXISTS driver_wallet (
    wallet_id BIGSERIAL PRIMARY KEY,
    driver_id BIGINT NOT NULL REFERENCES app_user(user_id),
    currency CHAR(3) NOT NULL DEFAULT 'INR',
    balance NUMERIC(12,2) NOT NULL DEFAULT 0,
    created_on TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_on TIMESTAMP WITH TIME ZONE,
    UNIQUE(driver_id, currency)
);

-- ================================================================
-- STEP 5: Ensure driver_ledger has settlement_status
-- ================================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'driver_ledger' AND column_name = 'settlement_status'
    ) THEN
        ALTER TABLE driver_ledger ADD COLUMN settlement_status TEXT DEFAULT 'unsettled';
    END IF;
END $$;

-- Index on driver_ledger for faster queries
CREATE INDEX IF NOT EXISTS idx_driver_ledger_settlement 
ON driver_ledger(driver_id, settlement_status, trip_id);

-- ================================================================
-- VERIFICATION QUERIES (run these to verify)
-- ================================================================

-- SELECT column_name, data_type, column_default 
-- FROM information_schema.columns 
-- WHERE table_name IN ('platform_ledger', 'tenant_ledger', 'fleet_ledger', 'driver_ledger')
-- AND column_name = 'settlement_status';

-- SELECT 'platform_ledger' as table_name, COUNT(*) as count FROM platform_ledger
-- UNION ALL SELECT 'tenant_ledger', COUNT(*) FROM tenant_ledger
-- UNION ALL SELECT 'fleet_ledger', COUNT(*) FROM fleet_ledger
-- UNION ALL SELECT 'driver_ledger', COUNT(*) FROM driver_ledger;
