import networkx as nx
import h3
import geopandas as gpd
from typing import List, Dict, Optional, Tuple, Union
from .models import (
    H3Node, DepotNode, NeighborEdge, DepotConnection, 
    GraphWeightConfig, BaseGraphNode, BaseEdge
)
from shapely.geometry import Point
from schemas.io_models import Depot, HexCell

class GraphBuilder:
    """
    Constructs the NetworkX graph from H3 tessellated population data.
    Models the hexagonal connectivity and integrates depot locations.
    """

    def __init__(self, weight_config: Optional[GraphWeightConfig] = None):
        self.weight_config = weight_config or GraphWeightConfig()
        self.graph = nx.DiGraph()
        self.nodes: Dict[str, BaseGraphNode] = {}

    def build_from_h3_gdf(self, h3_gdf: gpd.GeoDataFrame, k_ring: int = 1) -> nx.DiGraph:
        """
        Creates nodes from H3 cells and adds edges based on hexagonal adjacency.
        """
        # 1. Add H3 Nodes
        for _, row in h3_gdf.iterrows():
            h3_idx = row['h3_id']
            lat, lng = h3.cell_to_latlng(h3_idx)
            node = H3Node(
                id=h3_idx,
                h3_index=h3_idx,
                lat=lat,
                lng=lng,
                population=row.get('population', 0)
            )
            self._add_node(node)

        # 2. Add Adjacency Edges (k-ring)
        h3_indices = set(h3_gdf['h3_id'])
        for h3_idx in h3_indices:
            neighbors = h3.grid_disk(h3_idx, k_ring)
            for neighbor in neighbors:
                if neighbor in h3_indices and neighbor != h3_idx:
                    self._add_h3_edge(h3_idx, neighbor)
        
        return self.graph

    def add_depots(self, depots_gdf: gpd.GeoDataFrame, connection_radius_m: float = 1000.0):
        """
        Integrates depot locations into the graph and connects them to nearby H3 nodes.
        """
        for _, row in depots_gdf.iterrows():
            depot_id = row.get('id', f"depot_{_}")
            geom = row.geometry
            node = DepotNode(
                id=str(depot_id),
                lat=geom.y,
                lng=geom.x,
                capacity=row.get('capacity', 10),
                recharge_rate=row.get('recharge_rate', 1.0)
            )
            self._add_node(node)
            
            # Connect to H3 cells within radius
            # This is a simplified spatial join
            for h3_id, h3_node in self.nodes.items():
                if isinstance(h3_node, H3Node):
                    dist = self._haversine(node.lat, node.lng, h3_node.lat, h3_node.lng)
                    if dist <= connection_radius_m:
                        self._add_depot_edge(node.id, h3_id, dist)

    def _add_node(self, node: BaseGraphNode):
        self.nodes[node.id] = node
        self.graph.add_node(node.id, data=node)

    def _add_h3_edge(self, u: str, v: str):
        u_node = self.nodes[u]
        v_node = self.nodes[v]
        dist = self._haversine(u_node.lat, u_node.lng, v_node.lat, v_node.lng)
        
        edge = NeighborEdge(
            origin=u,
            destination=v,
            distance=dist,
            flight_time=dist / 15.0,  # 15 m/s average drone speed
            energy_cost=dist * 0.0001, # 0.1 Wh per meter approx
            risk_score=0.01,
            weather_penalty=1.0
        )
        
        weight = self.weight_config.calculate_weight(edge)
        self.graph.add_edge(u, v, weight=weight, data=edge)

    def _add_depot_edge(self, depot_id: str, h3_id: str, dist: float):
        edge = DepotConnection(
            origin=depot_id,
            destination=h3_id,
            distance=dist,
            flight_time=dist / 15.0,
            energy_cost=dist * 0.0001,
            risk_score=0.005,
            weather_penalty=1.0
        )
        
        weight = self.weight_config.calculate_weight(edge)
        # Bidirectional for depots
        self.graph.add_edge(depot_id, h3_id, weight=weight, data=edge)
        
        return_edge = DepotConnection(
            origin=h3_id,
            destination=depot_id,
            distance=dist,
            flight_time=dist / 15.0,
            energy_cost=dist * 0.0001,
            risk_score=0.005,
            weather_penalty=1.0
        )
        self.graph.add_edge(h3_id, depot_id, weight=self.weight_config.calculate_weight(return_edge), data=return_edge)

    @staticmethod
    def _haversine(lat1, lon1, lat2, lon2) -> float:
        """Calculates distance in meters between two points."""
        from math import radians, cos, sin, asin, sqrt
        R = 6371000  # Earth radius in meters
        dLat = radians(lat2 - lat1)
        dLon = radians(lon2 - lon1)
        lat1 = radians(lat1)
        lat2 = radians(lat2)

        a = sin(dLat / 2)**2 + cos(lat1) * cos(lat2) * sin(dLon / 2)**2
        c = 2 * asin(sqrt(a))
        return R * c

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
