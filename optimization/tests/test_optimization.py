import unittest
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
from optimization.weighted_kmeans import WeightedKMeansOptimizer
from optimization.pmedian import PMedianOptimizer
from optimization.set_cover import SetCoverOptimizer
from optimization.depot_selector import DepotSelector
from optimization.models import OptimizationConfig

class TestOptimizationEngine(unittest.TestCase):

    def setUp(self):
        # Create small test dataset
        self.h3_coords = np.array([
            [41.3275, 19.8189],
            [41.3300, 19.8200],
            [41.3250, 19.8150]
        ])
        self.h3_pop = np.array([1000, 2000, 1500])
        self.h3_ids = ["h1", "h2", "h3"]
        
        self.cand_coords = np.array([
            [41.3280, 19.8190],
            [41.3310, 19.8210]
        ])
        
        self.h3_gdf = gpd.GeoDataFrame({
            'h3_id': self.h3_ids,
            'population': self.h3_pop
        }, geometry=[Point(c[1], c[0]) for c in self.h3_coords], crs="EPSG:4326")
        
        self.cand_gdf = gpd.GeoDataFrame({
            'id': ['c1', 'c2'],
            'capacity': [5000, 5000]
        }, geometry=[Point(c[1], c[0]) for c in self.cand_coords], crs="EPSG:4326")

    def test_weighted_kmeans(self):
        optimizer = WeightedKMeansOptimizer(n_clusters=2)
        optimizer.optimize(self.h3_coords, self.h3_pop)
        result = optimizer.get_results(self.h3_ids, self.h3_coords, self.h3_pop)
        self.assertEqual(len(result.depots), 2)
        self.assertGreater(result.total_population_served, 0)

    def test_pmedian(self):
        optimizer = PMedianOptimizer(p=2)
        result = optimizer.optimize(self.h3_coords, self.cand_coords, self.h3_pop)
        self.assertEqual(len(result.depots), 2)
        self.assertLess(result.avg_distance, 1000)

    def test_depot_selector(self):
        config = OptimizationConfig(max_depots=1, total_population=4500)
        selector = DepotSelector(config)
        best = selector.select_best_strategy(self.h3_gdf, self.cand_gdf)
        self.assertIsNotNone(best)
        self.assertIn(best.method_name, ["Weighted K-Means", "P-Median", "Set Cover"])

if __name__ == '__main__':
    unittest.main()
