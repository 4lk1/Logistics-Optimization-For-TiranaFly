-- filename: db/migrations/V1__initial_postgis_schema.sql

-- Enable spatial extensions
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE administrative_units (
    id SERIAL PRIMARY KEY,
    name VARCHAR(64) UNIQUE NOT NULL,
    population INT NOT NULL CHECK (population >= 0),
    demand_weight NUMERIC(10, 8) NOT NULL,
    geom GEOMETRY(Polygon, 4326) NOT NULL
);

CREATE TABLE hex_cells (
    h3_index VARCHAR(16) PRIMARY KEY,
    admin_unit_name VARCHAR(64) REFERENCES administrative_units(name),
    centroid_lat NUMERIC(10, 7) NOT NULL,
    centroid_lon NUMERIC(10, 7) NOT NULL,
    local_demand_coefficient NUMERIC(10, 8) NOT NULL,
    geom GEOMETRY(Polygon, 4326) NOT NULL
);

CREATE TABLE depots (
    depot_id VARCHAR(16) PRIMARY KEY,
    lat NUMERIC(10, 7) NOT NULL,
    lon NUMERIC(10, 7) NOT NULL,
    h3_index VARCHAR(16) REFERENCES hex_cells(h3_index),
    max_drone_capacity INT NOT NULL DEFAULT 30,
    allocated_fleet_count INT NOT NULL DEFAULT 0,
    geom GEOMETRY(Point, 4326) NOT NULL
);

CREATE TABLE drones (
    drone_id VARCHAR(32) PRIMARY KEY,
    depot_id VARCHAR(16) REFERENCES depots(depot_id),
    model_type VARCHAR(32) NOT NULL DEFAULT 'TF-2026-FleetMaster',
    status_state VARCHAR(16) NOT NULL DEFAULT 'IDLE',
    battery_health_pct NUMERIC(5, 2) NOT NULL DEFAULT 100.0
);

CREATE TABLE routes (
    route_id VARCHAR(64) PRIMARY KEY,
    origin_id VARCHAR(32) NOT NULL,
    destination_id VARCHAR(32) NOT NULL,
    distance_km NUMERIC(8, 3) NOT NULL,
    energy_cost_wh NUMERIC(8, 2) NOT NULL,
    geom GEOMETRY(LineString, 4326) NOT NULL
);

CREATE TABLE deliveries (
    delivery_id BIGSERIAL PRIMARY KEY,
    route_id VARCHAR(64) REFERENCES routes(route_id),
    drone_id VARCHAR(32) REFERENCES drones(drone_id),
    timestamp_ingested TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(16) NOT NULL DEFAULT 'PENDING'
);

-- Optimize queries with standard spatial indices
CREATE INDEX idx_admin_units_spatial ON administrative_units USING GIST(geom);
CREATE INDEX idx_hex_cells_spatial ON hex_cells USING GIST(geom);
CREATE INDEX idx_depots_spatial ON depots USING GIST(geom);
CREATE INDEX idx_routes_spatial ON routes USING GIST(geom);