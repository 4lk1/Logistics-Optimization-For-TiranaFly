import networkx as nx
import numpy as np
from typing import Dict, Any, List

class NetworkMetrics:
    """
    Analyzes the topological and operational properties of the drone network.
    Provides insights into coverage, vulnerability, and efficiency.
    """

    @staticmethod
    def calculate_centrality(graph: nx.DiGraph) -> Dict[str, Dict[str, float]]:
        """
        Computes various centrality measures to identify critical network hubs.
        - Degree Centrality: Nodes with most connections.
        - Betweenness Centrality: Nodes that act as bridges.
        - Closeness Centrality: Nodes with best overall reach.
        """
        return {
            "degree": nx.degree_centrality(graph),
            "betweenness": nx.betweenness_centrality(graph, weight='weight'),
            "closeness": nx.closeness_centrality(graph, distance='weight')
        }

    @staticmethod
    def analyze_connectivity(graph: nx.DiGraph) -> Dict[str, Any]:
        """
        Evaluates network robustness and fragmentation.
        """
        # For directed graphs, we check strongly and weakly connected components
        scc = list(nx.strongly_connected_components(graph))
        wcc = list(nx.weakly_connected_components(graph))
        
        return {
            "num_nodes": graph.number_of_nodes(),
            "num_edges": graph.number_of_edges(),
            "density": nx.density(graph),
            "strongly_connected_components": len(scc),
            "weakly_connected_components": len(wcc),
            "largest_scc_size": len(max(scc, key=len)) if scc else 0
        }

    @staticmethod
    def calculate_coverage_metrics(graph: nx.DiGraph) -> Dict[str, float]:
        """
        Assesses how well the network serves the population.
        """
        total_pop = 0
        reachable_pop = 0
        
        # Identify nodes reachable from at least one depot
        depots = [n for n, d in graph.nodes(data=True) if "depot" in str(n)]
        reachable_nodes = set()
        for depot in depots:
            reachable_nodes.update(nx.descendants(graph, depot))
            reachable_nodes.add(depot)
            
        for node, data in graph.nodes(data=True):
            node_obj = data.get('data')
            if hasattr(node_obj, 'population'):
                pop = node_obj.population
                total_pop += pop
                if node in reachable_nodes:
                    reachable_pop += pop
                    
        return {
            "total_population": float(total_pop),
            "reachable_population": float(reachable_pop),
            "coverage_ratio": reachable_pop / total_pop if total_pop > 0 else 0.0
        }

    @staticmethod
    def demand_accessibility_index(graph: nx.DiGraph) -> Dict[str, float]:
        """
        Calculates an accessibility index for each H3 node based on proximity to depots.
        High index means easier/faster service.
        """
        accessibility = {}
        depots = [n for n, d in graph.nodes(data=True) if "depot" in str(n)]
        
        for node, data in graph.nodes(data=True):
            if "h3" in str(node):
                # Min cost from any depot
                min_cost = float('inf')
                for depot in depots:
                    try:
                        cost = nx.dijkstra_path_length(graph, depot, node, weight='weight')
                        if cost < min_cost:
                            min_cost = cost
                    except nx.NetworkXNoPath:
                        continue
                
                # Accessibility is inverse of cost
                accessibility[node] = 1.0 / (min_cost + 1.0) if min_cost != float('inf') else 0.0
                
        return accessibility
