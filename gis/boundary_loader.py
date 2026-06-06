# filename: gis/boundary_loader.py
"""
BoundaryLoader — loads administrative unit boundaries into a GeoDataFrame.

Priority order
--------------
1.  Real GeoJSON file (path passed explicitly or discovered from data/)
2.  Real Shapefile (.shp) — same discovery logic
3.  Canonical hardcoded boundaries from administrative_units.py

CRS contract
------------
All outputs are normalised to WGS84 / EPSG:4326.  If a source file uses a
different CRS the loader reprojects automatically and emits a warning.

Returned GeoDataFrame schema
-----------------------------
Column              Type          Description
──────────────────────────────────────────────────────────────────────────────
name                str           Administrative unit name (matches UNIT_NAMES)
population          int           2023 Census population
demand_weight       float         population / 807_029
area_km2            float         Approximate area in km²
geometry            Polygon       Shapely Polygon in WGS84
"""

from __future__ import annotations

import json
import logging
import warnings
from pathlib import Path
from typing import Dict, List, Optional

import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon, shape

from gis.administrative_units import (
    CENSUS_2023,
    TOTAL_POPULATION,
    APPROX_AREA_KM2,
    UNIT_NAMES,
    get_full_geojson_feature_collection,
)

log = logging.getLogger(__name__)

# Target CRS — all data is normalised to this
TARGET_CRS = "EPSG:4326"

# Root of the project — used for automatic file discovery
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_DATA_DIR = _PROJECT_ROOT / "data"


# ──────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────────────

def _normalise_crs(gdf: gpd.GeoDataFrame, source_label: str) -> gpd.GeoDataFrame:
    """Reproject to WGS84 if necessary."""
    if gdf.crs is None:
        warnings.warn(
            f"[BoundaryLoader] {source_label}: No CRS found — assuming WGS84.",
            UserWarning,
            stacklevel=3,
        )
        gdf = gdf.set_crs(TARGET_CRS)
    elif gdf.crs.to_epsg() != 4326:
        log.info(
            "[BoundaryLoader] %s: CRS is %s — reprojecting to %s.",
            source_label, gdf.crs.to_string(), TARGET_CRS,
        )
        gdf = gdf.to_crs(TARGET_CRS)
    return gdf


def _add_census_columns(gdf: gpd.GeoDataFrame, name_col: str) -> gpd.GeoDataFrame:
    """
    Join census data onto the GeoDataFrame using the unit name column.
    Missing units raise a ValueError so the caller discovers mismatches early.
    """
    if name_col not in gdf.columns:
        raise ValueError(
            f"[BoundaryLoader] Name column '{name_col}' not found. "
            f"Available columns: {list(gdf.columns)}"
        )

    gdf = gdf.copy()
    missing = [n for n in UNIT_NAMES if n not in gdf[name_col].values]
    if missing:
        raise ValueError(
            f"[BoundaryLoader] Boundary source is missing units: {missing}."
        )

    gdf["population"]    = gdf[name_col].map(CENSUS_2023).astype(int)
    gdf["demand_weight"] = gdf["population"] / TOTAL_POPULATION
    gdf["area_km2"]      = gdf[name_col].map(APPROX_AREA_KM2)
    gdf = gdf.rename(columns={name_col: "name"})

    # Reorder to canonical order
    name_order = {n: i for i, n in enumerate(UNIT_NAMES)}
    gdf = gdf.sort_values("name", key=lambda s: s.map(name_order)).reset_index(drop=True)

    return gdf[["name", "population", "demand_weight", "area_km2", "geometry"]]


def _build_from_canonical() -> gpd.GeoDataFrame:
    """Build GeoDataFrame from the hardcoded boundary data."""
    fc = get_full_geojson_feature_collection()
    rows = []
    for feat in fc["features"]:
        props = feat["properties"]
        geom = shape(feat["geometry"])
        rows.append({
            "name":          props["name"],
            "population":    props["population"],
            "demand_weight": props["demand_weight"],
            "area_km2":      props["area_km2"],
            "geometry":      geom,
        })

    gdf = gpd.GeoDataFrame(rows, crs=TARGET_CRS)
    # Reorder to canonical
    name_order = {n: i for i, n in enumerate(UNIT_NAMES)}
    gdf = gdf.sort_values("name", key=lambda s: s.map(name_order)).reset_index(drop=True)
    return gdf


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

class BoundaryLoader:
    """
    Loads the 14 Tirana administrative unit boundaries into a GeoDataFrame.

    Usage
    -----
    >>> gdf = BoundaryLoader.load()          # auto-discover or use canonical
    >>> gdf = BoundaryLoader.load_geojson("data/tirana_units.geojson")
    >>> gdf = BoundaryLoader.load_shapefile("data/tirana_units.shp")
    >>> gdf = BoundaryLoader.load_canonical()
    """

    # ── GeoJSON ───────────────────────────────────────────────────────────────

    @staticmethod
    def load_geojson(
        path: str | Path,
        name_col: str = "name",
    ) -> gpd.GeoDataFrame:
        """
        Load boundaries from a GeoJSON file.

        Parameters
        ----------
        path     : Path to the .geojson / .json file.
        name_col : Property name that holds the administrative unit name.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"[BoundaryLoader] GeoJSON not found: {path}")

        log.info("[BoundaryLoader] Loading GeoJSON from %s", path)
        gdf = gpd.read_file(str(path))
        gdf = _normalise_crs(gdf, str(path))
        return _add_census_columns(gdf, name_col)

    # ── Shapefile ─────────────────────────────────────────────────────────────

    @staticmethod
    def load_shapefile(
        path: str | Path,
        name_col: str = "name",
        encoding: str = "utf-8",
    ) -> gpd.GeoDataFrame:
        """
        Load boundaries from an ESRI Shapefile (.shp).

        Parameters
        ----------
        path     : Path to the .shp file (sibling .dbf/.shx must exist).
        name_col : Attribute field name holding the administrative unit name.
        encoding : Encoding of the .dbf attribute table.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"[BoundaryLoader] Shapefile not found: {path}")

        log.info("[BoundaryLoader] Loading Shapefile from %s", path)
        gdf = gpd.read_file(str(path), encoding=encoding)
        gdf = _normalise_crs(gdf, str(path))
        return _add_census_columns(gdf, name_col)

    # ── Canonical fallback ────────────────────────────────────────────────────

    @staticmethod
    def load_canonical() -> gpd.GeoDataFrame:
        """
        Build GeoDataFrame from the hardcoded approximate boundary polygons
        in gis/administrative_units.py.  No external files required.
        """
        log.info(
            "[BoundaryLoader] Using canonical hardcoded boundaries "
            "(no external GIS file found)."
        )
        return _build_from_canonical()

    # ── Auto-discovery ────────────────────────────────────────────────────────

    @staticmethod
    def load(
        geojson_path: Optional[str | Path] = None,
        shapefile_path: Optional[str | Path] = None,
        name_col: str = "name",
    ) -> gpd.GeoDataFrame:
        """
        Auto-load: tries GeoJSON → Shapefile → canonical fallback.

        Parameters
        ----------
        geojson_path   : Explicit GeoJSON path (optional).
        shapefile_path : Explicit Shapefile path (optional).
        name_col       : Attribute / property name for the unit name.
        """
        # 1. Explicit paths
        if geojson_path:
            return BoundaryLoader.load_geojson(geojson_path, name_col)
        if shapefile_path:
            return BoundaryLoader.load_shapefile(shapefile_path, name_col)

        # 2. Auto-discover in data/
        for candidate in sorted(_DATA_DIR.glob("*.geojson")) + sorted(_DATA_DIR.glob("*.json")):
            try:
                gdf = BoundaryLoader.load_geojson(candidate, name_col)
                log.info("[BoundaryLoader] Auto-discovered GeoJSON: %s", candidate)
                return gdf
            except Exception as exc:
                log.debug("[BoundaryLoader] Skipping %s: %s", candidate, exc)

        for candidate in sorted(_DATA_DIR.glob("*.shp")):
            try:
                gdf = BoundaryLoader.load_shapefile(candidate, name_col)
                log.info("[BoundaryLoader] Auto-discovered Shapefile: %s", candidate)
                return gdf
            except Exception as exc:
                log.debug("[BoundaryLoader] Skipping %s: %s", candidate, exc)

        # 3. Canonical fallback
        return BoundaryLoader.load_canonical()

    # ── Utilities ─────────────────────────────────────────────────────────────

    @staticmethod
    def export_canonical_geojson(output_path: str | Path) -> Path:
        """
        Write the canonical boundary data to a GeoJSON file so it can be
        inspected in QGIS or used as a starting point for real boundaries.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        gdf = BoundaryLoader.load_canonical()
        gdf.to_file(str(output_path), driver="GeoJSON")
        log.info("[BoundaryLoader] Exported canonical GeoJSON to %s", output_path)
        return output_path

    @staticmethod
    def compute_area_km2(gdf: gpd.GeoDataFrame) -> pd.Series:
        """
        Compute actual polygon area in km² using an equal-area projection.
        Returns a Series indexed like gdf.
        """
        projected = gdf.to_crs("EPSG:3857")       # Web Mercator (metres)
        return projected.geometry.area / 1_000_000  # m² → km²
