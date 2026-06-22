# filename: api/routes/fleet.py
from fastapi import APIRouter
from typing import List, Dict, Any
from main import OFFICIAL_CENSUS_DATA, generate_synthetic_h3_grid_seed
from schemas.io_models import Depot
from optimization.depot_selector import DepotLocationOptimizer
from fleet.fleet_allocator import FleetAllocationEngine
from gis.population_mapper import PopulationMapper

router = APIRouter(tags=["Fleet Operations"])

@router.get("/status")
async def get_fleet_status() -> List[Dict[str, Any]]:
    """Returns mock status for the allocated fleet."""
    mapper = PopulationMapper(target_denominator=807029)
    raw_cells = generate_synthetic_h3_grid_seed()
    mapper.distribute_population_to_grid(OFFICIAL_CENSUS_DATA, raw_cells)
    
    optimizer = DepotLocationOptimizer(target_hubs=3)
    centroid_coords = optimizer.execute_weighted_kmeans(raw_cells)
    
    depots = []
    for idx, (lat, lon) in enumerate(centroid_coords):
        depots.append(Depot(
            depot_id=f"DEPOT_{idx:02d}", lat=lat, lon=lon,
            h3_index=f"881e263ad00000{idx}", max_drone_capacity=30
        ))
    depots = FleetAllocationEngine.balance_fleet_distribution(depots, raw_cells, base_fleet_pool=65)
    
    drones = []
    for d in depots:
        for i in range(d.assigned_fleet_size):
            drones.append({
                "id": f"DRONE-{d.depot_id}-{i:02d}",
                "model": "TiranaFly-V1",
                "status": "IDLE",
                "depot_id": d.depot_id,
                "battery": {
                    "id": f"BAT-{d.depot_id}-{i:02d}",
                    "soc": 100,
                    "soh": 100,
                    "cycle_count": 0
                }
            })
    return drones

@router.post("/initialize/{depot_id}")
async def initialize_fleet(depot_id: str, num_drones: int):
    """No-op initialization for POC."""
    return {"message": f"Initialized {num_drones} drones at {depot_id} (Mock)"}
