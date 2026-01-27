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
