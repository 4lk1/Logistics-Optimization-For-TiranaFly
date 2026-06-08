# filename: api/routes/coverage.py
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Dict, Any
from main import OFFICIAL_CENSUS_DATA, generate_synthetic_h3_grid_seed
from schemas.io_models import Depot
from optimization.depot_selector import DepotLocationOptimizer
from gis.population_mapper import PopulationMapper
from gis.coordinate_utils import haversine_distance

router = APIRouter(tags=["Network Coverage Analysis"])

class CoverageRequest(BaseModel):
    depot_count: int = Field(default=3, ge=1, le=10)
    max_range_km: float = Field(default=24.0, ge=5.0, le=50.0)

@router.post("")
async def evaluate_coverage(payload: CoverageRequest) -> Dict[str, Any]:
    """Calculates percentage layout coverage rates of households within range of optimized depot hubs."""
    mapper = PopulationMapper(target_denominator=807029)
    raw_cells = generate_synthetic_h3_grid_seed()
    cell_matrix = mapper.distribute_population_to_grid(OFFICIAL_CENSUS_DATA, raw_cells)
    
    optimizer = DepotLocationOptimizer(target_hubs=payload.depot_count)
    centroid_coords = optimizer.execute_weighted_kmeans(raw_cells)
    
    covered_cells_count = 0
    total_cells_count = len(raw_cells)
    covered_demand_weight = 0.0
    
    for cell in raw_cells:
        is_covered = False
        for (lat, lon) in centroid_coords:
            dist = haversine_distance(cell.centroid_lat, cell.centroid_lon, lat, lon)
            if dist <= payload.max_range_km:
                is_covered = True
                break
        if is_covered:
            covered_cells_count += 1
            covered_demand_weight += cell.local_demand_coefficient
            
    return {
        "total_cells": total_cells_count,
        "covered_cells": covered_cells_count,
        "cell_coverage_rate_pct": (covered_cells_count / total_cells_count) * 100.0,
        "covered_demand_weight_pct": covered_demand_weight * 100.0,
        "unserved_demand_weight_pct": (1.0 - covered_demand_weight) * 100.0
    }
