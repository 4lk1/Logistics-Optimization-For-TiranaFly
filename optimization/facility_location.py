# filename: optimization/facility_location.py
import numpy as np
from typing import List, Tuple, Dict, Any
from schemas.io_models import HexCell
from gis.coordinate_utils import haversine_distance
from optimization.weighted_kmeans import run_weighted_kmeans
from optimization.p_median import solve_p_median_milp
from optimization.p_center import solve_p_center_milp
from optimization.set_cover import solve_set_cover_milp

class FacilityLocationComparativeHarness:
    def __init__(self, candidate_cells: List[HexCell], p_facilities: int):
        self.cells = candidate_cells
        self.p = p_facilities
        self.num_nodes = len(candidate_cells)
        self._build_distance_matrix()

    def _build_distance_matrix(self):
        self.dist_matrix = np.zeros((self.num_nodes, self.num_nodes))
        self.weights = np.array([c.local_demand_coefficient for c in self.cells])
        
        for i in range(self.num_nodes):
            for j in range(self.num_nodes):
                self.dist_matrix[i, j] = haversine_distance(
                    self.cells[i].centroid_lat, self.cells[i].centroid_lon,
                    self.cells[j].centroid_lat, self.cells[j].centroid_lon
                )

    def evaluate_p_median_cost(self, selected_indices: List[int]) -> float:
        """Evaluates sum of demand-weighted travel distances."""
        if not selected_indices:
            return float('inf')
        sub_matrix = self.dist_matrix[:, selected_indices]
        min_distances = np.min(sub_matrix, axis=1)
        return float(np.sum(min_distances * self.weights))

    def evaluate_p_center_cost(self, selected_indices: List[int]) -> float:
        """Evaluates the minimax distance constraint to isolate edge service latency."""
        if not selected_indices:
            return float('inf')
        sub_matrix = self.dist_matrix[:, selected_indices]
        min_distances = np.min(sub_matrix, axis=1)
        return float(np.max(min_distances))

    def run_greedy_set_cover(self, radius_km: float = 6.0) -> List[int]:
        """Greedy heuristic approximation for the Set Covering Location Problem."""
        uncovered = set(range(self.num_nodes))
        selected_depots = []
        
        while len(uncovered) > 0 and len(selected_depots) < self.p:
            best_candidate = -1
            best_coverage = set()
            
            for j in range(self.num_nodes):
                covered_by_j = set([i for i in uncovered if self.dist_matrix[i, j] <= radius_km])
                if len(covered_by_j) > len(best_coverage):
                    best_coverage = covered_by_j
                    best_candidate = j
            
            if best_candidate == -1 or len(best_coverage) == 0:
                # Fallback to absolute maximum remaining weight node
                remaining_list = list(uncovered)
                best_candidate = remaining_list[np.argmax(self.weights[remaining_list])]
                best_coverage = {best_candidate}
                
            selected_depots.append(best_candidate)
            uncovered -= best_coverage
            
        return selected_depots

    # --- Integrated custom mathematical optimization solvers ---

    def run_weighted_kmeans(self) -> List[Tuple[float, float]]:
        """Runs custom geographically weighted K-Means using Haversine distance."""
        return run_weighted_kmeans(self.cells, self.p)

    def run_p_median(self) -> List[int]:
        """Solves the p-median problem exactly using MILP (HiGHS) with heuristic fallback."""
        return solve_p_median_milp(self.cells, self.p, self.dist_matrix)

    def run_p_center(self) -> List[int]:
        """Solves the p-center problem exactly using MILP (HiGHS) with heuristic fallback."""
        return solve_p_center_milp(self.cells, self.p, self.dist_matrix)

    def run_set_cover(self, radius_km: float) -> List[int]:
        """Solves the Set Covering Location Problem exactly using MILP (HiGHS) with heuristic fallback."""
        return solve_set_cover_milp(self.cells, radius_km, self.dist_matrix)