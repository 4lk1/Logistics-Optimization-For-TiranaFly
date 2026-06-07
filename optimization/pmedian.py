from ortools.linear_solver import pywraplp
import numpy as np
from typing import List, Tuple
from .models import DepotCandidate, DemandAssignment, OptimizationResult
from gis.coordinate_utils import haversine_distance
import time

class PMedianOptimizer:
    """
    Exact P-Median formulation using Mixed-Integer Programming (MIP).
    Objective: Minimize total weighted distance between demand and depots.
    """

    def __init__(self, p: int = 5):
        self.p = p

    def optimize(self, demand_coords: np.ndarray, candidate_coords: np.ndarray, populations: np.ndarray) -> OptimizationResult:
        """
        Solves the P-Median problem.
        demand_coords: Nx2 array of demand (H3) coordinates
        candidate_coords: Mx2 array of potential depot coordinates
        populations: N array of population weights
        """
        solver = pywraplp.Solver.CreateSolver('SCIP')
        if not solver:
            solver = pywraplp.Solver.CreateSolver('GLOP')

        num_demand = len(demand_coords)
        num_candidates = len(candidate_coords)

        # 1. Calculate distance matrix (N x M)
        dist_matrix = np.zeros((num_demand, num_candidates))
        for i in range(num_demand):
            for j in range(num_candidates):
                dist_matrix[i, j] = haversine_distance(
                    demand_coords[i, 0], demand_coords[i, 1],
                    candidate_coords[j, 0], candidate_coords[j, 1]
                )

        # 2. Decision Variables
        # x[i, j] = 1 if demand i is assigned to depot j
        x = {}
        for i in range(num_demand):
            for j in range(num_candidates):
                x[i, j] = solver.BoolVar(f'x_{i}_{j}')

        # y[j] = 1 if depot j is opened
        y = {}
        for j in range(num_candidates):
            y[j] = solver.BoolVar(f'y_{j}')

        # 3. Constraints
        # Each demand must be assigned to exactly one depot
        for i in range(num_demand):
            solver.Add(sum(x[i, j] for j in range(num_candidates)) == 1)

        # Demand can only be assigned to an open depot
        for i in range(num_demand):
            for j in range(num_candidates):
                solver.Add(x[i, j] <= y[j])

        # Exactly p depots must be opened
        solver.Add(sum(y[j] for j in range(num_candidates)) == self.p)

        # 4. Objective: Minimize total weighted distance
        objective = solver.Objective()
        for i in range(num_demand):
            for j in range(num_candidates):
                objective.SetCoefficient(x[i, j], float(dist_matrix[i, j] * populations[i]))
        objective.SetMinimization()

        # 5. Solve
        start_time = time.perf_counter()
        status = solver.Solve()
        end_time = time.perf_counter()

        if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
            depots = []
            for j in range(num_candidates):
                if y[j].solution_value() > 0.5:
                    depots.append(DepotCandidate(
                        id=f"pmedian_depot_{j}",
                        lat=candidate_coords[j, 0],
                        lng=candidate_coords[j, 1]
                    ))

            assignments = []
            total_pop = 0
            total_dist = 0.0
            max_dist = 0.0
            
            for i in range(num_demand):
                for j in range(num_candidates):
                    if x[i, j].solution_value() > 0.5:
                        dist = dist_matrix[i, j]
                        pop = populations[i]
                        assignments.append(DemandAssignment(
                            h3_id=str(i), # Simplified for exact solve
                            depot_id=f"pmedian_depot_{j}",
                            distance=dist,
                            population_served=int(pop)
                        ))
                        total_pop += pop
                        total_dist += dist * pop
                        max_dist = max(max_dist, dist)

            return OptimizationResult(
                method_name="P-Median",
                depots=depots,
                assignments=assignments,
                total_population_served=int(total_pop),
                total_cost=len(depots) * 50000.0,
                avg_distance=total_dist / total_pop if total_pop > 0 else 0,
                max_distance=max_dist,
                runtime_sec=end_time - start_time
            )
        else:
            raise RuntimeError("Solver failed to find a solution")

    @staticmethod
    def _haversine(lat1, lon1, lat2, lon2) -> float:
        from math import radians, cos, sin, asin, sqrt
        R = 6371000
        dLat, dLon = radians(lat2-lat1), radians(lon2-lon1)
        a = sin(dLat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dLon/2)**2
        return R * 2 * asin(sqrt(a))
