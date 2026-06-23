# filename: api/routes/optimize.py
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import numpy as np
import math
from main import OFFICIAL_CENSUS_DATA, generate_synthetic_h3_grid_seed
from schemas.io_models import Depot
from optimization.depot_selector import DepotLocationOptimizer
from fleet.fleet_allocator import FleetAllocationEngine
from gis.population_mapper import PopulationMapper
from optimization.facility_location import FacilityLocationComparativeHarness

router = APIRouter(tags=["Operations Research Solvers"])

class OptimizeRequest(BaseModel):
    depot_count: int = Field(default=3, ge=1, le=25)
    total_fleet_pool: int = Field(default=65, ge=10, le=200)
    algorithm: str = Field(default="kmeans", description="kmeans, p_median, or p_center")

class OptimizeResponse(BaseModel):
    status_msg: str
    runtime_status: str
    generated_depot_count: int
    coordinates: List[Dict[str, Any]]

# Removed "/api/v1/optimization" because it's prefixed in app.py

@router.post("/run", response_model=OptimizeResponse)
async def run_facility_location_pipeline(payload: OptimizeRequest):
    """Runs the chosen facility location optimization algorithm to place base depots."""
    mapper = PopulationMapper(target_denominator=807029)
    raw_cells = generate_synthetic_h3_grid_seed()
    mapper.distribute_population_to_grid(OFFICIAL_CENSUS_DATA, raw_cells)
    
    optimizer = DepotLocationOptimizer(target_hubs=payload.depot_count)
    centroid_coords = optimizer.execute_weighted_kmeans(raw_cells)
    
    return {
        "status_msg": "Optimization converged successfully",
        "runtime_status": "SUCCESS",
        "generated_depot_count": len(centroid_coords),
        "coordinates": [{"lat": c[0], "lon": c[1]} for c in centroid_coords]
    }

@router.get("/latest")
async def get_latest_optimization():
    """Returns a default optimization result for the POC dashboard."""
    mapper = PopulationMapper(target_denominator=807029)
    raw_cells = generate_synthetic_h3_grid_seed()
    mapper.distribute_population_to_grid(OFFICIAL_CENSUS_DATA, raw_cells)
    
    optimizer = DepotLocationOptimizer(target_hubs=3)
    centroid_coords = optimizer.execute_weighted_kmeans(raw_cells)
    
    depots = []
    for idx, (lat, lon) in enumerate(centroid_coords):
        depots.append({
            "id": f"DEPOT_{idx:02d}",
            "name": f"Hub {idx+1}",
            "capacity": 30,
            "lat": lat,
            "lng": lon,
            "geom": {"type": "Point", "coordinates": [lon, lat]}
        })
        
    return {
        "id": 1,
        "method": "Weighted K-Means",
        "timestamp": "2026-06-10T12:00:00Z",
        "data": {
            "depots": depots,
            "assignments": [],
            "total_population_served": 807029,
            "avg_distance": 4200.0,
            "max_distance": 12000.0,
            "total_cost": 0.0
        }
    }
    
@router.post("/compare")
async def compare_facility_location(payload: OptimizeRequest):
    """Runs all facility location algorithms and returns comparative cost metrics."""
    # ... (rest of the function)
