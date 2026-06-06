# filename: gis/population_mapper.py
"""
PopulationMapper — distributes the 2023 Census populations (807 029 residents)
from administrative units to H3 hexagonal cells.

Algorithm
─────────
1.  For each administrative unit, compute its total cell count.
2.  Distribute population proportionally using a floating-point weight per cell:
        base_population_i = (population_unit / n_cells_in_unit)
3.  Convert float allocations to integers using the Largest-Remainder Method
    (Hamilton method) to guarantee:
        sum(allocated_int) == population_unit   for every unit
    and therefore:
        sum(all allocated integers) == 807 029   across the whole network.
4.  Convert integer allocations to demand weight coefficients:
        local_demand_coeff = allocated_population / 807 029
5.  Update TessellatedCell.local_demand_coeff in-place.

The Largest-Remainder Method is the standard technique used by electoral
apportionment and census data distribution systems to prevent rounding drift.

References
──────────
Hamilton, A. (1792). Report on Apportionment.
Balinski, M. L. & Young, H. P. (1982). Fair Representation. Yale University Press.
"""

from __future__ import annotations

import logging
import math
from typing import Dict, List, Tuple

import geopandas as gpd

from gis.administrative_units import (
    CENSUS_2023,
    TOTAL_POPULATION,
    UNIT_NAMES,
    AdminUnitRecord,
    get_registry,
)
from gis.h3_tessellation import TessellatedCell

log = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Largest-Remainder (Hamilton) integer allocation
# ──────────────────────────────────────────────────────────────────────────────

def _largest_remainder(total_int: int, float_shares: List[float]) -> List[int]:
    """
    Distribute `total_int` as integers proportional to `float_shares`.
    Guarantees sum(result) == total_int exactly.

    Parameters
    ----------
    total_int    : Integer to distribute (e.g. unit population).
    float_shares : Non-negative weights (need not sum to 1).

    Returns
    -------
    List of non-negative integers with the same length as float_shares.
    """
    n = len(float_shares)
    if n == 0:
        return []

    total_weight = sum(float_shares)
    if total_weight == 0.0:
        # Distribute evenly (edge case: all weights are 0)
        base = total_int // n
        result = [base] * n
        remainder = total_int - sum(result)
        for i in range(remainder):
            result[i] += 1
        return result

    # Exact real allocation for each cell
    exact = [(w / total_weight) * total_int for w in float_shares]

    # Floor allocation
    floors = [int(math.floor(e)) for e in exact]
    remainders = [e - f for e, f in zip(exact, floors)]

    # Distribute leftover seats by largest fractional remainder
    shortfall = total_int - sum(floors)
    ranked = sorted(range(n), key=lambda i: remainders[i], reverse=True)

    for i in range(shortfall):
        floors[ranked[i]] += 1

    assert sum(floors) == total_int, (
        f"LR allocation failed: sum={sum(floors)} ≠ {total_int}"
    )
    return floors


# ──────────────────────────────────────────────────────────────────────────────
# AllocationResult
# ──────────────────────────────────────────────────────────────────────────────

class AllocationResult:
    """Container for mapping audit data."""

    def __init__(self) -> None:
        self.per_unit:          Dict[str, Dict] = {}
        self.total_allocated:   int             = 0
        self.total_cells:       int             = 0
        self.weight_sum:        float           = 0.0

    def add_unit(
        self,
        unit: str,
        population: int,
        cells: int,
        allocated_pop: int,
    ) -> None:
        self.per_unit[unit] = {
            "census_population":  population,
            "allocated_population": allocated_pop,
            "cell_count":         cells,
            "mean_pop_per_cell":  allocated_pop / max(1, cells),
        }
        self.total_allocated += allocated_pop
        self.total_cells     += cells

    def finalize(self, weight_sum: float) -> None:
        self.weight_sum = weight_sum

    def validate(self) -> None:
        """Raise if invariants are violated."""
        if self.total_allocated != TOTAL_POPULATION:
            raise ValueError(
                f"Population conservation violated: "
                f"allocated {self.total_allocated} ≠ expected {TOTAL_POPULATION}."
            )
        deviation = abs(self.weight_sum - 1.0)
        if deviation > 1e-9:
            raise ValueError(
                f"Demand weight normalisation violated: "
                f"sum={self.weight_sum:.12f}, deviation={deviation:.2e}."
            )
        log.info(
            "[PopulationMapper] Validation passed: "
            "%d residents → %d cells, weight_sum=%.10f",
            self.total_allocated, self.total_cells, self.weight_sum,
        )

    def __repr__(self) -> str:
        return (
            f"AllocationResult(total_pop={self.total_allocated}, "
            f"total_cells={self.total_cells}, "
            f"weight_sum={self.weight_sum:.10f})"
        )


# ──────────────────────────────────────────────────────────────────────────────
# PopulationMapper
# ──────────────────────────────────────────────────────────────────────────────

class PopulationMapper:
    """
    Distributes 2023 Census populations to H3 tessellated cells.

    Parameters
    ----------
    denominator : The canonical total population (default: 807 029).
                  Must equal TOTAL_POPULATION — validated at construction.
    weighting   : Strategy for distributing population within a unit's cells.
                  "uniform"  — equal share per cell (default)
                  "density"  — weight by cell area (requires area metadata)
    """

    STRATEGIES = ("uniform", "density")

    def __init__(
        self,
        denominator: int = TOTAL_POPULATION,
        weighting: str = "uniform",
    ) -> None:
        if denominator != TOTAL_POPULATION:
            raise ValueError(
                f"denominator {denominator} ≠ canonical total {TOTAL_POPULATION}. "
                "The denominator must equal the 2023 Census sum of all 14 units."
            )
        if weighting not in self.STRATEGIES:
            raise ValueError(
                f"Unknown weighting strategy '{weighting}'. "
                f"Choices: {self.STRATEGIES}."
            )
        self.denominator = denominator
        self.weighting   = weighting
        log.info(
            "[PopulationMapper] Initialised: denominator=%d, strategy='%s'.",
            denominator, weighting,
        )

    # ── Main allocation method ────────────────────────────────────────────────

    def allocate(
        self,
        cells: List[TessellatedCell],
        admin_gdf: gpd.GeoDataFrame | None = None,
    ) -> AllocationResult:
        """
        Assign local_demand_coeff to every TessellatedCell in-place.

        Parameters
        ----------
        cells     : Flat list from H3TessellationEngine.build_full_grid().
        admin_gdf : Required when weighting=='density' to provide area_km2.
                    For 'uniform' weighting it is ignored.

        Returns
        -------
        AllocationResult with per-unit audit data.
        """
        # Group cells by administrative unit
        unit_cells: Dict[str, List[TessellatedCell]] = {name: [] for name in UNIT_NAMES}
        orphans: List[TessellatedCell] = []

        for cell in cells:
            if cell.admin_unit in unit_cells:
                unit_cells[cell.admin_unit].append(cell)
            else:
                orphans.append(cell)
                log.warning(
                    "[PopulationMapper] Cell %s has unknown unit '%s' — skipped.",
                    cell.h3_index, cell.admin_unit,
                )

        if orphans:
            log.warning(
                "[PopulationMapper] %d orphan cell(s) excluded from allocation.",
                len(orphans),
            )

        result = AllocationResult()
        weight_accumulator: float = 0.0

        for unit_name in UNIT_NAMES:
            unit_pop   = CENSUS_2023[unit_name]
            unit_group = unit_cells[unit_name]
            n          = len(unit_group)

            if n == 0:
                log.warning(
                    "[PopulationMapper] Unit '%s' has 0 cells — population "
                    "%d will NOT be allocated.",
                    unit_name, unit_pop,
                )
                result.add_unit(unit_name, unit_pop, 0, 0)
                continue

            # Build per-cell weights for the intra-unit distribution
            cell_weights = self._compute_cell_weights(unit_group, admin_gdf)

            # Integer allocation preserving unit total exactly
            int_pops = _largest_remainder(unit_pop, cell_weights)

            # Write demand coefficients back to cells
            for cell, int_pop in zip(unit_group, int_pops):
                coeff = int_pop / self.denominator
                cell.local_demand_coeff = coeff
                weight_accumulator += coeff

            allocated_sum = sum(int_pops)
            result.add_unit(unit_name, unit_pop, n, allocated_sum)

        result.finalize(weight_accumulator)
        result.validate()   # raises on invariant violation
        return result

    # ── Weighting strategy ────────────────────────────────────────────────────

    def _compute_cell_weights(
        self,
        cells: List[TessellatedCell],
        admin_gdf: gpd.GeoDataFrame | None,
    ) -> List[float]:
        """Return a weight per cell for the chosen intra-unit strategy."""
        if self.weighting == "uniform":
            return [1.0] * len(cells)

        if self.weighting == "density":
            return self._area_weights(cells, admin_gdf)

        raise RuntimeError(f"Unhandled strategy: {self.weighting}")

    @staticmethod
    def _area_weights(
        cells: List[TessellatedCell],
        admin_gdf: gpd.GeoDataFrame | None,
    ) -> List[float]:
        """
        Return weights proportional to the cell's polygon area.
        H3 cells at the same resolution have nearly identical area
        (~0.73 km² variation per resolution level), so this only matters
        when mixing resolutions — which SpatialValidator forbids.
        Falls back to uniform if Shapely area computation fails.
        """
        try:
            areas = [cell.shapely_polygon.area for cell in cells]
            total = sum(areas)
            if total == 0.0:
                return [1.0] * len(cells)
            return [a / total * len(cells) for a in areas]  # normalised
        except Exception as exc:
            log.warning(
                "[PopulationMapper] Area weight computation failed (%s) — "
                "falling back to uniform.",
                exc,
            )
            return [1.0] * len(cells)

    # ── Convenience factory ───────────────────────────────────────────────────

    @classmethod
    def run(
        cls,
        cells: List[TessellatedCell],
        admin_gdf: gpd.GeoDataFrame | None = None,
        weighting: str = "uniform",
    ) -> AllocationResult:
        """
        One-call convenience: construct mapper and run allocation.

        >>> result = PopulationMapper.run(cells)
        """
        mapper = cls(denominator=TOTAL_POPULATION, weighting=weighting)
        return mapper.allocate(cells, admin_gdf)

    # ── Legacy compatibility ──────────────────────────────────────────────────

    def distribute_population_to_grid(
        self,
        census_data: List[Dict],
        cells: List,
    ) -> List[Dict]:
        """
        Backward-compatible shim used by the existing main.py / API routes.

        Accepts the old list-of-dict census format and a list of schema.HexCell
        objects (not TessellatedCell).  Populates local_demand_coefficient on
        each HexCell and returns a list of dicts for JSON serialisation.

        This shim uses uniform allocation per named unit.
        """
        # Build census dict from old format
        census = {entry["name"]: entry["population"] for entry in census_data}
        total  = sum(census.values())

        if abs(total - TOTAL_POPULATION) > 0:
            raise ValueError(
                f"Census sum {total} ≠ {TOTAL_POPULATION}. "
                "Verify census_data entries."
            )

        # Group old HexCell objects by unit name
        unit_groups: Dict[str, List] = {}
        for cell in cells:
            unit_name = cell.assigned_unit
            unit_groups.setdefault(unit_name, []).append(cell)

        # Distribute using LR and write local_demand_coefficient in-place
        for unit_name, unit_pop in census.items():
            group = unit_groups.get(unit_name, [])
            if not group:
                continue
            n = len(group)
            int_pops = _largest_remainder(unit_pop, [1.0] * n)
            for cell, int_pop in zip(group, int_pops):
                cell.local_demand_coefficient = int_pop / total

        return [
            {
                "h3_index":                  c.h3_index,
                "centroid_lat":              c.centroid_lat,
                "centroid_lon":              c.centroid_lon,
                "assigned_unit":             c.assigned_unit,
                "local_demand_coefficient":  c.local_demand_coefficient,
            }
            for c in cells
        ]