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
select * from vehicle
select * from app_user
select * from fleet_driver;
select * from driver_profile;
select * from user_session;
select * from fleet
select * from driver_vehicle_assignment;
select * from driver_shift;
select * from driver_shift;
ALTER TABLE vehicle
ADD CONSTRAINT vehicle_pkey PRIMARY KEY (vehicle_id);

-- Add vehicle_id column to driver_shift table
ALTER TABLE driver_shift 
ADD COLUMN vehicle_id BIGINT REFERENCES vehicle(vehicle_id);

-- Optional: Add an index for faster queries
CREATE INDEX idx_driver_shift_vehicle_id ON driver_shift(vehicle_id)




ALTER TABLE trip DROP COLUMN IF EXISTS zone_id;
ALTER TABLE dispatcher_assignment DROP COLUMN IF EXISTS zone_id;
DROP TABLE IF EXISTS surge_event;
DROP TABLE IF EXISTS surge_zone;
DROP TABLE IF EXISTS pricing_time_rule;

DROP TABLE IF EXISTS zone;


ALTER TABLE city
ADD COLUMN boundary_geojson TEXT NOT NULL DEFAULT '{}',
ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE;

ALTER TABLE city
ADD PRIMARY KEY (city_id);
ALTER TABLE lu_vehicle_category
ADD CONSTRAINT pk_lu_vehicle_category
PRIMARY KEY (category_code);


DROP TABLE IF EXISTS fare_config;

CREATE TABLE fare_config (
    fare_id BIGSERIAL PRIMARY KEY,

    city_id BIGINT NOT NULL REFERENCES city(city_id),
    vehicle_category TEXT NOT NULL REFERENCES lu_vehicle_category(category_code),

    base_fare NUMERIC(10,2) NOT NULL,
    per_km NUMERIC(10,2) NOT NULL,
    per_minute NUMERIC(10,2) NOT NULL,
    minimum_fare NUMERIC(10,2) NOT NULL,

    created_by BIGINT REFERENCES app_user(user_id),
    created_on TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_by BIGINT REFERENCES app_user(user_id),
    updated_on TIMESTAMPTZ,

    UNIQUE (city_id, vehicle_category)
);


CREATE TABLE surge_zone (
    surge_zone_id BIGSERIAL PRIMARY KEY,

    city_id BIGINT NOT NULL REFERENCES city(city_id),
    name VARCHAR(120),

    boundary_geojson TEXT NOT NULL,
    multiplier NUMERIC(5,2) NOT NULL,

    starts_at TIMESTAMPTZ NOT NULL,
    ends_at TIMESTAMPTZ NOT NULL,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_by BIGINT REFERENCES app_user(user_id),
    created_on TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_by BIGINT REFERENCES app_user(user_id),
    updated_on TIMESTAMPTZ
);



ALTER TABLE trip
ADD COLUMN surge_zone_id BIGINT REFERENCES surge_zone(surge_zone_id);




INSERT INTO city (
    country_code,
    name,
    timezone,
    currency,
    boundary_geojson,
    is_active
)
VALUES (
    'IN',
    'Hyderabad',
    'Asia/Kolkata',
    'INR',
    '{
      "type":"Polygon",
      "coordinates":[[
        [78.30,17.35],
        [78.60,17.35],
        [78.60,17.55],
        [78.30,17.55],
        [78.30,17.35]
      ]]
    }',
    TRUE
);


select * from lu_vehicle_category;

INSERT INTO fare_config (
    city_id,
    vehicle_category,
    base_fare,
    per_km,
    per_minute,
    minimum_fare
)
VALUES (
    1,
    'BIKE',
    30,
    10,
    1,
    40
);

INSERT INTO driver_location (
    driver_id,
    latitude,
    longitude,
    last_updated
)
VALUES (
    21,
    17.40,
    78.45,
    now()
);


INSERT INTO app_user (user_id, full_name,phone,country_code,role,status,created_on)
VALUES
(201, 'Ravi Kumar', +919705939721, 'IN', 'RIDER', 'ACTIVE',now()),
(202, 'Suresh Reddy', +919705939722, 'IN', 'DRIVER', 'ACTIVE',now()),
(203, 'Mahesh Rao',  +919705939723, 'IN', 'DRIVER','ACTIVE',now()),
(204, 'Arjun Verma', +919705939726, 'IN', 'DRIVER', 'ACTIVE',now()),
(205, 'Vikas Singh', +919705939725, 'IN', 'DRIVER','ACTIVE', now());
select * from driver_profile;

INSERT INTO driver_profile (
    driver_id,
	tenant_id,
	driver_type,
    approval_status,
    allowed_vehicle_categories,
    created_on
)
VALUES
(201,1, 'INDEPENDENT','APPROVED',  ARRAY['BIKE'], now()),
(202, 1,'INDEPENDENT','APPROVED', ARRAY['BIKE'],  now()),
(203,1,'INDEPENDENT', 'APPROVED', ARRAY['BIKE'],  now()),
(204, 1,'INDEPENDENT','APPROVED', ARRAY['BIKE'],  now()),
(205, 1,'INDEPENDENT','APPROVED', ARRAY['BIKE'], now());

INSERT INTO fleet (
    tenant_id,
    owner_user_id,
    fleet_name,
    fleet_type,
    status,
    approval_status,
    created_by
)
VALUES
(1, 201, 'Ravi Fleet',   'INDIVIDUAL', 'ACTIVE', 'APPROVED', 1),
(1, 202, 'Suresh Fleet', 'INDIVIDUAL', 'ACTIVE', 'APPROVED', 1),
(1, 203, 'Mahesh Fleet', 'INDIVIDUAL', 'ACTIVE', 'APPROVED', 1),
(1, 204, 'Arjun Fleet',  'INDIVIDUAL', 'ACTIVE', 'APPROVED', 1),
(1, 205, 'Vikas Fleet',  'INDIVIDUAL', 'ACTIVE', 'APPROVED', 1);
select * from fleet;
select * from vehicle;
INSERT INTO vehicle (
    vehicle_id,
	tenant_id,
    fleet_id,
    category,
   registration_no,
    status,
    created_on
)
VALUES
(301,1, 11, 'BIKE','TS09AB1201', 'ACTIVE', now()),
(302,1, 12, 'BIKE','TS09AB1202', 'ACTIVE', now()),
(303,1,13, 'BIKE', 'TS09AB1203', 'ACTIVE', now()),
(304,1,14, 'BIKE','TS09AB1204', 'ACTIVE', now()),
(305,1,15, 'BIKE', 'TS09AB1205', 'ACTIVE', now());

select * from driver_shift;
INSERT INTO driver_location (driver_id, latitude, longitude, last_updated)
VALUES
(201, 17.3860, 78.4870, now()),  -- wave 1
(202, 17.3920, 78.4920, now()),  -- wave 1
(203, 17.4100, 78.5100, now()),  -- wave 2
(204, 17.4300, 78.5300, now()),  -- wave 3
(205, 17.4600, 78.5600, now());  -- excluded (beyond MAX_RADIUS)
select * from city;
select * from fare_config;
INSERT INTO fare_config (
    city_id,
    vehicle_category,
    base_fare,
    per_km,
    per_minute,
    minimum_fare,
    created_by,
    created_on
)
VALUES (         -- tenant_id
    2,          -- city_id
    'BIKE',     -- vehicle_category
    30.00,      -- base_fare (₹30)
    10.00,      -- per_km (₹10 per km)
    1.00,       -- per_minute (₹1 per minute)
    40.00,      -- minimum_fare (₹40)
    1,          -- created_by (platform admin)
    now()
);

ALTER TABLE trip
ALTER COLUMN tenant_id DROP NOT NULL;




INSERT INTO driver_location (
    driver_id,
    latitude,
    longitude,
    last_updated
)
VALUES (
    21,
    17.40,
    78.45,
    now()
);
INSERT INTO app_user (user_id, full_name,phon,,role, created_on)
VALUES
(201, 'Ravi Kumar',+919705939721,,'DRIVER', now()),
(202, 'Suresh Reddy', 'DRIVER', now()),
(203, 'Mahesh Rao',   'DRIVER', now()),
(204, 'Arjun Verma',  'DRIVER', now()),
(205, 'Vikas Singh',  'DRIVER', now());


INSERT INTO driver_location (driver_id, latitude, longitude, last_updated)
VALUES
(201, 17.3860, 78.4870, now()),  -- wave 1
(202, 17.3920, 78.4920, now()),  -- wave 1
(203, 17.4100, 78.5100, now()),  -- wave 2
(204, 17.4300, 78.5300, now()),  -- wave 3
(205, 17.4600, 78.5600, now());  -- excluded (beyond MAX_RADIUS)
INSERT INTO driver_shift (
    driver_id,
    tenant_id,
    status,
    started_at,
    created_on
)
VALUES
(201, 1, 'ONLINE', now(), now()),
(202, 1, 'ONLINE', now(), now()),
(203, 1, 'ONLINE', now(), now()),
(204, 1, 'ONLINE', now(), now()),
(205, 1, 'ONLINE', now(), now());


INSERT INTO driver_location (
    driver_id,
    latitude,
    longitude,
    last_updated
)
VALUES
-- Wave 1 (very close: < 3 km)
(201, 17.3860, 78.4870, now()),
(202, 17.3920, 78.4920, now()),

-- Wave 2 (~4–5 km)
(203, 17.4100, 78.5100, now()),
-- Wave 3 (~6–8 km)
(204, 17.4300, 78.5300, now()),

-- Beyond MAX_RADIUS (should be excluded)
(205, 17.4600, 78.5600, now());


select * from driver_location;


UPDATE app_user
SET phone = CASE user_id
    WHEN 201 THEN '+919876453211'
    WHEN 202 THEN '+919876453212'
    WHEN 203 THEN '+919876453213'
    WHEN 204 THEN '+919876453214'
END
WHERE user_id BETWEEN 201 AND 205;

select * from app_user;
update app_user set phone= +918498858063 where user_id = 9;

select * from fleet;
UPDATE dispatch_attempt
SET response = 'REJECTED', responded_at = now()
WHERE trip_id = 8;
select * from dispatch_attempt;
select * from driver_profile;
SELECT driver_id, city_id
FROM driver_profile
WHERE driver_id IN (201,202,203,204);
SELECT
  dp.driver_id,
  dp.allowed_vehicle_categories,
  ds.status,
  ds.ended_at
FROM driver_profile dp
JOIN driver_shift ds ON ds.driver_id = dp.driver_id
WHERE dp.driver_id = 204;
SELECT *
FROM driver_location
WHERE driver_id = 204;
-- Compare 203 vs 204 directly
SELECT
  dp.driver_id,
  dp.allowed_vehicle_categories,
}

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







---------------------------------------------------

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
select * from driver_shift;
TRUNCATE TABLE trip RESTART IDENTITY CASCADE;


INSERT INTO fare_config (
    city_id,
    vehicle_category,
    currency,
    base_fare,
    per_km_rate,
    per_min_rate,
    minimum_fare,
    booking_fee,
    surge_allowed,
    night_charge_pct,
    effective_from,
    effective_to,
    created_by
)
VALUES

-- 🏍 BIKE (cheapest option)
(
    2,
    'BIKE',
    'INR',
    20.00,      -- base_fare
    6.00,       -- per_km_rate
    0.80,       -- per_min_rate
    40.00,      -- minimum_fare
    5.00,       -- booking_fee
    true,
    15.00,      -- 15% night charge
    now(),
    NULL,
    1
),

-- 🛺 AUTO (mid tier)
(
    2,
    'AUTO',
    'INR',
    30.00,
    10.00,
    1.50,
    60.00,
    8.00,
    true,
    18.00,
    now(),
    NULL,
    1
),

-- 🚗 SEDAN (premium)
(
    2,
    'SEDAN',
    'INR',
    50.00,
    14.00,
    2.50,
    100.00,
    10.00,
    true,
    20.00,
    now(),
    NULL,
    1
);


select * from tenant_ledger;
ALTER TABLE driver_ledger
add COLUMN settlement_status text DEFAULT 'unsettled';

ALTER TABLE driver_profile
ADD COLUMN is_blocked boolean DEFAULT false NOT NULL;

ALTER TABLE driver_profile
ADD COLUMN blocked_reason text;

SELECT
    status,
    payment_mode,
    payment_status,
    settlement_status
FROM trip
WHERE trip_id = 11;

select * from driver_ledger;
truncate 
 driver_ledger,
 tenant_ledger,
 platform_ledger
 fleet_ledger
restart identity cascade;

CREATE TABLE payout_request (
    id BIGSERIAL PRIMARY KEY,
    
    driver_id BIGINT NOT NULL REFERENCES app_user(user_id),
    
    total_amount NUMERIC(12,2) NOT NULL,
    currency CHAR(3) NOT NULL DEFAULT 'INR',
    
    payout_type TEXT NOT NULL,  -- 'trip_batch' | 'full' | 'single'
    
    status TEXT DEFAULT 'requested',
    -- requested | approved | rejected | processing | completed
    
    payment_reference TEXT NULL,  -- bank/UPI transaction ID
    
    processed_by BIGINT NULL REFERENCES app_user(user_id),
    processed_on TIMESTAMPTZ NULL,
    
    created_on TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    FOREIGN KEY (driver_id) REFERENCES app_user(user_id)
);
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


