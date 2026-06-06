import geopandas as gpd
from typing import List, Dict, Any
from .depot_selector import DepotSelector
from .models import OptimizationConfig

class SensitivityAnalyzer:
    """
    Performs sensitivity analysis on key parameters like population growth and service radius.
    """

    def __init__(self, h3_gdf: gpd.GeoDataFrame, candidate_gdf: gpd.GeoDataFrame):
        self.h3_gdf = h3_gdf
        self.candidate_gdf = candidate_gdf

    def run_population_sensitivity(self, growth_rates: List[float] = [0.1, 0.2, 0.3]) -> Dict[float, Any]:
        """Analyzes impact of population growth on coverage."""
        results = {}
        for rate in growth_rates:
            temp_gdf = self.h3_gdf.copy()
            temp_gdf['population'] = (temp_gdf['population'] * (1 + rate)).astype(int)
            
            config = OptimizationConfig(total_population=temp_gdf['population'].sum())
            selector = DepotSelector(config)
            best_res = selector.select_best_strategy(temp_gdf, self.candidate_gdf)
            results[rate] = best_res
            
        return results

    def run_radius_sensitivity(self, radii: List[float] = [5000.0, 7500.0, 10000.0]) -> Dict[float, Any]:
        """Analyzes impact of drone service radius on infrastructure requirements."""
        results = {}
        for radius in radii:
            config = OptimizationConfig(service_radius_m=radius)
            selector = DepotSelector(config)
            best_res = selector.select_best_strategy(self.h3_gdf, self.candidate_gdf)
            results[radius] = best_res
            
        return results
