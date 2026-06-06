# filename: api/routes/simulate.py
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Dict, Any
from main import OFFICIAL_CENSUS_DATA, generate_synthetic_h3_grid_seed
from schemas.io_models import Depot
from optimization.depot_selector import DepotLocationOptimizer
from fleet.fleet_allocator import FleetAllocationEngine
from gis.population_mapper import PopulationMapper
from graph.graph_builder import FlightGraphBuilder
from graph.graph_pruner import NetworkTopologyPruner
from simulation.simulator import TiranaFlyStochasticSimulationEngine

router = APIRouter(prefix="/simulate", tags=["Stochastic Simulation Engine"])

class SimulationRequest(BaseModel):
    iterations: int = Field(default=250, ge=10, le=1000)
    depot_count: int = Field(default=3, ge=1, le=10)
    fleet_pool: int = Field(default=65, ge=10, le=200)

@router.post("")
async def run_simulation(payload: SimulationRequest) -> Dict[str, Any]:
    """Runs a stochastic simulation representing peak network load under standard conditions."""
    mapper = PopulationMapper(target_denominator=807029)
    raw_cells = generate_synthetic_h3_grid_seed()
    mapper.distribute_population_to_grid(OFFICIAL_CENSUS_DATA, raw_cells)
    
    optimizer = DepotLocationOptimizer(target_hubs=payload.depot_count)
    centroid_coords = optimizer.execute_weighted_kmeans(raw_cells)
    
    depots = []
    for idx, (lat, lon) in enumerate(centroid_coords):
        depots.append(Depot(
            depot_id=f"DEPOT_{idx:02d}", lat=lat, lon=lon,
            h3_index=f"881e263ad00000{idx}", max_drone_capacity=30
        ))
    depots = FleetAllocationEngine.balance_fleet_distribution(depots, raw_cells, base_fleet_pool=payload.fleet_pool)
    
    builder = FlightGraphBuilder()
    base_graph = builder.construct_base_topology(depots, raw_cells)
    
    pruner = NetworkTopologyPruner(max_range_km=24.0, power_coeff_wh_km=45.0)
    flight_network = pruner.prune_and_weight_edges(base_graph)
    
    simulator = TiranaFlyStochasticSimulationEngine(depots, raw_cells, flight_network)
    sim_kpis = simulator.execute_stochastic_run(iterations=payload.iterations)
    
    return sim_kpis
