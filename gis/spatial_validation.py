# filename: gis/spatial_validation.py
"""
SpatialValidator — enforces spatial and demographic integrity constraints
before data enters the optimisation pipeline.

All validation methods return a ValidationReport (pass/fail + structured
diagnostics).  Callers can choose to raise on first failure or collect all
violations.

Checks implemented
──────────────────
1.  CRS compliance          – all layers in EPSG:4326
2.  Population conservation – cells sum exactly to 807 029
3.  Demand weight normalisation – weights sum to 1.0 ± tolerance
4.  Coordinate bounds       – all points within Tirana bounding box (+ margin)
5.  H3 index uniqueness     – no duplicate cell indexes
6.  H3 resolution uniformity – all cells at the same resolution
7.  Boundary integrity      – no self-intersecting polygons, no empty geometries
8.  Unit completeness       – all 14 expected units present
9.  Population positivity   – no unit with population ≤ 0
10. Centroid containment    – each cell centroid lies inside its assigned unit
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import geopandas as gpd
from shapely.validation import explain_validity

from gis.administrative_units import TOTAL_POPULATION, UNIT_NAMES
from gis.h3_tessellation import TessellatedCell

log = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Tirana bounding box (with generous 5 % margin to handle boundary cells)
# ──────────────────────────────────────────────────────────────────────────────

TIRANA_BOUNDS = {
    "min_lon": 19.50,
    "max_lon": 20.25,
    "min_lat": 41.10,
    "max_lat": 41.55,
}

# Tolerances
WEIGHT_SUM_TOLERANCE: float = 1e-6
POP_CONSERVATION_TOLERANCE: int = 1    # allow ±1 resident due to rounding


# ──────────────────────────────────────────────────────────────────────────────
# Report data structure
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class ValidationViolation:
    check:   str
    message: str
    details: Optional[Any] = None


@dataclass
class ValidationReport:
    passed:     bool = True
    violations: List[ValidationViolation] = field(default_factory=list)
    warnings:   List[str] = field(default_factory=list)

    def fail(self, check: str, message: str, details: Any = None) -> None:
        self.passed = False
        self.violations.append(ValidationViolation(check, message, details))
        log.error("[SpatialValidation] FAIL [%s]: %s", check, message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)
        log.warning("[SpatialValidation] WARN: %s", message)

    def assert_passed(self) -> None:
        """Raise ValueError with full violation report if any check failed."""
        if not self.passed:
            lines = [f"  [{v.check}] {v.message}" for v in self.violations]
            raise ValueError(
                "Spatial validation failed with "
                f"{len(self.violations)} violation(s):\n" + "\n".join(lines)
            )

    def summary(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        return (
            f"[SpatialValidation] {status} — "
            f"{len(self.violations)} violation(s), "
            f"{len(self.warnings)} warning(s)."
        )


# ──────────────────────────────────────────────────────────────────────────────
# Validator
# ──────────────────────────────────────────────────────────────────────────────

class SpatialValidator:
    """
    Run spatial and demographic integrity checks.

    Usage
    -----
    >>> report = SpatialValidator.validate_all(admin_gdf, cells)
    >>> report.assert_passed()   # raises if any check failed
    """

    # ── 1.  CRS compliance ────────────────────────────────────────────────────

    @staticmethod
    def check_crs(gdf: gpd.GeoDataFrame, label: str = "GeoDataFrame") -> ValidationReport:
        report = ValidationReport()
        if gdf.crs is None:
            report.fail("CRS", f"{label}: CRS is not set.")
        elif gdf.crs.to_epsg() != 4326:
            report.fail(
                "CRS",
                f"{label}: Expected EPSG:4326, got {gdf.crs.to_string()}.",
            )
        return report

    # ── 2.  Population conservation ───────────────────────────────────────────

    @staticmethod
    def check_population_conservation(
        cells: List[TessellatedCell],
        expected_total: int = TOTAL_POPULATION,
        tolerance: int = POP_CONSERVATION_TOLERANCE,
    ) -> ValidationReport:
        """
        Verify that the sum of cell-allocated populations equals 807 029.
        The cell population is reconstructed from local_demand_coeff × 807 029.
        """
        report = ValidationReport()
        total_weight = sum(c.local_demand_coeff for c in cells)
        reconstructed_pop = round(total_weight * expected_total)
        delta = abs(reconstructed_pop - expected_total)

        if delta > tolerance:
            report.fail(
                "PopulationConservation",
                f"Reconstructed population {reconstructed_pop} deviates from "
                f"expected {expected_total} by {delta} resident(s) "
                f"(tolerance ±{tolerance}).",
                {"reconstructed": reconstructed_pop, "expected": expected_total, "delta": delta},
            )
        else:
            log.info(
                "[SpatialValidation] Population conservation OK: %d ≈ %d (Δ=%d).",
                reconstructed_pop, expected_total, delta,
            )
        return report

    # ── 3.  Demand weight normalisation ───────────────────────────────────────

    @staticmethod
    def check_demand_weight_sum(
        cells: List[TessellatedCell],
        tolerance: float = WEIGHT_SUM_TOLERANCE,
    ) -> ValidationReport:
        report = ValidationReport()
        total = sum(c.local_demand_coeff for c in cells)
        deviation = abs(total - 1.0)
        if deviation > tolerance:
            report.fail(
                "DemandWeightNorm",
                f"Demand weights sum to {total:.10f} — deviation {deviation:.2e} "
                f"exceeds tolerance {tolerance:.2e}.",
            )
        else:
            log.info(
                "[SpatialValidation] Demand weight sum OK: %.10f (dev=%.2e).",
                total, deviation,
            )
        return report

    # ── 4.  Coordinate bounds ─────────────────────────────────────────────────

    @staticmethod
    def check_coordinate_bounds(
        cells: List[TessellatedCell],
        bounds: Optional[Dict] = None,
    ) -> ValidationReport:
        report = ValidationReport()
        b = bounds or TIRANA_BOUNDS
        out_of_bounds = []

        for cell in cells:
            lat, lon = cell.centroid_lat, cell.centroid_lon
            if not (b["min_lat"] <= lat <= b["max_lat"] and
                    b["min_lon"] <= lon <= b["max_lon"]):
                out_of_bounds.append({
                    "h3_index":  cell.h3_index,
                    "admin_unit": cell.admin_unit,
                    "lat": lat, "lon": lon,
                })

        if out_of_bounds:
            report.fail(
                "CoordinateBounds",
                f"{len(out_of_bounds)} cell(s) outside Tirana bounding box "
                f"[{b['min_lat']}, {b['max_lat']}] × [{b['min_lon']}, {b['max_lon']}].",
                out_of_bounds[:10],   # show first 10
            )
        else:
            log.info(
                "[SpatialValidation] Coordinate bounds OK: all %d cells within bbox.",
                len(cells),
            )
        return report

    # ── 5.  H3 index uniqueness ───────────────────────────────────────────────

    @staticmethod
    def check_h3_uniqueness(cells: List[TessellatedCell]) -> ValidationReport:
        report = ValidationReport()
        seen: Dict[str, str] = {}
        duplicates = []

        for cell in cells:
            if cell.h3_index in seen:
                duplicates.append({
                    "h3_index":   cell.h3_index,
                    "first_unit": seen[cell.h3_index],
                    "dupe_unit":  cell.admin_unit,
                })
            else:
                seen[cell.h3_index] = cell.admin_unit

        if duplicates:
            report.fail(
                "H3Uniqueness",
                f"{len(duplicates)} duplicate H3 index(es) found.",
                duplicates[:10],
            )
        else:
            log.info(
                "[SpatialValidation] H3 uniqueness OK: %d distinct indexes.",
                len(cells),
            )
        return report

    # ── 6.  H3 resolution uniformity ─────────────────────────────────────────

    @staticmethod
    def check_h3_resolution_uniformity(cells: List[TessellatedCell]) -> ValidationReport:
        report = ValidationReport()
        if not cells:
            report.warn("No cells provided to resolution uniformity check.")
            return report

        resolutions = {c.resolution for c in cells}
        if len(resolutions) > 1:
            report.fail(
                "H3Resolution",
                f"Cells span multiple H3 resolutions: {sorted(resolutions)}. "
                "All cells must share the same resolution.",
            )
        else:
            log.info(
                "[SpatialValidation] H3 resolution uniform: all cells at res=%d.",
                next(iter(resolutions)),
            )
        return report

    # ── 7.  Boundary integrity (GeoDataFrame) ─────────────────────────────────

    @staticmethod
    def check_boundary_integrity(gdf: gpd.GeoDataFrame) -> ValidationReport:
        report = ValidationReport()
        invalid = []
        empty   = []

        for _, row in gdf.iterrows():
            geom = row["geometry"]
            if geom is None or geom.is_empty:
                empty.append(row.get("name", "unknown"))
                continue
            if not geom.is_valid:
                reason = explain_validity(geom)
                invalid.append({"name": row.get("name", "unknown"), "reason": reason})

        if empty:
            report.fail("BoundaryIntegrity", f"Empty geometries for units: {empty}.")
        if invalid:
            report.fail(
                "BoundaryIntegrity",
                f"{len(invalid)} invalid polygon(s) found.",
                invalid,
            )
        if not empty and not invalid:
            log.info(
                "[SpatialValidation] Boundary integrity OK: all %d polygons valid.",
                len(gdf),
            )
        return report

    # ── 8.  Unit completeness ─────────────────────────────────────────────────

    @staticmethod
    def check_unit_completeness(
        gdf: gpd.GeoDataFrame,
        name_col: str = "name",
    ) -> ValidationReport:
        report = ValidationReport()
        present = set(gdf[name_col].tolist())
        expected = set(UNIT_NAMES)
        missing = expected - present
        extra   = present - expected

        if missing:
            report.fail(
                "UnitCompleteness",
                f"{len(missing)} expected unit(s) missing: {sorted(missing)}.",
            )
        if extra:
            report.warn(
                f"{len(extra)} unexpected unit(s) in boundary source: "
                f"{sorted(extra)}. They will be ignored."
            )
        if not missing:
            log.info("[SpatialValidation] Unit completeness OK: all 14 units present.")
        return report

    # ── 9.  Population positivity ─────────────────────────────────────────────

    @staticmethod
    def check_population_positivity(gdf: gpd.GeoDataFrame) -> ValidationReport:
        report = ValidationReport()
        if "population" not in gdf.columns:
            report.warn("'population' column not found — skipping positivity check.")
            return report

        non_positive = gdf[gdf["population"] <= 0]["name"].tolist()
        if non_positive:
            report.fail(
                "PopulationPositivity",
                f"Unit(s) with population ≤ 0: {non_positive}.",
            )
        else:
            log.info("[SpatialValidation] Population positivity OK.")
        return report

    # ── 10.  Centroid containment ─────────────────────────────────────────────

    @staticmethod
    def check_centroid_containment(
        cells: List[TessellatedCell],
        admin_gdf: gpd.GeoDataFrame,
        name_col: str = "name",
        max_violations_to_report: int = 10,
    ) -> ValidationReport:
        """
        Verify that each cell's centroid is geometrically inside its assigned
        administrative unit polygon.  Border cells are expected to fail; the
        check emits a warning (not a failure) if <5 % of cells are outside.
        """
        report = ValidationReport()
        unit_polygons = {
            row[name_col]: row["geometry"]
            for _, row in admin_gdf.iterrows()
        }

        outside = []
        for cell in cells:
            poly = unit_polygons.get(cell.admin_unit)
            if poly is None:
                continue
            if not poly.contains(cell.centroid_point):
                outside.append(cell.h3_index)

        pct = len(outside) / max(1, len(cells)) * 100
        if pct > 5.0:
            report.fail(
                "CentroidContainment",
                f"{len(outside)} / {len(cells)} cell centroids ({pct:.1f} %) "
                "lie outside their assigned unit — exceeds 5 % threshold.",
                outside[:max_violations_to_report],
            )
        elif outside:
            report.warn(
                f"{len(outside)} / {len(cells)} cell centroids ({pct:.1f} %) "
                "lie outside their polygon (acceptable — border cells)."
            )
        else:
            log.info("[SpatialValidation] Centroid containment OK: 0 outliers.")

        return report

    # ── Aggregate runner ──────────────────────────────────────────────────────

    @staticmethod
    def validate_admin_gdf(gdf: gpd.GeoDataFrame) -> ValidationReport:
        """Run all GeoDataFrame-level checks and merge reports."""
        aggregate = ValidationReport()

        for check_fn in [
            lambda: SpatialValidator.check_crs(gdf, "AdminGeoDataFrame"),
            lambda: SpatialValidator.check_boundary_integrity(gdf),
            lambda: SpatialValidator.check_unit_completeness(gdf),
            lambda: SpatialValidator.check_population_positivity(gdf),
        ]:
            sub = check_fn()
            aggregate.violations.extend(sub.violations)
            aggregate.warnings.extend(sub.warnings)
            if not sub.passed:
                aggregate.passed = False

        log.info("[SpatialValidation] Admin GDF check: %s", aggregate.summary())
        return aggregate

    @staticmethod
    def validate_cells(
        cells: List[TessellatedCell],
        admin_gdf: Optional[gpd.GeoDataFrame] = None,
        skip_containment: bool = False,
    ) -> ValidationReport:
        """Run all cell-level checks and optionally containment against admin_gdf."""
        aggregate = ValidationReport()

        cell_checks = [
            lambda: SpatialValidator.check_h3_uniqueness(cells),
            lambda: SpatialValidator.check_h3_resolution_uniformity(cells),
            lambda: SpatialValidator.check_coordinate_bounds(cells),
            lambda: SpatialValidator.check_population_conservation(cells),
            lambda: SpatialValidator.check_demand_weight_sum(cells),
        ]

        if admin_gdf is not None and not skip_containment:
            cell_checks.append(
                lambda: SpatialValidator.check_centroid_containment(cells, admin_gdf)
            )

        for check_fn in cell_checks:
            sub = check_fn()
            aggregate.violations.extend(sub.violations)
            aggregate.warnings.extend(sub.warnings)
            if not sub.passed:
                aggregate.passed = False

        log.info("[SpatialValidation] Cell check: %s", aggregate.summary())
        return aggregate

    @staticmethod
    def validate_all(
        admin_gdf: gpd.GeoDataFrame,
        cells: List[TessellatedCell],
        raise_on_failure: bool = False,
    ) -> ValidationReport:
        """Run all checks end-to-end."""
        aggregate = ValidationReport()

        for sub in [
            SpatialValidator.validate_admin_gdf(admin_gdf),
            SpatialValidator.validate_cells(cells, admin_gdf),
        ]:
            aggregate.violations.extend(sub.violations)
            aggregate.warnings.extend(sub.warnings)
            if not sub.passed:
                aggregate.passed = False

        log.info("[SpatialValidation] Full pipeline: %s", aggregate.summary())
        if raise_on_failure:
            aggregate.assert_passed()
        return aggregate
