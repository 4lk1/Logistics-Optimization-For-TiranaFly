# filename: graph/shortest_path.py
import networkx as nx
from typing import List, Tuple, Dict, Any
import heapq
import math

class ShortestPathRoutingEngine:
    @staticmethod
    def execute_dijkstra(graph: nx.DiGraph, source: str, target: str) -> Tuple[List[str], float]:
        try:
            path = nx.dijkstra_path(graph, source, target, weight="weight")
            cost = nx.dijkstra_path_length(graph, source, target, weight="weight")
            return path, cost
        except nx.NetworkXNoPath:
            return [], float('inf')

    @staticmethod
    def execute_a_star(graph: nx.DiGraph, source: str, target: str) -> Tuple[List[str], float]:
        def heuristic(u, v):
            u_data = graph.nodes[u]
            v_data = graph.nodes[v]
            # Haversine distance used as admissible tracking heuristic multiplier baseline
            R = 6371.0
            dlat = math.radians(v_data['lat'] - u_data['lat'])
            dlon = math.radians(v_data['lon'] - u_data['lon'])
            a = math.sin(dlat/2)**2 + math.cos(math.radians(u_data['lat'])) * math.cos(math.radians(v_data['lat'])) * math.sin(dlon/2)**2
            return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a)) * 45.0 # Scaled to match energy cost metrics

        try:
            path = nx.astar_path(graph, source, target, heuristic=heuristic, weight="weight")
            cost = nx.astar_path_length(graph, source, target, heuristic=heuristic, weight="weight")
            return path, cost
        except nx.NetworkXNoPath:
            return [], float('inf')

    @staticmethod
    def execute_bidirectional_dijkstra(graph: nx.DiGraph, source: str, target: str) -> Tuple[List[str], float]:
        try:
            cost, path = nx.bidirectional_dijkstra(graph, source, target, weight="weight")
            return path, cost
        except nx.NetworkXNoPath:
            return [], float('inf')

    @staticmethod
    def execute_yen_k_shortest_paths(graph: nx.DiGraph, source: str, target: str, k: int = 3) -> List[Tuple[List[str], float]]:
        try:
            generator = nx.shortest_simple_paths(graph, source, target, weight="weight")
            paths = []
            for i, path in enumerate(generator):
                if i >= k:
                    break
                cost = sum(graph[path[j]][path[j+1]]["weight"] for j in range(len(path)-1))
                paths.append((path, cost))
            return paths
        except nx.NetworkXNoPath:
            return []