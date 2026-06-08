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
    depot_count: int = Field(default=3, ge=1, le=10)
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
    # ... (rest of the function)
    # ...
    
@router.post("/compare")
async def compare_facility_location(payload: OptimizeRequest):
    """Runs all facility location algorithms and returns comparative cost metrics."""
    # ... (rest of the function)
