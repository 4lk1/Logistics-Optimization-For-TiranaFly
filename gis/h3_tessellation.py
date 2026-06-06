# filename: gis/h3_tessellation.py
"""
H3TessellationEngine — fills administrative unit polygons with H3 hexagonal cells.

H3 library version : 4.x  (installed: h3 4.5.0)
Default resolution : 8  →  mean cell area ≈ 0.74 km²,  edge length ≈ 0.46 km

H3 v4 API reference used here
──────────────────────────────
  h3.polygon_to_cells(h3_poly, resolution)  →  set[str]
      h3_poly is h3.LatLngPoly([(lat, lon), ...])

  h3.cell_to_latlng(cell)                   →  (lat, lon)
  h3.cell_to_boundary(cell)                 →  tuple of (lat, lon)
  h3.latlng_to_cell(lat, lon, resolution)   →  str
  h3.grid_disk(cell, k)                     →  set[str]   (k-ring incl. center)
  h3.grid_distance(cell_a, cell_b)          →  int
  h3.get_resolution(cell)                   →  int

Output
──────
Returns list[TessellatedCell] ordered by (unit_name, h3_index) for
reproducibility, and a summary dict.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

import geopandas as gpd
import h3
from shapely.geometry import Polygon, Point

log = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────

DEFAULT_RESOLUTION: int = 8       # ~0.74 km²  per cell
MIN_RESOLUTION:     int = 6       # ~36 km²    per cell (coarsest meaningful)
MAX_RESOLUTION:     int = 10      # ~0.015 km² per cell (finest practical)

# H3 resolution → approximate cell area in km²
H3_CELL_AREA_KM2: Dict[int, float] = {
    6:  36.1289,
    7:   5.1614,
    8:   0.7373,
    9:   0.1053,
    10:  0.0150,
}


# ──────────────────────────────────────────────────────────────────────────────
# Data structure
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class TessellatedCell:
    """
    A single H3 hexagonal cell produced by tessellation.

    Attributes
    ----------
    h3_index            : Canonical H3 index string
    admin_unit          : Name of the administrative unit this cell belongs to
    centroid_lat        : WGS84 latitude of cell centre
    centroid_lon        : WGS84 longitude of cell centre
    boundary_coords     : Cell boundary as list of (lat, lon) tuples (H3 convention)
    shapely_polygon     : Shapely Polygon for spatial operations (lon, lat axes)
    local_demand_coeff  : Fractional demand weight — set by PopulationMapper
    resolution          : H3 resolution level
    """
    h3_index:           str
    admin_unit:         str
    centroid_lat:       float
    centroid_lon:       float
    boundary_coords:    List[Tuple[float, float]]   # (lat, lon) — H3 convention
    shapely_polygon:    Polygon
    local_demand_coeff: float = 0.0
    resolution:         int   = DEFAULT_RESOLUTION

    @property
    def centroid_point(self) -> Point:
        """Shapely Point(lon, lat) — GeoJSON / Shapely axis order."""
        return Point(self.centroid_lon, self.centroid_lat)

    def to_geojson_feature(self) -> Dict:
        """Serialise to a GeoJSON Feature (lon, lat axis order)."""
        coords = [(lon, lat) for lat, lon in self.boundary_coords]
        coords.append(coords[0])  # close ring
        return {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [coords],
            },
            "properties": {
                "h3_index":           self.h3_index,
                "admin_unit":         self.admin_unit,
                "centroid_lat":       self.centroid_lat,
                "centroid_lon":       self.centroid_lon,
                "local_demand_coeff": self.local_demand_coeff,
                "resolution":         self.resolution,
            },
        }


# ──────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────────────

def _shapely_to_h3_poly(polygon: Polygon) -> h3.LatLngPoly:
    """
    Convert a Shapely Polygon (lon, lat axes) to an h3.LatLngPoly (lat, lon).
    Holes (interior rings) are also included.
    """
    # Exterior ring: Shapely stores coords as (lon, lat) → swap to (lat, lon)
    exterior = [(lat, lon) for lon, lat in polygon.exterior.coords]

    # Interior rings / holes
    holes = [
        [(lat, lon) for lon, lat in interior.coords]
        for interior in polygon.interiors
    ]

    return h3.LatLngPoly(exterior, *holes)


def _build_cell(h3_index: str, unit_name: str, resolution: int) -> TessellatedCell:
    """Construct a TessellatedCell from an H3 index string."""
    lat, lon        = h3.cell_to_latlng(h3_index)        # returns (lat, lon)
    boundary_latlon = h3.cell_to_boundary(h3_index)       # tuple of (lat, lon)

    # Build Shapely polygon in (lon, lat) order for Shapely / GeoJSON compat
    shapely_coords = [(pt[1], pt[0]) for pt in boundary_latlon]
    shapely_coords.append(shapely_coords[0])              # close ring
    poly = Polygon(shapely_coords)

    return TessellatedCell(
        h3_index=h3_index,
        admin_unit=unit_name,
        centroid_lat=lat,
        centroid_lon=lon,
        boundary_coords=list(boundary_latlon),
        shapely_polygon=poly,
        resolution=resolution,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Main engine
# ──────────────────────────────────────────────────────────────────────────────

class H3TessellationEngine:
    """
    Fill administrative unit polygons with H3 cells.

    Parameters
    ----------
    resolution              : H3 resolution (6–10). Default 8.
    fill_partial_edge_cells : When the polygon is too small for polyfill,
                              fall back to the centroid cell so every unit
                              has at least one cell.
    """

    def __init__(
        self,
        resolution: int = DEFAULT_RESOLUTION,
        fill_partial_edge_cells: bool = True,
    ):
        if not (MIN_RESOLUTION <= resolution <= MAX_RESOLUTION):
            raise ValueError(
                f"Resolution {resolution} out of range "
                f"[{MIN_RESOLUTION}, {MAX_RESOLUTION}]."
            )
        self.resolution = resolution
        self.fill_partial_edge_cells = fill_partial_edge_cells
        self._cell_area_km2 = H3_CELL_AREA_KM2.get(resolution, 0.74)

    # ── Single-unit tessellation ───────────────────────────────────────────────

    def tessellate_unit(
        self,
        unit_name: str,
        polygon: Polygon,
    ) -> List[TessellatedCell]:
        """
        Fill a single administrative unit polygon with H3 cells.

        Parameters
        ----------
        unit_name : Name tag embedded in each cell.
        polygon   : Shapely Polygon in WGS84 (lon, lat axes).

        Returns
        -------
        Sorted list of TessellatedCell.
        """
        h3_poly = _shapely_to_h3_poly(polygon)
        h3_indexes: Set[str] = h3.polygon_to_cells(h3_poly, self.resolution)

        # Fallback for very small polygons that yield zero cells
        if not h3_indexes and self.fill_partial_edge_cells:
            centroid = polygon.centroid
            fallback = h3.latlng_to_cell(centroid.y, centroid.x, self.resolution)
            h3_indexes = {fallback}
            log.debug(
                "[Tessellation] %s polygon too small for polyfill at res=%d "
                "— using centroid cell %s.",
                unit_name, self.resolution, fallback,
            )

        cells = [_build_cell(idx, unit_name, self.resolution) for idx in h3_indexes]
        cells.sort(key=lambda c: c.h3_index)

        log.debug(
            "[Tessellation] %s → %d cells (res=%d, ~%.4f km² each).",
            unit_name, len(cells), self.resolution, self._cell_area_km2,
        )
        return cells

    # ── Full-network tessellation ──────────────────────────────────────────────

    def build_full_grid(
        self,
        admin_gdf: gpd.GeoDataFrame,
        name_col: str = "name",
    ) -> Tuple[List[TessellatedCell], Dict]:
        """
        Tessellate all administrative units in a GeoDataFrame.

        Parameters
        ----------
        admin_gdf : GeoDataFrame from BoundaryLoader (CRS must be EPSG:4326).
        name_col  : Column holding the unit name.

        Returns
        -------
        cells   : Flat list of TessellatedCell across all units (no duplicates).
        summary : Dict with per-unit stats and global totals.
        """
        if admin_gdf.crs is None or admin_gdf.crs.to_epsg() != 4326:
            raise ValueError(
                f"[Tessellation] admin_gdf must be EPSG:4326. Got: {admin_gdf.crs}"
            )

        all_cells:    List[TessellatedCell] = []
        seen_indexes: Set[str]              = set()
        summary: Dict = {
            "per_unit":    {},
            "total_cells": 0,
            "resolution":  self.resolution,
        }

        for _, row in admin_gdf.iterrows():
            unit_name = row[name_col]
            polygon   = row["geometry"]

            raw_cells = self.tessellate_unit(unit_name, polygon)

            # Deduplicate: border cells go to whichever unit claimed them first
            unique: List[TessellatedCell] = []
            for cell in raw_cells:
                if cell.h3_index not in seen_indexes:
                    seen_indexes.add(cell.h3_index)
                    unique.append(cell)

            border_absorbed = len(raw_cells) - len(unique)
            if border_absorbed:
                log.debug(
                    "[Tessellation] %s: %d border cell(s) absorbed by adjacent units.",
                    unit_name, border_absorbed,
                )

            all_cells.extend(unique)
            summary["per_unit"][unit_name] = {
                "cell_count":      len(unique),
                "raw_cell_count":  len(raw_cells),
                "border_absorbed": border_absorbed,
            }

        summary["total_cells"] = len(all_cells)
        log.info(
            "[Tessellation] Complete: %d total cells at res=%d across %d units.",
            len(all_cells), self.resolution, len(admin_gdf),
        )
        return all_cells, summary

    # ── Static H3 utilities (v4 API) ──────────────────────────────────────────

    @staticmethod
    def latlon_to_h3(lat: float, lon: float, resolution: int = DEFAULT_RESOLUTION) -> str:
        """Convert a WGS84 point to its containing H3 cell index."""
        return h3.latlng_to_cell(lat, lon, resolution)

    @staticmethod
    def h3_to_latlon(h3_index: str) -> Tuple[float, float]:
        """Return (lat, lon) centroid of an H3 cell."""
        return h3.cell_to_latlng(h3_index)

    @staticmethod
    def h3_neighbors(h3_index: str, k: int = 1) -> Set[str]:
        """Return k-ring neighbors of an H3 cell (excluding the cell itself)."""
        ring = h3.grid_disk(h3_index, k)
        ring.discard(h3_index)
        return ring

    @staticmethod
    def cell_resolution(h3_index: str) -> int:
        """Return the resolution of an H3 cell."""
        return h3.get_resolution(h3_index)

    @staticmethod
    def h3_distance(a: str, b: str) -> int:
        """Grid distance (hop count) between two H3 cells at the same resolution."""
        return h3.grid_distance(a, b)

    # ── Export helpers ────────────────────────────────────────────────────────

    @staticmethod
    def cells_to_geodataframe(cells: List[TessellatedCell]) -> gpd.GeoDataFrame:
        """Convert a list of TessellatedCell to a GeoDataFrame (EPSG:4326)."""
        records = [
            {
                "h3_index":           c.h3_index,
                "admin_unit":         c.admin_unit,
                "centroid_lat":       c.centroid_lat,
                "centroid_lon":       c.centroid_lon,
                "local_demand_coeff": c.local_demand_coeff,
                "resolution":         c.resolution,
                "geometry":           c.shapely_polygon,
            }
            for c in cells
        ]
        return gpd.GeoDataFrame(records, crs="EPSG:4326")

    @staticmethod
    def cells_to_geojson(cells: List[TessellatedCell]) -> Dict:
        """Serialise all cells to a GeoJSON FeatureCollection."""
        return {
            "type": "FeatureCollection",
            "features": [c.to_geojson_feature() for c in cells],
        }
