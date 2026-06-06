# filename: optimization/depot_selector.py
import numpy as np
from typing import List, Tuple, Dict
from schemas.io_models import HexCell, Depot

class DepotLocationOptimizer:
    def __init__(self, target_hubs: int = 3):
        self.k = target_hubs

    def execute_weighted_kmeans(self, client_cells: List[HexCell]) -> List[Tuple[float, float]]:
        """
        Calculates optimized hub centers using custom geographically weighted K-Means (Haversine).
        """
        from optimization.weighted_kmeans import run_weighted_kmeans
        return run_weighted_kmeans(client_cells, self.k)

    def execute_p_median(self, client_cells: List[HexCell]) -> List[Tuple[float, float]]:
        """
        Calculates optimized hub centers solving the p-median MILP model.
        """
        from optimization.facility_location import FacilityLocationComparativeHarness
        harness = FacilityLocationComparativeHarness(client_cells, self.k)
        selected_indices = harness.run_p_median()
        return [(client_cells[idx].centroid_lat, client_cells[idx].centroid_lon) for idx in selected_indices]

    def execute_p_center(self, client_cells: List[HexCell]) -> List[Tuple[float, float]]:
        """
        Calculates optimized hub centers solving the p-center minimax MILP model.
        """
        from optimization.facility_location import FacilityLocationComparativeHarness
        harness = FacilityLocationComparativeHarness(client_cells, self.k)
        selected_indices = harness.run_p_center()
        return [(client_cells[idx].centroid_lat, client_cells[idx].centroid_lon) for idx in selected_indices]