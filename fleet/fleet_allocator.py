import numpy as np
import math
from typing import Dict, List, Any
from .queue_models import QueueingModels
from .demand_forecaster import DemandForecaster
from schemas.io_models import Depot, HexCell

class FleetAllocator:
    """
    Determines optimal fleet size and distribution across depots.
    Integrates demand forecasting and queueing theory.
    """

    def __init__(self, service_rate_per_drone: float = 2.0): # orders per hour
        self.service_rate = service_rate_per_drone

    def calculate_required_fleet(self, arrival_rate: float, target_wait_time_s: float = 600.0) -> int:
        """
        Calculates the minimum number of drones needed to keep wait time below threshold.
        """
        target_w = target_wait_time_s / 3600.0 # to hours
        
        # Start with minimum c such that rho < 1
        c = int(np.ceil(arrival_rate / self.service_rate))
        if c == 0: c = 1
        
        while True:
            metrics = QueueingModels.mmc_model(arrival_rate, self.service_rate, c)
            if metrics["stable"] and metrics["W"] <= target_w:
                return c
            c += 1
            if c > 100: break # Safety break
            
        return c

    def allocate_to_depots(self, depot_demand: Dict[str, float], reserve_factor: float = 0.2) -> Dict[str, int]:
        """
        Distributes fleet across depots based on local demand.
        depot_demand: Dict mapping depot_id to peak hourly arrival rate.
        """
        allocation = {}
        for depot_id, rate in depot_demand.items():
            base_count = self.calculate_required_fleet(rate)
            # Add reserve for maintenance and battery swaps
            total_count = int(np.ceil(base_count * (1 + reserve_factor)))
            allocation[depot_id] = total_count
            
        return allocation

    def estimate_utilization(self, arrival_rate: float, fleet_size: int) -> float:
        """Predicts expected utilization (rho)."""
        return arrival_rate / (fleet_size * self.service_rate)

class FleetAllocationEngine:
    @staticmethod
    def balance_fleet_distribution(depots: List[Depot], cells: List[HexCell], base_fleet_pool: int = 65) -> List[Depot]:
        depot_demand_shares = {d.depot_id: 0.0 for d in depots}
        
        # Associate each cell's demand with its nearest depot hub
        for cell in cells:
            min_dist = float('inf')
            closest_depot_id = depots[0].depot_id
            
            for depot in depots:
                R = 6371.0
                dlat = math.radians(depot.lat - cell.centroid_lat)
                dlon = math.radians(depot.lon - cell.centroid_lon)
                a = math.sin(dlat/2)**2 + math.cos(math.radians(cell.centroid_lat)) * math.cos(math.radians(depot.lat)) * math.sin(dlon/2)**2
                dist = 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))
                
                if dist < min_dist:
                    min_dist = dist
                    closest_depot_id = depot.depot_id
                    
            depot_demand_shares[closest_depot_id] += cell.local_demand_coefficient
            
        # Allocate drones proportionally based on the total demand weight assigned to each depot
        for depot in depots:
            share = depot_demand_shares[depot.depot_id]
            depot.assigned_fleet_size = max(2, round(share * base_fleet_pool))
            
        return depots
