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

router = APIRouter(prefix="/optimize", tags=["Operations Research Solvers"])

class OptimizeRequest(BaseModel):
    depot_count: int = Field(default=3, ge=1, le=10)
    total_fleet_pool: int = Field(default=65, ge=10, le=200)
    algorithm: str = Field(default="kmeans", description="kmeans, p_median, or p_center")

class OptimizeResponse(BaseModel):
    status_msg: str
    runtime_status: str
    generated_depot_count: int
    coordinates: List[Dict[str, Any]]

@router.post("", response_model=OptimizeResponse)
async def run_facility_location_pipeline(payload: OptimizeRequest):
    """Runs the chosen facility location optimization algorithm to place base depots."""
    mapper = PopulationMapper(target_denominator=807029)
    raw_cells = generate_synthetic_h3_grid_seed()
    mapper.distribute_population_to_grid(OFFICIAL_CENSUS_DATA, raw_cells)
    
    optimizer = DepotLocationOptimizer(target_hubs=payload.depot_count)
    
    if payload.algorithm == "p_median":
        centroid_coords = optimizer.execute_p_median(raw_cells)
        msg = "Exact p-Median MILP selection complete."
    elif payload.algorithm == "p_center":
        centroid_coords = optimizer.execute_p_center(raw_cells)
        msg = "Exact p-Center MILP selection complete."
    else:
        centroid_coords = optimizer.execute_weighted_kmeans(raw_cells)
        msg = "Weighted K-Means infrastructure selection complete."
        
    coords_list = []
    for idx, (lat, lon) in enumerate(centroid_coords):
        coords_list.append({
            "depot_id": f"DEPOT_{idx:02d}",
            "lat": lat,
            "lon": lon
        })
        
    return OptimizeResponse(
        status_msg=msg,
        runtime_status="SUCCESS",
        generated_depot_count=len(coords_list),
        coordinates=coords_list
    )

@router.post("/compare")
async def compare_facility_location(payload: OptimizeRequest):
    """Runs all facility location algorithms and returns comparative cost metrics."""
    mapper = PopulationMapper(target_denominator=807029)
    raw_cells = generate_synthetic_h3_grid_seed()
    mapper.distribute_population_to_grid(OFFICIAL_CENSUS_DATA, raw_cells)
    
    harness = FacilityLocationComparativeHarness(raw_cells, payload.depot_count)
    
    # 1. Weighted K-Means
    kmeans_centroids = harness.run_weighted_kmeans()
    kmeans_indices = []
    for cx, cy in kmeans_centroids:
        node_dists = [math.hypot(c.centroid_lat - cx, c.centroid_lon - cy) for c in raw_cells]
        kmeans_indices.append(int(np.argmin(node_dists)))
        
    # 2. p-Median MILP
    p_median_indices = harness.run_p_median()
    
    # 3. p-Center MILP
    p_center_indices = harness.run_p_center()
    
    # 4. Greedy Set Cover (using radius of 6km)
    set_cover_indices = harness.run_greedy_set_cover(radius_km=6.0)
    
    return {
        "kmeans": {
            "p_median_cost": harness.evaluate_p_median_cost(kmeans_indices),
            "p_center_cost": harness.evaluate_p_center_cost(kmeans_indices),
            "depot_indices": kmeans_indices
        },
        "p_median": {
            "p_median_cost": harness.evaluate_p_median_cost(p_median_indices),
            "p_center_cost": harness.evaluate_p_center_cost(p_median_indices),
            "depot_indices": p_median_indices
        },
        "p_center": {
            "p_median_cost": harness.evaluate_p_median_cost(p_center_indices),
            "p_center_cost": harness.evaluate_p_center_cost(p_center_indices),
            "depot_indices": p_center_indices
        },
        "set_cover_greedy": {
            "p_median_cost": harness.evaluate_p_median_cost(set_cover_indices),
            "p_center_cost": harness.evaluate_p_center_cost(set_cover_indices),
            "depot_indices": set_cover_indices
        }
    }
