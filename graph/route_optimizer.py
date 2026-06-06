import networkx as nx
from typing import List, Tuple, Dict, Optional
from .shortest_path import ShortestPathEngine

class RouteOptimizer:
    """
    Implements VRP heuristics for drone fleet routing.
    Focuses on multi-stop deliveries and efficient depot returns.
    """

    @staticmethod
    def nearest_neighbor_route(graph: nx.DiGraph, start_node: str, delivery_points: List[str]) -> List[str]:
        """
        Builds a route by always visiting the nearest unvisited delivery point.
        Greedy heuristic for TSP-like problems.
        """
        route = [start_node]
        unvisited = set(delivery_points)
        current = start_node

        while unvisited:
            # Find nearest neighbor among unvisited
            best_next = None
            min_cost = float('inf')
            
            for candidate in unvisited:
                try:
                    # Using A* for distance check
                    _, cost = ShortestPathEngine.a_star(graph, current, candidate)
                    if cost < min_cost:
                        min_cost = cost
                        best_next = candidate
                except (nx.NetworkXNoPath, nx.NodeNotFound):
                    continue
            
            if best_next is None:
                # No path to any remaining unvisited nodes
                break
                
            route.append(best_next)
            unvisited.remove(best_next)
            current = best_next

        # Always return to depot if start_node was a depot
        if "depot" in start_node:
            try:
                _, cost = ShortestPathEngine.a_star(graph, current, start_node)
                route.append(start_node)
            except:
                pass
                
        return route

    @staticmethod
    def greedy_multi_stop(graph: nx.DiGraph, depot_id: str, demand_nodes: List[str], max_capacity: float) -> List[List[str]]:
        """
        Groups demand nodes into multiple routes based on drone capacity.
        Implements a simple sweep or greedy clustering approach.
        """
        routes = []
        unvisited = list(demand_nodes)
        
        while unvisited:
            current_route = [depot_id]
            current_load = 0.0
            current_pos = depot_id
            
            # Simple greedy fill for the current drone capacity
            to_remove = []
            for node in unvisited:
                node_data = graph.nodes[node]['data']
                demand = getattr(node_data, 'demand_volume', 1.0)
                
                if current_load + demand <= max_capacity:
                    try:
                        _, cost = ShortestPathEngine.a_star(graph, current_pos, node)
                        current_route.append(node)
                        current_load += demand
                        current_pos = node
                        to_remove.append(node)
                    except:
                        continue
            
            for node in to_remove:
                unvisited.remove(node)
                
            # Return to depot
            current_route.append(depot_id)
            routes.append(current_route)
            
            if not to_remove: # Avoid infinite loop if no node can be reached
                break
                
        return routes

    @staticmethod
    def calculate_route_metrics(graph: nx.DiGraph, route: List[str]) -> Dict[str, float]:
        """Calculates total distance, time, and energy for a given sequence of nodes."""
        total_dist = 0.0
        total_time = 0.0
        total_energy = 0.0
        
        for i in range(len(route) - 1):
            u, v = route[i], route[i+1]
            try:
                # We need the actual path to get edge data
                path, _ = ShortestPathEngine.dijkstra(graph, u, v)
                for j in range(len(path) - 1):
                    edge_data = graph[path[j]][path[j+1]]['data']
                    total_dist += edge_data.distance
                    total_time += edge_data.flight_time
                    total_energy += edge_data.energy_cost
            except:
                continue
                
        return {
            "total_distance_m": total_dist,
            "total_time_s": total_time,
            "total_energy_kwh": total_energy
        }
