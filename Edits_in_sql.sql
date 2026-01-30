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

