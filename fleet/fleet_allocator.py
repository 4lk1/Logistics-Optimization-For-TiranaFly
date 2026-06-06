# filename: fleet/fleet_allocator.py
import math
from typing import List, Dict
from schemas.io_models import Depot, HexCell
from gis.coordinate_utils import haversine_distance

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