import networkx as nx
from typing import List, Tuple, Optional, Dict, Any
import time

class ShortestPathEngine:
    """
    Unified API for shortest path calculations on the drone network graph.
    Supports multiple algorithms optimized for different use cases.
    """

    @staticmethod
    def dijkstra(graph: nx.DiGraph, source: str, target: str, weight: str = 'weight') -> Tuple[List[str], float]:
        """
        Classic Dijkstra's algorithm. 
        Complexity: O(E + V log V).
        Best for general single-source single-target paths.
        """
        path = nx.dijkstra_path(graph, source, target, weight=weight)
        cost = nx.dijkstra_path_length(graph, source, target, weight=weight)
        return path, cost

    @staticmethod
    def a_star(graph: nx.DiGraph, source: str, target: str, weight: str = 'weight') -> Tuple[List[str], float]:
        """
        A* search with Haversine heuristic.
        Complexity: O(E) in best case, O(V log V) in worst case.
        Faster than Dijkstra when a good heuristic is available.
        """
        def heuristic(u, v):
            u_data = graph.nodes[u]['data']
            v_data = graph.nodes[v]['data']
            # Haversine distance as heuristic
            from .graph_builder import GraphBuilder
            return GraphBuilder._haversine(u_data.lat, u_data.lng, v_data.lat, v_data.lng) / 15.0 # Min possible cost estimate

        path = nx.astar_path(graph, source, target, heuristic=heuristic, weight=weight)
        cost = nx.astar_path_length(graph, source, target, heuristic=heuristic, weight=weight)
        return path, cost

    @staticmethod
    def bidirectional_dijkstra(graph: nx.DiGraph, source: str, target: str, weight: str = 'weight') -> Tuple[List[str], float]:
        """
        Bidirectional Dijkstra's algorithm.
        Complexity: O(E + V log V), but typically visits fewer nodes than standard Dijkstra.
        """
        dist, path = nx.bidirectional_dijkstra(graph, source, target, weight=weight)
        return path, dist

    @staticmethod
    def yen_k_shortest_paths(graph: nx.DiGraph, source: str, target: str, k: int = 3, weight: str = 'weight') -> List[Tuple[List[str], float]]:
        """
        Yen's algorithm for finding K-shortest simple paths.
        Complexity: O(K V (E + V log V)).
        Used for identifying alternative routes in case of congestion or dynamic obstacles.
        """
        paths = list(nx.shortest_simple_paths(graph, source, target, weight=weight))
        results = []
        for i, path in enumerate(paths):
            if i >= k:
                break
            cost = sum(graph[path[j]][path[j+1]][weight] for j in range(len(path)-1))
            results.append((path, cost))
        return results

    @staticmethod
    def benchmark_algorithms(graph: nx.DiGraph, source: str, target: str) -> Dict[str, Any]:
        """Benchmarks the performance of different shortest path algorithms."""
        results = {}
        algorithms = {
            "Dijkstra": ShortestPathEngine.dijkstra,
            "A*": ShortestPathEngine.a_star,
            "Bidirectional Dijkstra": ShortestPathEngine.bidirectional_dijkstra
        }

        for name, func in algorithms.items():
            start_time = time.perf_counter()
            path, cost = func(graph, source, target)
            end_time = time.perf_counter()
            results[name] = {
                "time_ms": (end_time - start_time) * 1000,
                "cost": cost,
                "path_length": len(path)
            }
        
        return results
