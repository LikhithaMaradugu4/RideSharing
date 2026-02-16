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
INSERT INTO country (
    country_code,
    name,
    phone_code,
    default_timezone,
    default_currency,
    created_by,
    updated_by
)
VALUES
('US', 'United States', '+1', 'America/New_York', 'USD', 1, 1),
('GB', 'United Kingdom', '+44', 'Europe/London', 'GBP', 1, 1),
('AE', 'United Arab Emirates', '+971', 'Asia/Dubai', 'AED', 1, 1),
('SG', 'Singapore', '+65', 'Asia/Singapore', 'SGD', 1, 1);

select * from city;
SELECT setval(
    pg_get_serial_sequence('city', 'city_id'),
    COALESCE((SELECT MAX(city_id) FROM city), 1)
);

INSERT INTO city (
    country_code,
    name,
    timezone,
    currency,
    boundary_geojson,
    created_by,
    updated_by,
    is_active
)
VALUES
('US', 'New York', 'America/New_York', 'USD',
'{"type":"Polygon","coordinates":[[[-74.10,40.70],[-73.90,40.70],[-73.90,40.85],[-74.10,40.85],[-74.10,40.70]]]}',
1,1,true),

('US', 'Los Angeles', 'America/Los_Angeles', 'USD',
'{"type":"Polygon","coordinates":[[[-118.45,33.90],[-118.15,33.90],[-118.15,34.10],[-118.45,34.10],[-118.45,33.90]]]}',
1,1,true),

('US', 'Chicago', 'America/Chicago', 'USD',
'{"type":"Polygon","coordinates":[[[-87.75,41.80],[-87.60,41.80],[-87.60,41.95],[-87.75,41.95],[-87.75,41.80]]]}',
1,1,true),

('US', 'Houston', 'America/Chicago', 'USD',
'{"type":"Polygon","coordinates":[[[-95.45,29.65],[-95.25,29.65],[-95.25,29.85],[-95.45,29.85],[-95.45,29.65]]]}',
1,1,true),

('US', 'San Francisco', 'America/Los_Angeles', 'USD',
'{"type":"Polygon","coordinates":[[[-122.52,37.70],[-122.35,37.70],[-122.35,37.83],[-122.52,37.83],[-122.52,37.70]]]}',
1,1,true);

INSERT INTO city (
    country_code,
    name,
    timezone,
    currency,
    boundary_geojson,
    created_by,
    updated_by,
    is_active
)
VALUES
('GB', 'London', 'Europe/London', 'GBP',
'{"type":"Polygon","coordinates":[[[-0.30,51.45],[0.10,51.45],[0.10,51.60],[-0.30,51.60],[-0.30,51.45]]]}',
1,1,true),

('GB', 'Manchester', 'Europe/London', 'GBP',
'{"type":"Polygon","coordinates":[[[-2.30,53.40],[-2.15,53.40],[-2.15,53.50],[-2.30,53.50],[-2.30,53.40]]]}',
1,1,true),

('GB', 'Birmingham', 'Europe/London', 'GBP',
'{"type":"Polygon","coordinates":[[[-1.95,52.45],[-1.80,52.45],[-1.80,52.55],[-1.95,52.55],[-1.95,52.45]]]}',
1,1,true),

('GB', 'Liverpool', 'Europe/London', 'GBP',
'{"type":"Polygon","coordinates":[[[-3.05,53.35],[-2.85,53.35],[-2.85,53.45],[-3.05,53.45],[-3.05,53.35]]]}',
1,1,true),

('GB', 'Leeds', 'Europe/London', 'GBP',
'{"type":"Polygon","coordinates":[[[-1.60,53.75],[-1.45,53.75],[-1.45,53.85],[-1.60,53.85],[-1.60,53.75]]]}',
1,1,true);


INSERT INTO city (
    country_code,
    name,
    timezone,
    currency,
    boundary_geojson,
    created_by,
    updated_by,
    is_active
)
VALUES
('AE', 'Dubai', 'Asia/Dubai', 'AED',
'{"type":"Polygon","coordinates":[[[55.20,25.15],[55.40,25.15],[55.40,25.30],[55.20,25.30],[55.20,25.15]]]}',
1,1,true),

('AE', 'Abu Dhabi', 'Asia/Dubai', 'AED',
'{"type":"Polygon","coordinates":[[[54.30,24.40],[54.50,24.40],[54.50,24.55],[54.30,24.55],[54.30,24.40]]]}',
1,1,true),

('AE', 'Sharjah', 'Asia/Dubai', 'AED',
'{"type":"Polygon","coordinates":[[[55.35,25.30],[55.45,25.30],[55.45,25.40],[55.35,25.40],[55.35,25.30]]]}',
1,1,true),

('AE', 'Ajman', 'Asia/Dubai', 'AED',
'{"type":"Polygon","coordinates":[[[55.40,25.35],[55.50,25.35],[55.50,25.45],[55.40,25.45],[55.40,25.35]]]}',
1,1,true),

('AE', 'Al Ain', 'Asia/Dubai', 'AED',
'{"type":"Polygon","coordinates":[[[55.70,24.15],[55.85,24.15],[55.85,24.30],[55.70,24.30],[55.70,24.15]]]}',
1,1,true);



INSERT INTO city (
    country_code,
    name,
    timezone,
    currency,
    boundary_geojson,
    created_by,
    updated_by,
    is_active
)
VALUES
('SG', 'Singapore', 'Asia/Singapore', 'SGD',
'{"type":"Polygon","coordinates":[[[103.70,1.25],[103.90,1.25],[103.90,1.45],[103.70,1.45],[103.70,1.25]]]}',
1,1,true),

('SG', 'Jurong', 'Asia/Singapore', 'SGD',
'{"type":"Polygon","coordinates":[[[103.68,1.30],[103.75,1.30],[103.75,1.35],[103.68,1.35],[103.68,1.30]]]}',
1,1,true),

('SG', 'Woodlands', 'Asia/Singapore', 'SGD',
'{"type":"Polygon","coordinates":[[[103.75,1.42],[103.85,1.42],[103.85,1.48],[103.75,1.48],[103.75,1.42]]]}',
1,1,true),

('SG', 'Tampines', 'Asia/Singapore', 'SGD',
'{"type":"Polygon","coordinates":[[[103.90,1.33],[104.00,1.33],[104.00,1.38],[103.90,1.38],[103.90,1.33]]]}',
1,1,true),

('SG', 'Punggol', 'Asia/Singapore', 'SGD',
'{"type":"Polygon","coordinates":[[[103.90,1.38],[104.00,1.38],[104.00,1.45],[103.90,1.45],[103.90,1.38]]]}',
1,1,true);
select * from city;


CREATE TABLE commission_config (
    id bigserial PRIMARY KEY,

    commission_type text NOT NULL, -- platform | tenant | fleet

    tenant_id bigint NULL,
    city_id bigint NULL,
    vehicle_category text NULL,

    fixed_amount numeric(10,2) DEFAULT 0,
    percentage numeric(5,4) DEFAULT 0,

    currency char(3) DEFAULT 'INR',

    is_active boolean DEFAULT true,

    effective_from timestamptz NOT NULL,
    effective_to timestamptz NULL,

    created_on timestamptz DEFAULT now(),
    created_by bigint,
    updated_on timestamptz,
    updated_by bigint
);

ALTER TABLE commission_config
ADD CONSTRAINT check_percentage_range
CHECK (percentage >= 0 AND percentage <= 1);

ALTER TABLE commission_config
ADD CONSTRAINT check_fixed_positive
CHECK (fixed_amount >= 0);


CREATE TABLE payout_request (
    id bigserial PRIMARY KEY,

    driver_id bigint NOT NULL,

    requested_amount numeric(12,2) NOT NULL,

    payout_type text NOT NULL, -- full | specific_rides

    status text DEFAULT 'requested',
    -- requested
    -- approved
    -- rejected
    -- completed

    processed_by bigint NULL,

    processed_on timestamptz NULL,

    created_on timestamptz DEFAULT now()
);

CREATE TABLE ride_payment_dispute (
    id bigserial PRIMARY KEY,

    ride_id bigint NOT NULL,
    driver_id bigint NOT NULL,

    raised_by text NOT NULL, -- rider | driver

    reason text,

    status text DEFAULT 'open',
    -- open
    -- under_review
    -- resolved
    -- rejected

    resolved_by bigint NULL,
    resolved_on timestamptz NULL,

    created_on timestamptz DEFAULT now()
);


ALTER TABLE trip
ADD COLUMN tenant_commission numeric(10,2) DEFAULT 0,
ADD COLUMN fleet_commission numeric(10,2) DEFAULT 0,
ADD COLUMN payment_mode text, -- cash | online
ADD COLUMN settlement_status text DEFAULT 'unsettled';


INSERT INTO commission_config
(commission_type, percentage, currency, effective_from)
VALUES
('platform', 0.20, 'INR', now()),
('tenant',   0.05, 'INR', now()),
('fleet',    0.05, 'INR', now());
drop table payout_request;

CREATE TABLE payout_request (
    id bigserial PRIMARY KEY,

    driver_id bigint NOT NULL,

    total_amount numeric(12,2) NOT NULL,

    payout_type text NOT NULL, -- full | specific_trips

    status text DEFAULT 'requested',
    -- requested
    -- approved
    -- rejected
    -- processing
    -- completed

    payment_reference text NULL,  -- bank/UPI txn id

    processed_by bigint NULL,
    processed_on timestamptz NULL,

    created_on timestamptz DEFAULT now()
);
CREATE TABLE payout_request_item (
    id bigserial PRIMARY KEY,

    payout_request_id bigint NOT NULL,
    ledger_id bigint NOT NULL,

    created_on timestamptz DEFAULT now()
);

ALTER TABLE tenant_wallet
ADD CONSTRAINT tenant_wallet_tenant_currency_unique
UNIQUE (tenant_id, currency);

ALTER TABLE fleet_wallet
ADD CONSTRAINT fleet_wallet_fleet_currency_unique
UNIQUE (fleet_id, currency);