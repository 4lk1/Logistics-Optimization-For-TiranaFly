# filename: graph/graph_pruner.py
import networkx as nx
import math
from typing import List

class NetworkTopologyPruner:
    def __init__(self, max_range_km: float = 24.0, power_coeff_wh_km: float = 45.0):
        self.max_range_km = max_range_km
        self.power_coeff = power_coeff_wh_km

    def compute_haversine(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))

    def prune_and_weight_edges(self, graph: nx.DiGraph) -> nx.DiGraph:
        nodes = list(graph.nodes(data=True))
        
        for i, (u_id, u_data) in enumerate(nodes):
            for j, (v_id, v_data) in enumerate(nodes):
                if u_id == v_id:
                    continue
                
                dist = self.compute_haversine(u_data['lat'], u_data['lon'], v_data['lat'], v_data['lon'])
                
                # Rigid Operational Constraint Check Validation Loop
                if dist <= self.max_range_km:
                    energy_cost = dist * self.power_coeff
                    time_seconds = (dist * 1000.0) / 15.0  # Assumes 15 m/s uniform cruise speed velocity
                    
                    graph.add_edge(
                        u_id, 
                        v_id, 
                        distance_km=dist, 
                        weight=energy_cost,  # Primary cost weight parameter configured for Dijkstra pathing
                        duration_sec=time_seconds
                    )
        return graph