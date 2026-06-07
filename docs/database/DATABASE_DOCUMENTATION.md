# TiranaFly: Database Schema & PostGIS Invariants

## 1. Entity Relationship Overview
The database is built on **PostgreSQL 15** with the **PostGIS 3.3** extension for high-performance spatial indexing.

## 2. Spatial Tables
### 2.1 `administrative_units`
Stores the polygonal boundaries of the 14 municipal units.
*   `geom`: `MULTIPOLYGON` (SRID 4326)
*   `spatial_index`: `GIST(geom)`

### 2.2 `hex_cells`
Primary demand abstraction layer.
*   `h3_index`: Unique H3 identifier.
*   `population`: Integrated inhabitant count.
*   `geom`: `POLYGON` (SRID 4326)

### 2.3 `depots`
Optimized facility locations.
*   `geom`: `POINT` (SRID 4326)
*   `capacity`: Max drone slots.

## 3. Operational Tables
### 3.1 `drones` & `batteries`
*   State-tracking for the active fleet.
*   `status`: Enum (AVAILABLE, EN_ROUTE, CHARGING, MAINTENANCE).

### 3.2 `missions`
*   Audit log of all delivery flights.
*   Linkage between drones, depots, and destination cells.

## 4. Performance Optimizations
*   **Spatial Indexing**: All geometry columns use `GIST` indexes for fast range queries and containment checks.
*   **Partitioning**: High-volume telemetry data (if implemented) should be partitioned by `timestamp`.
*   **Constraints**: `CHECK` constraints on battery `soc` (0.0 to 1.0) and population counts (non-negative).
