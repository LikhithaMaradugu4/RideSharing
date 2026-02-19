-- Migration: Add rejection_reason column to fleet_document table
-- This enables per-document rejection with reasons (matching UserKYC pattern)

ALTER TABLE fleet_document ADD COLUMN IF NOT EXISTS rejection_reason TEXT;



CREATE TABLE trip_ratings (
    id SERIAL PRIMARY KEY,
    trip_id INTEGER NOT NULL REFERENCES trip(trip_id),
    rater_user_id INTEGER NOT NULL REFERENCES app_user(user_id),
    rated_user_id INTEGER NOT NULL REFERENCES app_user(user_id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    feedback TEXT,
    role_type VARCHAR(10) CHECK (role_type IN ('DRIVER', 'RIDER')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(trip_id, rater_user_id)
);


ALTER TABLE fleet_document ADD COLUMN IF NOT EXISTS rejection_reason TEXT;


ALTER TABLE user_kyc ADD COLUMN IF NOT EXISTS rejection_reason TEXT;

-- Add PARTIALLY_REJECTED status to lu_approval_status lookup table
INSERT INTO lu_approval_status (status_code) VALUES ('PARTIALLY_REJECTED')
ON CONFLICT (status_code) DO NOTHING;

-- Comment for documentation
COMMENT ON COLUMN user_kyc.rejection_reason IS 'Reason provided when document is rejected by tenant admin';

select * from driver_profile;

CREATE TABLE trip_ratings (
    id SERIAL PRIMARY KEY,
    trip_id INTEGER NOT NULL REFERENCES trip(trip_id),
    rater_user_id INTEGER NOT NULL REFERENCES app_user(user_id),
    rated_user_id INTEGER NOT NULL REFERENCES app_user(user_id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    feedback TEXT,
    role_type VARCHAR(10) CHECK (role_type IN ('DRIVER', 'RIDER')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(trip_id, rater_user_id)
);
select * from trip;
se

ALTER TABLE fleet_document ADD COLUMN IF NOT EXISTS rejection_reason TEXT;


-- Execute against your database:
ALTER TABLE trip ADD COLUMN IF NOT EXISTS surge_multiplier NUMERIC(5,2) NOT NULL DEFAULT 1.0;



ALTER TABLE trip
ADD COLUMN IF NOT EXISTS surge_multiplier NUMERIC(5,2) NOT NULL DEFAULT 1.0;

COMMENT ON COLUMN trip.surge_multiplier
IS 'Surge multiplier locked at trip creation. Never updated after trip is created.';


select * from surge_zone;
