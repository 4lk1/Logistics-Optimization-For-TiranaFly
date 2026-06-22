import time
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from typing import List

from main import OFFICIAL_CENSUS_DATA, generate_synthetic_h3_grid_seed
from gis.population_mapper import PopulationMapper
from optimization.weighted_kmeans import WeightedKMeansOptimizer
from optimization.pmedian import PMedianOptimizer
from optimization.pcenter import PCenterOptimizer
from optimization.set_cover import SetCoverOptimizer
from optimization.coverage_optimizer import CoverageOptimizer

class TiranaFlyBenchmarker:
    def __init__(self, p_values: List[int] = [3, 5, 8]):
        self.p_values = p_values
        self.population_target = 807029
        self.mapper = PopulationMapper(target_denominator=self.population_target)
        self.coverage_eval = CoverageOptimizer(target_population=self.population_target)

    def run_benchmarks(self):
        print("Starting Optimization Benchmarks...")
        raw_cells = generate_synthetic_h3_grid_seed()
        self.mapper.distribute_population_to_grid(OFFICIAL_CENSUS_DATA, raw_cells)
        
        h3_coords = np.array([[c.centroid_lat, c.centroid_lon] for c in raw_cells])
        h3_pop = np.array([c.local_demand_coefficient * self.population_target for c in raw_cells])
        h3_ids = [c.h3_index for c in raw_cells]
        
        # Sample candidates (use demand points as candidates for simplicity)
        cand_coords = h3_coords
        
        results = []
        
        for p in self.p_values:
            print(f"Testing p = {p}")
            
            # 1. Weighted K-Means
            opt = WeightedKMeansOptimizer(n_clusters=p)
            opt.optimize(h3_coords, h3_pop)
            res = opt.get_results(h3_ids, h3_coords, h3_pop)
            results.append(self._record(res, "K-Means", p))

            # 2. P-Median
            opt = PMedianOptimizer(p=p)
            try:
                # Use a subset of candidates for performance if N is large
                res = opt.optimize(h3_coords, cand_coords[::5], h3_pop)
                results.append(self._record(res, "P-Median", p))
            except: pass

            # 3. P-Center
            opt = PCenterOptimizer(p=p)
            try:
                res = opt.optimize(h3_coords, cand_coords[::5])
                results.append(self._record(res, "P-Center", p))
            except: pass

        df = pd.DataFrame(results)
        df.to_csv("experiments/benchmarks/optimization_comparison.csv", index=False)
        print("Benchmarks complete. Results saved to experiments/benchmarks/optimization_comparison.csv")
        return df

    def _record(self, res, method, p):
        return {
            "method": method,
            "p": p,
            "pop_served": res.total_population_served,
            "avg_dist_m": res.avg_distance,
            "max_dist_m": res.max_distance,
            "runtime_sec": res.runtime_sec
        }

if __name__ == "__main__":
    benchmarker = TiranaFlyBenchmarker()
    benchmarker.run_benchmarks()
