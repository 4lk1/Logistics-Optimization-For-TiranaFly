# filename: gis/h3_grid.py
"""
H3GridEngine — thin compatibility wrapper for H3 v4 API.

The existing codebase references this class through the legacy module name.
New code should prefer gis/h3_tessellation.py (H3TessellationEngine).

H3 v4 API notes
───────────────
  h3.latlng_to_cell(lat, lon, res)   ←  was geo_to_h3
  h3.cell_to_latlng(cell)            ←  was h3_to_geo       → (lat, lon)
  h3.cell_to_boundary(cell)          ←  was h3_to_geo_boundary → tuple[(lat,lon)]
  h3.polygon_to_cells(poly, res)     ←  was polyfill         (poly = LatLngPoly)
  h3.grid_disk(cell, k)              ←  was k_ring
"""

from __future__ import annotations

from typing import Dict, List, Tuple

import h3
from shapely.geometry import Polygon


class H3GridEngine:
    """Lightweight H3 cell operations — H3 v4 compatible."""

    def __init__(self, resolution: int = 8) -> None:
        self.resolution = resolution

    def latlon_to_h3(self, lat: float, lon: float) -> str:
        return h3.latlng_to_cell(lat, lon, self.resolution)

    def h3_to_centroid(self, h3_index: str) -> Tuple[float, float]:
        """Returns (lat, lon)."""
        return h3.cell_to_latlng(h3_index)

    def h3_to_polygon(self, h3_index: str) -> Polygon:
        """Return Shapely Polygon in (lon, lat) axis order."""
        boundary = h3.cell_to_boundary(h3_index)   # tuple of (lat, lon)
        coords   = [(pt[1], pt[0]) for pt in boundary]
        coords.append(coords[0])
        return Polygon(coords)

    def fill_polygon_with_h3(self, geojson_geometry: Dict) -> List[str]:
        """
        Fill a GeoJSON Polygon geometry with H3 cells.

        geojson_geometry format:
            {"type": "Polygon", "coordinates": [[[lon, lat], ...]]}
        """
        coords_lonlat = geojson_geometry["coordinates"][0]  # exterior ring
        # H3 v4 LatLngPoly expects (lat, lon) tuples
        exterior_latlng = [(lat, lon) for lon, lat in coords_lonlat]
        h3_poly = h3.LatLngPoly(exterior_latlng)
        return sorted(h3.polygon_to_cells(h3_poly, self.resolution))