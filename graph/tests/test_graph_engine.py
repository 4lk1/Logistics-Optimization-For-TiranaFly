import unittest
import networkx as nx
import geopandas as gpd
import h3
from shapely.geometry import Point
from graph.models import H3Node, DepotNode, GraphWeightConfig
from graph.graph_builder import GraphBuilder
from graph.graph_pruner import GraphPruner
from graph.shortest_path import ShortestPathEngine
from graph.route_optimizer import RouteOptimizer
from graph.network_metrics import NetworkMetrics

class TestGraphEngine(unittest.TestCase):

    def setUp(self):
        # Create a small mock H3 GDF for testing
        # Center of Tirana
        lat, lng = 41.3275, 19.8189
        self.h3_res = 9
        center_h3 = h3.geo_to_h3(lat, lng, self.h3_res)
        neighbors = h3.k_ring(center_h3, 2)
        
        self.h3_gdf = gpd.GeoDataFrame({
            'h3_id': list(neighbors),
            'population': [100] * len(neighbors)
        }, geometry=[Point(h3.h3_to_geo(h)[1], h3.h3_to_geo(h)[0]) for h in neighbors], crs="EPSG:4326")
        
        self.builder = GraphBuilder()
        self.graph = self.builder.build_from_h3_gdf(self.h3_gdf)
        
        # Add a mock depot
        depots_gdf = gpd.GeoDataFrame({
            'id': ['depot_1'],
            'capacity': [20],
            'recharge_rate': [2.0]
        }, geometry=[Point(lng, lat)], crs="EPSG:4326")
        self.builder.add_depots(depots_gdf)
        self.graph = self.builder.graph

    def test_graph_construction(self):
        self.assertGreater(self.graph.number_of_nodes(), 0)
        self.assertGreater(self.graph.number_of_edges(), 0)
        self.assertIn('depot_1', self.graph.nodes)

    def test_shortest_path(self):
        source = 'depot_1'
        target = list(self.h3_gdf['h3_id'])[5]
        path, cost = ShortestPathEngine.dijkstra(self.graph, source, target)
        self.assertIsInstance(path, list)
        self.assertGreater(cost, 0)
        
        path_a, cost_a = ShortestPathEngine.a_star(self.graph, source, target)
        self.assertEqual(path, path_a)

    def test_pruning(self):
        # Initial edge count
        initial_edges = self.graph.number_of_edges()
        
        # Prune with a very small range
        removed = GraphPruner.prune_by_range(self.graph, 1.0)
        self.assertGreater(removed, 0)
        self.assertLess(self.graph.number_of_edges(), initial_edges)

    def test_route_optimization(self):
        depot = 'depot_1'
        delivery_points = list(self.h3_gdf['h3_id'])[:3]
        route = RouteOptimizer.nearest_neighbor_route(self.graph, depot, delivery_points)
        self.assertEqual(route[0], depot)
        self.assertEqual(route[-1], depot)
        self.assertTrue(set(delivery_points).issubset(set(route)))

    def test_metrics(self):
        metrics = NetworkMetrics.analyze_connectivity(self.graph)
        self.assertEqual(metrics['num_nodes'], self.graph.number_of_nodes())
        
        coverage = NetworkMetrics.calculate_coverage_metrics(self.graph)
        self.assertGreaterEqual(coverage['coverage_ratio'], 0.0)

if __name__ == '__main__':
    unittest.main()
