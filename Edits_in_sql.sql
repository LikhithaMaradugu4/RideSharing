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