select * from app_user;
select * from user_auth;
select * from user_session;
select * from driver_profile;
select * from tenant;
select * from user_kyc;
select * from driver_shift;
select * from fleet;
select * from fleet_driver;
select * from city;
select * from vehicle;
select * from vehicle_document;
select * from vehicle_spec;
select * from tenant_admin;

insert into tenant_admin values (3,5,19,true);

update app_user set role='TENANT_ADMIN' where user_id=19;

insert into user_auth values(19,'$2b$12$8ffBaRjjS2TDy2fI.Ai57.5MTYe.baeXRw8qF1PjRM2Ju4e8ykF5a',false);

DELETE FROM fleet WHERE fleet_id = 3;
CREATE TABLE fleet_driver_invite (
    invite_id BIGSERIAL PRIMARY KEY,
    fleet_id BIGINT NOT NULL REFERENCES fleet(fleet_id) ON DELETE CASCADE,
    driver_id BIGINT NOT NULL REFERENCES app_user(user_id) ON DELETE CASCADE,

    status TEXT NOT NULL DEFAULT 'PENDING',
    invited_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    responded_at TIMESTAMPTZ,

    created_by BIGINT REFERENCES app_user(user_id),
    created_on TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_by BIGINT REFERENCES app_user(user_id),
    updated_on TIMESTAMPTZ,

    UNIQUE (fleet_id, driver_id, status)  -- prevents duplicate active invites
);

ALTER TABLE fleet
ADD PRIMARY KEY (fleet_id);

 CREATE TABLE fleet_driver_invite (
    invite_id  BIGSERIAL PRIMARY KEY,
    fleet_id   BIGINT NOT NULL REFERENCES fleet(fleet_id) ON DELETE CASCADE,
    driver_id  BIGINT NOT NULL REFERENCES app_user(user_id) ON DELETE CASCADE,
    status     TEXT NOT NULL DEFAULT 'PENDING', -- PENDING, ACCEPTED, REJECTED, EXPIRED
    invited_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    responded_at TIMESTAMPTZ,
    UNIQUE (fleet_id, driver_id, status)
);

ALTER TABLE fleet_driver_invite DROP CONSTRAINT fleet_driver_invite_fleet_id_fkey;
-- then add the correct one
ALTER TABLE fleet_driver_invite
ADD CONSTRAINT fleet_driver_invite_fleet_id_fkey
FOREIGN KEY (fleet_id) REFERENCES fleet(fleet_id) ON DELETE CASCADE;

ALTER TABLE app_user
ADD PRIMARY KEY (user_id);
insert into fleet_city values(2,1);


-- Add approval_status column to vehicle table
ALTER TABLE vehicle 
ADD COLUMN approval_status VARCHAR(20) DEFAULT 'PENDING' NOT NULL;

-- Add check constraint for valid values
ALTER TABLE vehicle
ADD CONSTRAINT vehicle_approval_status_check 
CHECK (approval_status IN ('PENDING', 'APPROVED', 'REJECTED'));

-- Update existing vehicles to APPROVED (optional - for existing data)
-- UPDATE vehicle SET approval_status = 'APPROVED' WHERE approval_status IS NULL;

-- Add index for filtering by approval_status
CREATE INDEX idx_vehicle_approval_status ON vehicle(approval_status);

-- Add index for tenant + approval status queries
CREATE INDEX idx_vehicle_tenant_approval ON vehicle(tenant_id, approval_status);

select * from app_user;
select * from fleet;
select * from fleet_driver;
select * from city;
select * from vehicle;
select * from driver_vehicle_assignment;

select * from vehicle_document;

select 

INSERT INTO driver_vehicle_assignment (
    driver_id,
    vehicle_id,
    start_time,
    end_time,
    created_by,
    created_on
)
VALUES
(201, 301, now(), NULL, 1, now()),
(202, 302, now(), NULL, 1, now()),
(203, 303, now(), NULL, 1, now()),
(204, 304, now(), NULL, 1, now()),
(205, 305, now(), NULL, 1, now());

UPDATE vehicle
SET approval_status = 'APPROVED'
WHERE vehicle_id BETWEEN 301 AND 305;
INSERT INTO vehicle_document (
    vehicle_id,
    document_type,
    file_url,
    verification_status,
    verified_by,
    verified_on,
    created_by,
    created_on
)
VALUES
-- Vehicle 301
(301, 'RC',            'https://files.test/vehicle/301/rc.pdf',            'VERIFIED', 1, now(), 1, now()),
(301, 'INSURANCE',     'https://files.test/vehicle/301/insurance.pdf',     'VERIFIED', 1, now(), 1, now()),
(301, 'PERMIT',        'https://files.test/vehicle/301/permit.pdf',        'VERIFIED', 1, now(), 1, now()),
(301, 'FITNESS',       'https://files.test/vehicle/301/fitness.pdf',       'VERIFIED', 1, now(), 1, now()),
(301, 'VEHICLE_PHOTO', 'https://files.test/vehicle/301/photo.jpg',         'VERIFIED', 1, now(), 1, now()),

-- Vehicle 302
(302, 'RC',            'https://files.test/vehicle/302/rc.pdf',            'VERIFIED', 1, now(), 1, now()),
(302, 'INSURANCE',     'https://files.test/vehicle/302/insurance.pdf',     'VERIFIED', 1, now(), 1, now()),
(302, 'PERMIT',        'https://files.test/vehicle/302/permit.pdf',        'VERIFIED', 1, now(), 1, now()),
(302, 'FITNESS',       'https://files.test/vehicle/302/fitness.pdf',       'VERIFIED', 1, now(), 1, now()),
(302, 'VEHICLE_PHOTO', 'https://files.test/vehicle/302/photo.jpg',         'VERIFIED', 1, now(), 1, now()),

-- Vehicle 303
(303, 'RC',            'https://files.test/vehicle/303/rc.pdf',            'VERIFIED', 1, now(), 1, now()),
(303, 'INSURANCE',     'https://files.test/vehicle/303/insurance.pdf',     'VERIFIED', 1, now(), 1, now()),
(303, 'PERMIT',        'https://files.test/vehicle/303/permit.pdf',        'VERIFIED', 1, now(), 1, now()),
(303, 'FITNESS',       'https://files.test/vehicle/303/fitness.pdf',       'VERIFIED', 1, now(), 1, now()),
(303, 'VEHICLE_PHOTO', 'https://files.test/vehicle/303/photo.jpg',         'VERIFIED', 1, now(), 1, now()),

-- Vehicle 304
(304, 'RC',            'https://files.test/vehicle/304/rc.pdf',            'VERIFIED', 1, now(), 1, now()),
(304, 'INSURANCE',     'https://files.test/vehicle/304/insurance.pdf',     'VERIFIED', 1, now(), 1, now()),
(304, 'PERMIT',        'https://files.test/vehicle/304/permit.pdf',        'VERIFIED', 1, now(), 1, now()),
(304, 'FITNESS',       'https://files.test/vehicle/304/fitness.pdf',       'VERIFIED', 1, now(), 1, now()),
(304, 'VEHICLE_PHOTO', 'https://files.test/vehicle/304/photo.jpg',         'VERIFIED', 1, now(), 1, now()),

-- Vehicle 305
(305, 'RC',            'https://files.test/vehicle/305/rc.pdf',            'VERIFIED', 1, now(), 1, now()),
(305, 'INSURANCE',     'https://files.test/vehicle/305/insurance.pdf',     'VERIFIED', 1, now(), 1, now()),
(305, 'PERMIT',        'https://files.test/vehicle/305/permit.pdf',        'VERIFIED', 1, now(), 1, now()),
(305, 'FITNESS',       'https://files.test/vehicle/305/fitness.pdf',       'VERIFIED', 1, now(), 1, now()),
(305, 'VEHICLE_PHOTO', 'https://files.test/vehicle/305/photo.jpg',         'VERIFIED', 1, now(), 1, now());

select * from dispatch_attempt;
select * from trip;
update trip set status = 'COMPLETED' where trip_id = 11;
select * from driver_shi
TRUNCATE TABLE trip RESTART IDENTITY CASCADE;
alter table country add primary key(country_code);
ALTER TABLE trip
ADD COLUMN country_code CHAR(2) NOT NULL REFERENCES country(country_code),
ADD COLUMN currency CHAR(3) NOT NULL,
ADD COLUMN fare_config_id BIGINT,
ADD COLUMN fare_snapshot JSONB;


drop  table fare_config;
CREATE TABLE fare_config (
    fare_config_id BIGSERIAL PRIMARY KEY,

    city_id BIGINT NOT NULL REFERENCES city(city_id),
    vehicle_category TEXT NOT NULL,     -- BIKE / AUTO / CAB / XL
    currency CHAR(3) NOT NULL,           -- frozen from city

    base_fare NUMERIC(10,2) NOT NULL,
    per_km_rate NUMERIC(10,2) NOT NULL,
    per_min_rate NUMERIC(10,2) NOT NULL,

    minimum_fare NUMERIC(10,2),
    booking_fee NUMERIC(10,2),

    surge_allowed BOOLEAN NOT NULL DEFAULT TRUE,
    night_charge_pct NUMERIC(5,2),

    effective_from TIMESTAMPTZ NOT NULL,
    effective_to TIMESTAMPTZ,

    created_by BIGINT REFERENCES app_user(user_id),
    created_on TIMESTAMPTZ NOT NULL DEFAULT now(),

    UNIQUE (city_id, vehicle_category, effective_from)
);

DROP TABLE IF EXISTS driver_wallet;

CREATE TABLE driver_wallet (
    driver_id BIGINT NOT NULL REFERENCES app_user(user_id),
    currency CHAR(3) NOT NULL,
    balance NUMERIC(12,2) NOT NULL DEFAULT 0,

    created_on TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_on TIMESTAMPTZ,

    PRIMARY KEY (driver_id, currency)
);
alter table tenant add primary key (tenant_id);
DROP TABLE IF EXISTS tenant_wallet;

CREATE TABLE tenant_wallet (
    tenant_id BIGINT NOT NULL REFERENCES tenant(tenant_id),
    currency CHAR(3) NOT NULL,
    balance NUMERIC(12,2) NOT NULL DEFAULT 0,

    created_on TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_on TIMESTAMPTZ,

    PRIMARY KEY (tenant_id, currency)
);

DROP TABLE IF EXISTS platform_wallet;

CREATE TABLE platform_wallet (
    currency CHAR(3) PRIMARY KEY,
    balance NUMERIC(14,2) NOT NULL DEFAULT 0,

    created_on TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_on TIMESTAMPTZ
);

DROP TABLE IF EXISTS platform_ledger;

CREATE TABLE platform_ledger (
    entry_id BIGSERIAL PRIMARY KEY,
    trip_id BIGINT REFERENCES trip(trip_id),

    currency CHAR(3) NOT NULL,
    amount NUMERIC(12,2) NOT NULL,
    entry_type TEXT NOT NULL,   -- CREDIT / DEBIT
    reason TEXT,

    created_on TIMESTAMPTZ NOT NULL DEFAULT now()
);

alter table trip add primary key(trip_id);

DROP TABLE IF EXISTS tenant_ledger;

CREATE TABLE tenant_ledger (
    entry_id BIGSERIAL PRIMARY KEY,
    tenant_id BIGINT NOT NULL REFERENCES tenant(tenant_id),
    trip_id BIGINT REFERENCES trip(trip_id),

    currency CHAR(3) NOT NULL,
    amount NUMERIC(12,2) NOT NULL,
    entry_type TEXT NOT NULL,
    reason TEXT,

    created_on TIMESTAMPTZ NOT NULL DEFAULT now()
);

DROP TABLE IF EXISTS fleet_ledger;

CREATE TABLE fleet_ledger (
    entry_id BIGSERIAL PRIMARY KEY,
    fleet_id BIGINT NOT NULL REFERENCES fleet(fleet_id),
    trip_id BIGINT REFERENCES trip(trip_id),

    currency CHAR(3) NOT NULL,
    amount NUMERIC(12,2) NOT NULL,
    entry_type TEXT NOT NULL,
    reason TEXT,

    created_on TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE payment
ADD COLUMN gateway_name TEXT,
ADD COLUMN gateway_order_id TEXT,
ADD COLUMN gateway_payment_id TEXT UNIQUE,
ADD COLUMN gateway_signature TEXT,
ADD COLUMN gateway_payload JSONB;

CREATE INDEX idx_trip_city ON trip(city_id);
CREATE INDEX idx_trip_currency ON trip(currency);

CREATE INDEX idx_fare_config_lookup
ON fare_config(city_id, vehicle_category, effective_from, effective_to);

CREATE INDEX idx_platform_ledger_currency
ON platform_ledger(currency);

CREATE TABLE platform_commission_config (
    id BIGSERIAL PRIMARY KEY,

    city_id BIGINT REFERENCES city(city_id),
    vehicle_category TEXT NOT NULL,

    commission_type TEXT NOT NULL, 
    -- HYBRID / FIXED / PERCENTAGE

    fixed_amount NUMERIC(10,2),
    percentage NUMERIC(5,2),

    currency CHAR(3) NOT NULL,

    effective_from TIMESTAMPTZ NOT NULL,
    effective_to TIMESTAMPTZ,

    created_on TIMESTAMPTZ DEFAULT now(),

    UNIQUE (city_id, vehicle_category, effective_from)
);


CREATE INDEX idx_driver_wallet_negative
ON driver_wallet(balance)
WHERE balance < 0;


