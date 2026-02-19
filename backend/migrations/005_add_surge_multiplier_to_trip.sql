-- Migration: Add surge_multiplier column to trip table
-- This column permanently stores the surge multiplier applied at trip creation time.
-- It must never be modified after the trip is created.

ALTER TABLE trip
ADD COLUMN IF NOT EXISTS surge_multiplier NUMERIC(5,2) NOT NULL DEFAULT 1.0;

COMMENT ON COLUMN trip.surge_multiplier
IS 'Surge multiplier locked at trip creation. Never updated after trip is created.';


npm  install leaflet-draw
npx vite build 2>&1 | Select-Object -Last 30