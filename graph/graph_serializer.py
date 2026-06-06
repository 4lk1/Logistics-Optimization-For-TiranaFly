import networkx as nx
import json
import pickle
import os
from typing import Any, Dict
from dataclasses import asdict
from .models import BaseGraphNode, BaseEdge

class GraphSerializer:
    """
    Handles graph persistence and export to standard spatial and graph formats.
    """

    @staticmethod
    def to_json(graph: nx.DiGraph, file_path: str):
        """Exports the graph to a custom JSON format preserving dataclass attributes."""
        data = nx.node_link_data(graph)
        # Convert dataclasses to dicts for JSON serialization
        for node in data['nodes']:
            if 'data' in node:
                node['data'] = asdict(node['data'])
        for edge in data['links']:
            if 'data' in edge:
                edge['data'] = asdict(edge['data'])
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def to_geojson(graph: nx.DiGraph, file_path: str):
        """Exports nodes and edges to GeoJSON for visualization."""
        features = []
        
        # Add Nodes as Points
        for n, data in graph.nodes(data=True):
            node_obj: BaseGraphNode = data['data']
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [node_obj.lng, node_obj.lat]},
                "properties": {**asdict(node_obj), "type": "node"}
            })
            
        # Add Edges as LineStrings
        for u, v, data in graph.edges(data=True):
            u_obj: BaseGraphNode = graph.nodes[u]['data']
            v_obj: BaseGraphNode = graph.nodes[v]['data']
            edge_obj: BaseEdge = data['data']
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "LineString", 
                    "coordinates": [[u_obj.lng, u_obj.lat], [v_obj.lng, v_obj.lat]]
                },
                "properties": {**asdict(edge_obj), "type": "edge", "weight": data['weight']}
            })
            
        geojson = {"type": "FeatureCollection", "features": features}
        with open(file_path, 'w') as f:
            json.dump(geojson, f)

    @staticmethod
    def to_graphml(graph: nx.DiGraph, file_path: str):
        """Exports to GraphML for use in tools like Gephi or Cytoscape."""
        # GraphML doesn't handle complex objects well, so we simplify
        temp_graph = graph.copy()
        for n in temp_graph.nodes:
            node_data = temp_graph.nodes[n]['data']
            for k, v in asdict(node_data).items():
                if k != 'metadata':
                    temp_graph.nodes[n][k] = v
            del temp_graph.nodes[n]['data']
            
        for u, v in temp_graph.edges:
            edge_data = temp_graph[u][v]['data']
            for k, v in asdict(edge_data).items():
                if k != 'metadata':
                    temp_graph[u][v][k] = v
            del temp_graph[u][v]['data']
            
        nx.write_graphml(temp_graph, file_path)

    @staticmethod
    def save_pickle(graph: nx.DiGraph, file_path: str):
        """Fast binary serialization using pickle."""
        with open(file_path, 'wb') as f:
            pickle.dump(graph, f)

    @staticmethod
    def load_pickle(file_path: str) -> nx.DiGraph:
        """Loads a graph from a pickle file."""
        with open(file_path, 'rb') as f:
            return pickle.load(f)
