# filename: simulation/simulator.py
import random
from typing import List, Dict, Any
from schemas.io_models import Depot, HexCell
from graph.shortest_path import ShortestPathEngine
from gis.coordinate_utils import haversine_distance

class TiranaFlyStochasticSimulationEngine:
    def __init__(self, depots: List[Depot], cells: List[HexCell], graph_layer: Any):
        self.depots = depots
        self.cells = cells
        self.graph = graph_layer

    def _nearest_depot(self, cell: HexCell) -> Depot:
        return min(
            self.depots,
            key=lambda depot: haversine_distance(
                depot.lat,
                depot.lon,
                cell.centroid_lat,
                cell.centroid_lon,
            ),
        )

    def _path_coordinates(self, path: List[str]) -> List[List[float]]:
        coordinates = []
        for node_id in path:
            node = self.graph.nodes.get(node_id)
            if not node:
                continue
            coordinates.append([node["lon"], node["lat"]])
        return coordinates

    def execute_stochastic_run(
        self,
        iterations: int = 100,
        demand_spike_ratio: float = 1.0,
        replay_sample_size: int = 80,
    ) -> Dict[str, Any]:
        successful_deliveries = 0
        failed_deliveries = 0
        accumulated_wait_seconds = 0.0
        replay_orders = []
        weights = [max(cell.local_demand_coefficient, 0.000001) for cell in self.cells]
        
        for i in range(iterations):
            # Pick a target delivery node at random based on population density weights
            target_cell = random.choices(self.cells, weights=weights, k=1)[0]
            assigned_depot = self._nearest_depot(target_cell)
            drone_id = f"DRONE-{assigned_depot.depot_id}-{i % max(1, assigned_depot.assigned_fleet_size):02d}"
            order = {
                "id": f"ORD-{i + 1:04d}",
                "drone_id": drone_id,
                "depot_id": assigned_depot.depot_id,
                "target_h3": target_cell.h3_index,
                "destination": {
                    "lat": target_cell.centroid_lat,
                    "lng": target_cell.centroid_lon,
                },
                "status": "FAILED",
                "path": [],
                "path_coordinates": [],
                "distance_km": 0.0,
                "duration_sec": 0.0,
            }
            
            # Check for range anomalies or path failures due to bad weather simulations
            if random.random() < 0.03:  
                # Simulates unexpected hardware failures or temporary route blocks
                failed_deliveries += 1
                if len(replay_orders) < replay_sample_size:
                    replay_orders.append(order)
                continue
                
            try:
                # Calculate paths using the short-path routing engine
                path, cost = ShortestPathEngine.dijkstra(
                    self.graph, assigned_depot.depot_id, target_cell.h3_index
                )
                if len(path) > 0 and cost < float('inf'):
                    successful_deliveries += 1
                    duration = cost * 1.5  # Scale operational durations
                    accumulated_wait_seconds += duration
                    order.update({
                        "status": "DELIVERED",
                        "path": path,
                        "path_coordinates": self._path_coordinates(path),
                        "distance_km": cost / 45.0,
                        "duration_sec": duration,
                    })
                else:
                    failed_deliveries += 1
            except Exception:
                failed_deliveries += 1

            if len(replay_orders) < replay_sample_size:
                replay_orders.append(order)
                
        return {
            "total_orders_processed": iterations,
            "successful_deliveries": successful_deliveries,
            "failed_deliveries": failed_deliveries,
            "system_delivery_success_rate": float(successful_deliveries / iterations) * 100.0,
            "average_delivery_wait_time_sec": float(accumulated_wait_seconds / max(1, successful_deliveries)),
            "orders": replay_orders,
        }