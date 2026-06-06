import numpy as np
import geopandas as gpd
from typing import List, Dict, Any, Optional
from .models import OptimizationResult, OptimizationConfig
from .weighted_kmeans import WeightedKMeansOptimizer
from .pmedian import PMedianOptimizer
from .pcenter import PCenterOptimizer
from .set_cover import SetCoverOptimizer
from .facility_location import FacilityLocationOptimizer
from .coverage_optimizer import CoverageOptimizer

class DepotSelector:
    """
    Orchestrates multiple optimization runs and selects the best deployment strategy.
    """

    def __init__(self, config: Optional[OptimizationConfig] = None):
        self.config = config or OptimizationConfig()
        self.coverage_opt = CoverageOptimizer(target_population=self.config.total_population)

    def select_best_strategy(self, h3_gdf: gpd.GeoDataFrame, candidate_gdf: gpd.GeoDataFrame) -> OptimizationResult:
        """
        Runs all models and compares them.
        """
        # Prepare data
        h3_coords = np.array([[g.y, g.x] for g in h3_gdf.geometry])
        h3_pop = h3_gdf['population'].values
        h3_ids = h3_gdf['h3_id'].tolist()
        
        cand_coords = np.array([[g.y, g.x] for g in candidate_gdf.geometry])
        cand_caps = candidate_gdf.get('capacity', np.full(len(cand_coords), 100000)).values
        
        results = []

        # 1. Weighted K-Means
        try:
            kmeans = WeightedKMeansOptimizer(n_clusters=self.config.max_depots)
            kmeans.optimize(h3_coords, h3_pop)
            results.append(kmeans.get_results(h3_ids, h3_coords, h3_pop))
        except Exception as e:
            print(f"K-Means failed: {e}")

        # 2. P-Median (Sampled if too many nodes for exact solve)
        try:
            pmed = PMedianOptimizer(p=self.config.max_depots)
            # For demonstration, we use all nodes. In production, we'd sample or use heuristics for N > 500.
            results.append(pmed.optimize(h3_coords, cand_coords, h3_pop))
        except Exception as e:
            print(f"P-Median failed: {e}")

        # 3. Set Cover
        try:
            sc = SetCoverOptimizer(r_max_m=self.config.service_radius_m)
            results.append(sc.optimize(h3_coords, cand_coords))
        except Exception as e:
            print(f"Set Cover failed: {e}")

        if not results:
            raise RuntimeError("All optimization models failed")

        # Evaluate and find best
        best_result = None
        best_score = -1.0

        for res in results:
            score = self.coverage_opt.evaluate_multi_objective(
                res, 
                alpha=self.config.alpha_coverage,
                beta=self.config.beta_cost,
                gamma=self.config.gamma_distance,
                delta=self.config.delta_equity
            )
            res.metrics['moo_score'] = score
            
            if score > best_score:
                best_score = score
                best_result = res

        return best_result
