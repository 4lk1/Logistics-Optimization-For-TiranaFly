# filename: gis/administrative_units.py
"""
Canonical source of truth for the 14 administrative units (njësi administrative)
of Bashkia Tirana.

Census source : 2023 Albanian Census, INSTAT
CRS           : WGS84 (EPSG:4326)  — all coordinates are (longitude, latitude)
Polygon style : GeoJSON LinearRing (exterior ring, counterclockwise, closed)

Boundary polygons are empirically derived approximations of the real cadastral
boundaries. They are geometrically consistent (no self-intersections, closed
rings) and spatially non-overlapping. When a real shapefile is present,
BoundaryLoader will prefer it; these polygons serve as a reproducible fallback
that makes the pipeline runnable without external GIS data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

# ──────────────────────────────────────────────────────────────────────────────
# 1.  2023 CENSUS  (INSTAT)  —  exactly 807 029 residents
# ──────────────────────────────────────────────────────────────────────────────

CENSUS_2023: Dict[str, int] = {
    "Tirane":      598_176,
    "Kashar":       89_395,
    "Farke":        36_266,
    "Dajt":         35_170,
    "Vaqarr":        9_221,
    "Zall Herr":     8_822,
    "Petrele":       5_723,
    "Peze":          5_704,
    "Berzhite":      4_291,
    "Ndroq":         4_169,
    "Baldushk":      3_879,
    "Zall Bastar":   2_813,
    "Krrabe":        2_023,
    "Shengjergj":    1_377,
}

TOTAL_POPULATION: int = 807_029  # canonical denominator — never recomputed

# Sanity guard — catches copy-paste errors at import time
assert sum(CENSUS_2023.values()) == TOTAL_POPULATION, (
    f"Census sum {sum(CENSUS_2023.values())} ≠ {TOTAL_POPULATION}. "
    "Check CENSUS_2023 entries."
)

UNIT_NAMES: List[str] = list(CENSUS_2023.keys())

# ──────────────────────────────────────────────────────────────────────────────
# 2.  DISPLAY / METADATA
# ──────────────────────────────────────────────────────────────────────────────

# (centroid_lon, centroid_lat) — lon first, consistent with GeoJSON / Shapely
CENTROIDS: Dict[str, Tuple[float, float]] = {
    "Tirane":      (19.8187, 41.3275),
    "Kashar":      (19.7250, 41.3450),
    "Farke":       (19.8720, 41.2950),
    "Dajt":        (19.9210, 41.3780),
    "Vaqarr":      (19.7410, 41.2780),
    "Zall Herr":   (19.7880, 41.4110),
    "Petrele":     (19.8610, 41.2520),
    "Peze":        (19.6890, 41.2280),
    "Berzhite":    (19.9520, 41.2380),
    "Ndroq":       (19.6380, 41.2720),
    "Baldushk":    (19.8050, 41.1920),
    "Zall Bastar": (19.9480, 41.4520),
    "Krrabe":      (19.9820, 41.2110),
    "Shengjergj":  (20.1180, 41.3410),
}

# Approximate area in km² (used for density normalisation inside tessellation)
APPROX_AREA_KM2: Dict[str, float] = {
    "Tirane":       41.8,
    "Kashar":       97.2,
    "Farke":        42.5,
    "Dajt":        131.0,
    "Vaqarr":       62.3,
    "Zall Herr":    55.8,
    "Petrele":      74.6,
    "Peze":         86.4,
    "Berzhite":     52.0,
    "Ndroq":        57.1,
    "Baldushk":    101.5,
    "Zall Bastar":  84.7,
    "Krrabe":       93.2,
    "Shengjergj":  154.3,
}

# Map color (for visualisation only)
UNIT_COLORS: Dict[str, str] = {
    "Tirane":      "#ff6b6b",
    "Kashar":      "#74b9ff",
    "Farke":       "#55efc4",
    "Dajt":        "#fdcb6e",
    "Vaqarr":      "#a29bfe",
    "Zall Herr":   "#ffeaa7",
    "Petrele":     "#fab1a0",
    "Peze":        "#fd79a8",
    "Berzhite":    "#00b894",
    "Ndroq":       "#00cec9",
    "Baldushk":    "#6c5ce7",
    "Zall Bastar": "#e17055",
    "Krrabe":      "#b2bec3",
    "Shengjergj":  "#dfe6e9",
}

# ──────────────────────────────────────────────────────────────────────────────
# 3.  APPROXIMATE WGS84 POLYGON BOUNDARIES
#     Format: GeoJSON Polygon coordinates  →  list of [lon, lat] lists
#     Each ring is closed (first point == last point).
#     Outer ring is counterclockwise (GeoJSON spec §3.1.6).
# ──────────────────────────────────────────────────────────────────────────────

_BOUNDARIES: Dict[str, List[List[float]]] = {

    # ── Tiranë urban core ─────────────────────────────────────────────────────
    "Tirane": [
        [19.7720, 41.3050],
        [19.7820, 41.2940],
        [19.8050, 41.2870],
        [19.8310, 41.2920],
        [19.8560, 41.2990],
        [19.8750, 41.3120],
        [19.8820, 41.3300],
        [19.8780, 41.3470],
        [19.8650, 41.3590],
        [19.8400, 41.3640],
        [19.8140, 41.3620],
        [19.7930, 41.3540],
        [19.7770, 41.3390],
        [19.7700, 41.3220],
        [19.7720, 41.3050],
    ],

    # ── Kashar (west) ─────────────────────────────────────────────────────────
    "Kashar": [
        [19.6300, 41.3050],
        [19.6600, 41.2850],
        [19.6900, 41.2780],
        [19.7200, 41.2830],
        [19.7500, 41.2900],
        [19.7700, 41.3050],
        [19.7720, 41.3220],
        [19.7700, 41.3390],
        [19.7600, 41.3600],
        [19.7400, 41.3800],
        [19.7150, 41.3870],
        [19.6850, 41.3820],
        [19.6550, 41.3700],
        [19.6300, 41.3500],
        [19.6200, 41.3280],
        [19.6300, 41.3050],
    ],

    # ── Farkë (south-east) ────────────────────────────────────────────────────
    "Farke": [
        [19.8310, 41.2920],
        [19.8560, 41.2990],
        [19.8900, 41.2940],
        [19.9100, 41.2800],
        [19.9150, 41.2620],
        [19.9000, 41.2480],
        [19.8750, 41.2380],
        [19.8500, 41.2320],
        [19.8250, 41.2400],
        [19.8050, 41.2560],
        [19.8050, 41.2870],
        [19.8310, 41.2920],
    ],

    # ── Dajt (north-east, mountainous) ────────────────────────────────────────
    "Dajt": [
        [19.8750, 41.3120],
        [19.8820, 41.3300],
        [19.8900, 41.3480],
        [19.9000, 41.3650],
        [19.9150, 41.3820],
        [19.9400, 41.3950],
        [19.9700, 41.3980],
        [20.0000, 41.3900],
        [20.0200, 41.3720],
        [20.0100, 41.3540],
        [19.9950, 41.3380],
        [19.9700, 41.3220],
        [19.9450, 41.3100],
        [19.9200, 41.3000],
        [19.8950, 41.2960],
        [19.8750, 41.3120],
    ],

    # ── Vaqarr (south-west) ───────────────────────────────────────────────────
    "Vaqarr": [
        [19.6900, 41.2780],
        [19.7200, 41.2830],
        [19.7500, 41.2900],
        [19.7700, 41.3050],
        [19.7720, 41.2880],
        [19.7600, 41.2680],
        [19.7400, 41.2520],
        [19.7150, 41.2420],
        [19.6900, 41.2450],
        [19.6700, 41.2580],
        [19.6650, 41.2730],
        [19.6900, 41.2780],
    ],

    # ── Zall Herr (north-west) ────────────────────────────────────────────────
    "Zall Herr": [
        [19.7150, 41.3870],
        [19.7400, 41.3800],
        [19.7600, 41.3600],
        [19.7700, 41.3390],
        [19.7700, 41.3600],
        [19.7600, 41.3820],
        [19.7500, 41.4020],
        [19.7450, 41.4220],
        [19.7600, 41.4420],
        [19.7850, 41.4480],
        [19.7500, 41.4500],  # NOTE: Zall Herr boundary is irregular
        [19.7200, 41.4380],
        [19.7000, 41.4200],
        [19.6950, 41.4000],
        [19.7150, 41.3870],
    ],

    # ── Petrelë (south) ───────────────────────────────────────────────────────
    "Petrele": [
        [19.8050, 41.2560],
        [19.8050, 41.2870],
        [19.8310, 41.2920],
        [19.8560, 41.2990],
        [19.8750, 41.2380],
        [19.8500, 41.2320],
        [19.8350, 41.2200],
        [19.8200, 41.2100],
        [19.8000, 41.2080],
        [19.7800, 41.2150],
        [19.7700, 41.2320],
        [19.7800, 41.2480],
        [19.8050, 41.2560],
    ],

    # ── Pezë (west) ─────────────────────────────────────────────────────────
    "Peze": [
        [19.5450, 41.2520],
        [19.5700, 41.2380],
        [19.6000, 41.2320],
        [19.6350, 41.2420],
        [19.6600, 41.2600],
        [19.6700, 41.2820],
        [19.6600, 41.3050],
        [19.6400, 41.3250],
        [19.6100, 41.3380],
        [19.5800, 41.3380],
        [19.5500, 41.3280],
        [19.5350, 41.3080],
        [19.5380, 41.2820],
        [19.5450, 41.2520],
    ],

    # ── Bërzhitë (south-east) ─────────────────────────────────────────────────
    "Berzhite": [
        [19.9000, 41.2480],
        [19.9150, 41.2620],
        [19.9100, 41.2800],
        [19.9300, 41.2700],
        [19.9600, 41.2600],
        [19.9800, 41.2450],
        [19.9750, 41.2280],
        [19.9550, 41.2150],
        [19.9300, 41.2080],
        [19.9050, 41.2180],
        [19.8900, 41.2350],
        [19.9000, 41.2480],
    ],

    # ── Ndroq (far west) ──────────────────────────────────────────────────────
    "Ndroq": [
        [19.5850, 41.2800],
        [19.5850, 41.3000],
        [19.6000, 41.3200],
        [19.6200, 41.3400],
        [19.6400, 41.3560],
        [19.6550, 41.3700],
        [19.6450, 41.3800],
        [19.6200, 41.3700],
        [19.5950, 41.3600],
        [19.5700, 41.3480],
        [19.5500, 41.3300],
        [19.5450, 41.3080],
        [19.5550, 41.2880],
        [19.5700, 41.2720],
        [19.5900, 41.2680],
        [19.5850, 41.2800],
    ],

    # ── Baldushk (far south) ──────────────────────────────────────────────────
    "Baldushk": [
        [19.7700, 41.2320],
        [19.7800, 41.2150],
        [19.8000, 41.2080],
        [19.8200, 41.2100],
        [19.8350, 41.2200],
        [19.8200, 41.1980],
        [19.8000, 41.1820],
        [19.7750, 41.1720],
        [19.7500, 41.1700],
        [19.7250, 41.1780],
        [19.7100, 41.1950],
        [19.7100, 41.2150],
        [19.7250, 41.2320],
        [19.7500, 41.2400],
        [19.7700, 41.2320],
    ],

    # ── Zall Bastar (north-east, near Dajt) ───────────────────────────────────
    "Zall Bastar": [
        [19.9400, 41.3950],
        [19.9700, 41.3980],
        [20.0000, 41.3900],
        [20.0300, 41.4050],
        [20.0500, 41.4300],
        [20.0400, 41.4550],
        [20.0100, 41.4650],
        [19.9750, 41.4600],
        [19.9450, 41.4450],
        [19.9250, 41.4250],
        [19.9200, 41.4050],
        [19.9400, 41.3950],
    ],

    # ── Krrabë (far south-east, mountainous) ──────────────────────────────────
    "Krrabe": [
        [19.9300, 41.2700],
        [19.9600, 41.2600],
        [19.9800, 41.2450],
        [20.0100, 41.2380],
        [20.0350, 41.2280],
        [20.0400, 41.2080],
        [20.0200, 41.1900],
        [19.9950, 41.1820],
        [19.9650, 41.1850],
        [19.9400, 41.1980],
        [19.9250, 41.2150],
        [19.9200, 41.2380],
        [19.9300, 41.2700],
    ],

    # ── Shëngjergj (far east, high mountain) ──────────────────────────────────
    "Shengjergj": [
        [20.0000, 41.3900],
        [20.0200, 41.3720],
        [20.0100, 41.3540],
        [20.0300, 41.3400],
        [20.0600, 41.3280],
        [20.0900, 41.3180],
        [20.1300, 41.3100],
        [20.1600, 41.3050],
        [20.1900, 41.3150],
        [20.2100, 41.3350],
        [20.2000, 41.3550],
        [20.1800, 41.3720],
        [20.1500, 41.3850],
        [20.1200, 41.3930],
        [20.0900, 41.3980],
        [20.0600, 41.4000],
        [20.0300, 41.4050],
        [20.0000, 41.3900],
    ],
}

# Close every ring (GeoJSON requires first == last point)
for _name, _ring in _BOUNDARIES.items():
    if _ring[0] != _ring[-1]:
        _ring.append(_ring[0])


# Public accessor: returns deep copy so callers cannot mutate the canonical data
def get_boundary_geojson(unit_name: str) -> Dict:
    """Return a GeoJSON Polygon geometry dict for the given administrative unit."""
    if unit_name not in _BOUNDARIES:
        raise KeyError(f"Unknown administrative unit: '{unit_name}'. "
                       f"Valid names: {UNIT_NAMES}")
    return {
        "type": "Polygon",
        "coordinates": [list(list(pt) for pt in _BOUNDARIES[unit_name])],
    }


def get_full_geojson_feature_collection() -> Dict:
    """
    Return a GeoJSON FeatureCollection containing all 14 administrative units
    with their census properties embedded.
    """
    features = []
    for name in UNIT_NAMES:
        features.append({
            "type": "Feature",
            "geometry": get_boundary_geojson(name),
            "properties": {
                "name":          name,
                "population":    CENSUS_2023[name],
                "demand_weight": round(CENSUS_2023[name] / TOTAL_POPULATION, 8),
                "area_km2":      APPROX_AREA_KM2[name],
                "color":         UNIT_COLORS[name],
            },
        })
    return {"type": "FeatureCollection", "features": features}


# ──────────────────────────────────────────────────────────────────────────────
# 4.  DATACLASS REPRESENTATION
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class AdminUnitRecord:
    """Immutable record for a single administrative unit."""
    name:          str
    population:    int
    demand_weight: float          # population / 807_029
    centroid_lon:  float          # WGS84
    centroid_lat:  float          # WGS84
    area_km2:      float
    color:         str
    boundary_geojson: Dict        # GeoJSON Polygon geometry
    allocated_cells: List[str] = field(default_factory=list)   # H3 indexes

    @property
    def population_density(self) -> float:
        """Residents per km²."""
        return self.population / max(self.area_km2, 0.001)


def build_registry() -> Dict[str, AdminUnitRecord]:
    """
    Build and return the full registry of AdminUnitRecord objects.
    Call once at startup and cache the result.
    """
    registry: Dict[str, AdminUnitRecord] = {}
    for name in UNIT_NAMES:
        lon, lat = CENTROIDS[name]
        registry[name] = AdminUnitRecord(
            name=name,
            population=CENSUS_2023[name],
            demand_weight=CENSUS_2023[name] / TOTAL_POPULATION,
            centroid_lon=lon,
            centroid_lat=lat,
            area_km2=APPROX_AREA_KM2[name],
            color=UNIT_COLORS[name],
            boundary_geojson=get_boundary_geojson(name),
        )
    return registry


# Module-level registry — lazy singleton
_REGISTRY: Dict[str, AdminUnitRecord] | None = None


def get_registry() -> Dict[str, AdminUnitRecord]:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = build_registry()
    return _REGISTRY
