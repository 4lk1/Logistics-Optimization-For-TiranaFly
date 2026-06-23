# filename: api/routes/simulate.py
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Dict, Any
from main import H3_GRID_RESOLUTION, OFFICIAL_CENSUS_DATA, generate_synthetic_h3_grid_seed, lat_lon_to_h3
from schemas.io_models import Depot
from optimization.depot_selector import DepotLocationOptimizer
from fleet.fleet_allocator import FleetAllocationEngine
from gis.population_mapper import PopulationMapper
from gis.coordinate_utils import haversine_distance
from graph.graph_builder import FlightGraphBuilder
from simulation.simulator import TiranaFlyStochasticSimulationEngine

router = APIRouter(tags=["Stochastic Simulation Engine"])

class SimulationRequest(BaseModel):
    iterations: int = Field(default=250, ge=10, le=1000)
    depot_count: int = Field(default=3, ge=1, le=10)
    fleet_pool: int = Field(default=65, ge=10, le=200)
    replay_sample_size: int = Field(default=80, ge=1, le=200)

def build_depot_centered_flight_graph(depots, cells):
    """Builds a lightweight graph for replayable depot-to-order paths."""
    builder = FlightGraphBuilder()
    graph = builder.construct_base_topology(depots, cells)

    for depot in depots:
        for cell in cells:
            distance_km = haversine_distance(
                depot.lat,
                depot.lon,
                cell.centroid_lat,
                cell.centroid_lon,
            )
            graph.add_edge(depot.depot_id, cell.h3_index, distance=distance_km, weight=distance_km * 45.0)

    return graph

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
            h3_index=lat_lon_to_h3(lat, lon, H3_GRID_RESOLUTION), max_drone_capacity=30
        ))
    depots = FleetAllocationEngine.balance_fleet_distribution(depots, raw_cells, base_fleet_pool=payload.fleet_pool)
    
    flight_network = build_depot_centered_flight_graph(depots, raw_cells)
    
    simulator = TiranaFlyStochasticSimulationEngine(depots, raw_cells, flight_network)
    sim_kpis = simulator.execute_stochastic_run(
        iterations=payload.iterations,
        replay_sample_size=payload.replay_sample_size,
    )
    
    return sim_kpis
