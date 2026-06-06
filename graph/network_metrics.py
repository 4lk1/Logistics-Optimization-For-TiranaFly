# filename: graph/network_metrics.py
import networkx as nx
from typing import Dict, Any

class NetworkTopologyAnalyzer:
    @staticmethod
    def compute_network_structural_metrics(graph: nx.DiGraph) -> Dict[str, Any]:
        return {
            "node_count": graph.number_of_nodes(),
            "edge_count": graph.number_of_edges(),
            "graph_density": nx.density(graph),
            "strongly_connected_components": nx.number_strongly_connected_components(graph),
            "average_clustering_coefficient": nx.average_clustering(graph.to_undirected())
        }