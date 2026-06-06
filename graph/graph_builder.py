# filename: graph/graph_builder.py
import networkx as nx
from typing import List, Dict, Any, Tuple
from schemas.io_models import Depot, HexCell
from gis.coordinate_utils import haversine_distance  # Reused baseline spherical calculator

class FlightGraphBuilder:
    def __init__(self):
        self.G = nx.DiGraph()

    def construct_base_topology(self, depots: List[Depot], clients: List[HexCell]) -> nx.DiGraph:
        self.G.clear()
        
        for depot in depots:
            self.G.add_node(
                depot.depot_id, 
                type="DEPOT", 
                lat=depot.lat, 
                lon=depot.lon, 
                h3_index=depot.h3_index
            )
            
        for client in clients:
            self.G.add_node(
                client.h3_index, 
                type="CLIENT", 
                lat=client.centroid_lat, 
                lon=client.centroid_lon, 
                weight=client.local_demand_coefficient
            )
            
        return self.G