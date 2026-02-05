-- ============================================================================
-- CASH-ONLY SETTLEMENT: Database Schema and Wallet Triggers
-- ============================================================================
-- This script creates:
-- 1. Missing tables (driver_ledger, fleet_wallet)
-- 2. AFTER INSERT triggers for automatic wallet updates
--
-- IMPORTANT: Wallet updates are ONLY done via triggers, NOT in application code.
-- ============================================================================

-- ============================================================================
-- 1. CREATE MISSING TABLES
-- ============================================================================

-- Driver Ledger table (if not exists)
CREATE TABLE IF NOT EXISTS driver_ledger (
    entry_id BIGSERIAL PRIMARY KEY,
    driver_id BIGINT NOT NULL REFERENCES app_user(user_id),
    trip_id BIGINT REFERENCES trip(trip_id),
    currency CHAR(3) NOT NULL,
    amount NUMERIC(12,2) NOT NULL,
    entry_type TEXT NOT NULL,  -- CREDIT / DEBIT
    reason TEXT,
    created_on TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Fleet Wallet table (if not exists)
CREATE TABLE IF NOT EXISTS fleet_wallet (
    fleet_id BIGINT NOT NULL REFERENCES fleet(fleet_id),
    currency CHAR(3) NOT NULL,
    balance NUMERIC(12,2) NOT NULL DEFAULT 0,
    created_on TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_on TIMESTAMPTZ,
    PRIMARY KEY (fleet_id, currency)
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_driver_ledger_driver_id ON driver_ledger(driver_id);
CREATE INDEX IF NOT EXISTS idx_driver_ledger_trip_id ON driver_ledger(trip_id);
CREATE INDEX IF NOT EXISTS idx_fleet_wallet_fleet_id ON fleet_wallet(fleet_id);


-- ============================================================================
-- 2. WALLET TRIGGER FUNCTIONS
-- ============================================================================
-- All triggers follow the same pattern:
-- - CREDIT → add amount to balance
-- - DEBIT → subtract amount from balance
-- - Create wallet if not exists
-- - Negative balances allowed
-- - NO business logic in triggers
-- ============================================================================

-- Platform Wallet Trigger Function
CREATE OR REPLACE FUNCTION update_platform_wallet_from_ledger()
RETURNS TRIGGER AS $$
BEGIN
    -- Insert wallet if not exists
    INSERT INTO platform_wallet (currency, balance, created_on)
    VALUES (NEW.currency, 0, NOW())
    ON CONFLICT (currency) DO NOTHING;
    
    -- Update balance based on entry_type
    IF NEW.entry_type = 'CREDIT' THEN
        UPDATE platform_wallet
        SET balance = balance + NEW.amount,
            updated_on = NOW()
        WHERE currency = NEW.currency;
    ELSIF NEW.entry_type = 'DEBIT' THEN
        UPDATE platform_wallet
        SET balance = balance - NEW.amount,
            updated_on = NOW()
        WHERE currency = NEW.currency;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- Tenant Wallet Trigger Function
CREATE OR REPLACE FUNCTION update_tenant_wallet_from_ledger()
RETURNS TRIGGER AS $$
BEGIN
    -- Insert wallet if not exists
    INSERT INTO tenant_wallet (tenant_id, currency, balance, created_on)
    VALUES (NEW.tenant_id, NEW.currency, 0, NOW())
    ON CONFLICT (tenant_id, currency) DO NOTHING;
    
    -- Update balance based on entry_type
    IF NEW.entry_type = 'CREDIT' THEN
        UPDATE tenant_wallet
        SET balance = balance + NEW.amount,
            updated_on = NOW()
        WHERE tenant_id = NEW.tenant_id AND currency = NEW.currency;
    ELSIF NEW.entry_type = 'DEBIT' THEN
        UPDATE tenant_wallet
        SET balance = balance - NEW.amount,
            updated_on = NOW()
        WHERE tenant_id = NEW.tenant_id AND currency = NEW.currency;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- Fleet Wallet Trigger Function
CREATE OR REPLACE FUNCTION update_fleet_wallet_from_ledger()
RETURNS TRIGGER AS $$
BEGIN
    -- Insert wallet if not exists
    INSERT INTO fleet_wallet (fleet_id, currency, balance, created_on)
    VALUES (NEW.fleet_id, NEW.currency, 0, NOW())
    ON CONFLICT (fleet_id, currency) DO NOTHING;
    
    -- Update balance based on entry_type
    IF NEW.entry_type = 'CREDIT' THEN
        UPDATE fleet_wallet
        SET balance = balance + NEW.amount,
            updated_on = NOW()
        WHERE fleet_id = NEW.fleet_id AND currency = NEW.currency;
    ELSIF NEW.entry_type = 'DEBIT' THEN
        UPDATE fleet_wallet
        SET balance = balance - NEW.amount,
            updated_on = NOW()
        WHERE fleet_id = NEW.fleet_id AND currency = NEW.currency;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- Driver Wallet Trigger Function
CREATE OR REPLACE FUNCTION update_driver_wallet_from_ledger()
RETURNS TRIGGER AS $$
BEGIN
    -- Insert wallet if not exists
    INSERT INTO driver_wallet (driver_id, currency, balance, created_on)
    VALUES (NEW.driver_id, NEW.currency, 0, NOW())
    ON CONFLICT (driver_id, currency) DO NOTHING;
    
    -- Update balance based on entry_type
    IF NEW.entry_type = 'CREDIT' THEN
        UPDATE driver_wallet
        SET balance = balance + NEW.amount,
            updated_on = NOW()
        WHERE driver_id = NEW.driver_id AND currency = NEW.currency;
    ELSIF NEW.entry_type = 'DEBIT' THEN
        UPDATE driver_wallet
        SET balance = balance - NEW.amount,
            updated_on = NOW()
        WHERE driver_id = NEW.driver_id AND currency = NEW.currency;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- ============================================================================
-- 3. CREATE TRIGGERS
-- ============================================================================

-- Drop existing triggers if they exist (for idempotency)
DROP TRIGGER IF EXISTS trg_platform_ledger_wallet ON platform_ledger;
DROP TRIGGER IF EXISTS trg_tenant_ledger_wallet ON tenant_ledger;
DROP TRIGGER IF EXISTS trg_fleet_ledger_wallet ON fleet_ledger;
DROP TRIGGER IF EXISTS trg_driver_ledger_wallet ON driver_ledger;

-- Platform Ledger → Platform Wallet
CREATE TRIGGER trg_platform_ledger_wallet
AFTER INSERT ON platform_ledger
FOR EACH ROW
EXECUTE FUNCTION update_platform_wallet_from_ledger();

-- Tenant Ledger → Tenant Wallet
CREATE TRIGGER trg_tenant_ledger_wallet
AFTER INSERT ON tenant_ledger
FOR EACH ROW
EXECUTE FUNCTION update_tenant_wallet_from_ledger();

-- Fleet Ledger → Fleet Wallet
CREATE TRIGGER trg_fleet_ledger_wallet
AFTER INSERT ON fleet_ledger
FOR EACH ROW
EXECUTE FUNCTION update_fleet_wallet_from_ledger();

-- Driver Ledger → Driver Wallet
CREATE TRIGGER trg_driver_ledger_wallet
AFTER INSERT ON driver_ledger
FOR EACH ROW
EXECUTE FUNCTION update_driver_wallet_from_ledger();


-- ============================================================================
-- 4. VERIFICATION QUERIES (run after setup to verify)
-- ============================================================================
/*
-- Check triggers are created:
SELECT trigger_name, event_object_table, action_timing 
FROM information_schema.triggers 
WHERE trigger_schema = 'public' 
AND trigger_name LIKE 'trg_%_wallet';

-- Test platform ledger trigger:
-- INSERT INTO platform_ledger (trip_id, currency, amount, entry_type, reason)
-- VALUES (1, 'INR', 100.00, 'CREDIT', 'Test');
-- SELECT * FROM platform_wallet WHERE currency = 'INR';
*/


-- ============================================================================
-- 5. ADD PAID STATUS TO LOOKUP TABLE (if not exists)
-- ============================================================================
INSERT INTO lu_trip_status (status_code, description)
VALUES ('PAID', 'Trip payment settled')
ON CONFLICT (status_code) DO NOTHING;


-- ============================================================================
-- SUMMARY
-- ============================================================================
-- After running this script:
-- 1. driver_ledger table exists
-- 2. fleet_wallet table exists
-- 3. Four triggers are active:
--    - platform_ledger → platform_wallet
--    - tenant_ledger → tenant_wallet
--    - fleet_ledger → fleet_wallet
--    - driver_ledger → driver_wallet
-- 4. PAID trip status is available
--
-- Wallet balances auto-update on ledger INSERT:
-- - CREDIT → adds to balance
-- - DEBIT → subtracts from balance
-- ============================================================================
