import networkx as nx
from typing import List, Set, Callable
from .models import BaseEdge

class GraphPruner:
    """
    Filters the graph based on physical and operational constraints.
    Ensures that only viable routes remain for the optimization phase.
    """

    @staticmethod
    def prune_by_range(graph: nx.DiGraph, max_range_m: float) -> int:
        """Removes edges that exceed the drone's maximum flight range."""
        return GraphPruner._prune_edges(graph, lambda e: e.distance > max_range_m)

    @staticmethod
    def prune_by_battery(graph: nx.DiGraph, battery_capacity_kwh: float) -> int:
        """Removes edges that require more energy than the battery capacity."""
        return GraphPruner._prune_edges(graph, lambda e: e.energy_cost > battery_capacity_kwh)

    @staticmethod
    def prune_by_risk(graph: nx.DiGraph, max_risk_threshold: float) -> int:
        """Removes edges with a risk score above the threshold."""
        return GraphPruner._prune_edges(graph, lambda e: e.risk_score > max_risk_threshold)

    @staticmethod
    def prune_by_weather(graph: nx.DiGraph, max_weather_penalty: float) -> int:
        """Removes edges where weather conditions make the route unsafe."""
        return GraphPruner._prune_edges(graph, lambda e: e.weather_penalty > max_weather_penalty)

    @staticmethod
    def prune_isolated_nodes(graph: nx.DiGraph) -> int:
        """Removes nodes with no incoming or outgoing edges."""
        isolated = list(nx.isolates(graph))
        graph.remove_nodes_from(isolated)
        return len(isolated)

    @staticmethod
    def _prune_edges(graph: nx.DiGraph, criteria: Callable[[BaseEdge], bool]) -> int:
        """Internal helper to prune edges based on a boolean criteria."""
        edges_to_remove = []
        for u, v, data in graph.edges(data=True):
            edge_data: BaseEdge = data['data']
            if criteria(edge_data):
                edges_to_remove.append((u, v))
        
        graph.remove_edges_from(edges_to_remove)
        return len(edges_to_remove)
