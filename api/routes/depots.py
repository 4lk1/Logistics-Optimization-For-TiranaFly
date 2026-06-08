# filename: api/routes/depots.py
from fastapi import APIRouter
from typing import List, Dict, Any
from main import OFFICIAL_CENSUS_DATA, generate_synthetic_h3_grid_seed
from schemas.io_models import Depot
from optimization.depot_selector import DepotLocationOptimizer
from fleet.fleet_allocator import FleetAllocationEngine
from gis.population_mapper import PopulationMapper

router = APIRouter(tags=["Core Infrastructure Query Layer"])

@router.get("")
async def get_active_depot_configurations(target_hubs: int = 3, fleet_pool: int = 65) -> List[Dict[str, Any]]:
    """Calculates active depot configurations and allocated fleet sizes using weighted k-means."""
    mapper = PopulationMapper(target_denominator=807029)
    raw_cells = generate_synthetic_h3_grid_seed()
    mapper.distribute_population_to_grid(OFFICIAL_CENSUS_DATA, raw_cells)
    
    optimizer = DepotLocationOptimizer(target_hubs=target_hubs)
    centroid_coords = optimizer.execute_weighted_kmeans(raw_cells)
    
    depots = []
    for idx, (lat, lon) in enumerate(centroid_coords):
        depots.append(Depot(
            depot_id=f"DEPOT_{idx:02d}", lat=lat, lon=lon,
            h3_index=f"881e263ad00000{idx}", max_drone_capacity=30
        ))
        
    depots = FleetAllocationEngine.balance_fleet_distribution(depots, raw_cells, base_fleet_pool=fleet_pool)
    
    return [
        {
            "depot_id": d.depot_id,
            "lat": d.lat,
            "lon": d.lon,
            "h3_index": d.h3_index,
            "max_drone_capacity": d.max_drone_capacity,
            "fleet_allocated": d.assigned_fleet_size
        } for d in depots
    ]
