# filename: api/routes/routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from main import OFFICIAL_CENSUS_DATA, generate_synthetic_h3_grid_seed
from schemas.io_models import Depot
from optimization.depot_selector import DepotLocationOptimizer
from fleet.fleet_allocator import FleetAllocationEngine
from gis.population_mapper import PopulationMapper
from graph.graph_builder import FlightGraphBuilder
from graph.graph_pruner import NetworkTopologyPruner
from graph.shortest_path import ShortestPathRoutingEngine

router = APIRouter(prefix="/route", tags=["Routing Optimization Engines"])

class RouteRequest(BaseModel):
    origin_node: str = Field(..., example="DEPOT_00")
    destination_h3: str = Field(..., example="881e263a000000c")
    algorithm: str = Field(default="dijkstra", description="dijkstra, a_star, bidirectional, or yen")

class RouteResponse(BaseModel):
    path_sequence: List[str]
    total_energy_wh: float
    distance_km: float
    feasible: bool

@router.post("", response_model=RouteResponse)
async def generate_optimal_flight_path(payload: RouteRequest):
    """Calculates the optimal flight path from a depot to a destination H3 cell."""
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
    
    builder = FlightGraphBuilder()
    base_graph = builder.construct_base_topology(depots, raw_cells)
    
    pruner = NetworkTopologyPruner(max_range_km=24.0, power_coeff_wh_km=45.0)
    flight_network = pruner.prune_and_weight_edges(base_graph)
    
    # Validate node existence
    if payload.origin_node not in flight_network.nodes:
        raise HTTPException(status_code=400, detail=f"Origin node '{payload.origin_node}' not found in flight network.")
    if payload.destination_h3 not in flight_network.nodes:
        # Check if they passed an index that exists in the cells list
        matching_nodes = [node for node in flight_network.nodes if node.lower() == payload.destination_h3.lower()]
        if matching_nodes:
            payload.destination_h3 = matching_nodes[0]
        else:
            client_nodes = [node for node, data in flight_network.nodes(data=True) if data.get('type') == 'CLIENT']
            raise HTTPException(
                status_code=404, 
                detail=f"Destination cell '{payload.destination_h3}' not found. Try one of: {client_nodes[:5]}"
            )
        
    # Execute the requested shortest-path algorithm
    if payload.algorithm == "a_star":
        path, cost = ShortestPathRoutingEngine.execute_a_star(flight_network, payload.origin_node, payload.destination_h3)
    elif payload.algorithm == "bidirectional":
        path, cost = ShortestPathRoutingEngine.execute_bidirectional_dijkstra(flight_network, payload.origin_node, payload.destination_h3)
    elif payload.algorithm == "yen":
        paths = ShortestPathRoutingEngine.execute_yen_k_shortest_paths(flight_network, payload.origin_node, payload.destination_h3, k=1)
        if paths:
            path, cost = paths[0]
        else:
            path, cost = [], float('inf')
    else:
        path, cost = ShortestPathRoutingEngine.execute_dijkstra(flight_network, payload.origin_node, payload.destination_h3)
        
    if not path or cost == float('inf'):
        return RouteResponse(
            path_sequence=[],
            total_energy_wh=0.0,
            distance_km=0.0,
            feasible=False
        )
        
    # Sum up path segments distance in km
    distance_km = 0.0
    for i in range(len(path) - 1):
        edge_data = flight_network[path[i]][path[i+1]]
        distance_km += edge_data.get("distance_km", 0.0)
        
    return RouteResponse(
        path_sequence=path,
        total_energy_wh=cost,
        distance_km=distance_km,
        feasible=True
    )
