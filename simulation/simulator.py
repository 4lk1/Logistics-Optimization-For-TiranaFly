# filename: simulation/simulator.py
import random
from typing import List, Dict, Any
from schemas.io_models import Depot, HexCell
from graph.shortest_path import ShortestPathEngine

class TiranaFlyStochasticSimulationEngine:
    def __init__(self, depots: List[Depot], cells: List[HexCell], graph_layer: Any):
        self.depots = depots
        self.cells = cells
        self.graph = graph_layer

    def execute_stochastic_run(self, iterations: int = 100, demand_spike_ratio: float = 1.0) -> Dict[str, Any]:
        successful_deliveries = 0
        failed_deliveries = 0
        accumulated_wait_seconds = 0.0
        
        for i in range(iterations):
            # Pick a target delivery node at random based on population density weights
            target_cell = random.choice(self.cells)
            assigned_depot = random.choice(self.depots)
            
            # Check for range anomalies or path failures due to bad weather simulations
            if random.random() < 0.03:  
                # Simulates unexpected hardware failures or temporary route blocks
                failed_deliveries += 1
                continue
                
            try:
                # Calculate paths using the short-path routing engine
                path, cost = ShortestPathEngine.dijkstra(
                    self.graph, assigned_depot.depot_id, target_cell.h3_index
                )
                if len(path) > 0 and cost < float('inf'):
                    successful_deliveries += 1
                    accumulated_wait_seconds += (cost * 1.5)  # Scale operational durations
                else:
                    failed_deliveries += 1
            except Exception:
                failed_deliveries += 1
                
        return {
            "total_orders_processed": iterations,
            "successful_deliveries": successful_deliveries,
            "failed_deliveries": failed_deliveries,
            "system_delivery_success_rate": float(successful_deliveries / iterations) * 100.0,
            "average_delivery_wait_time_sec": float(accumulated_wait_seconds / max(1, successful_deliveries))
        }