from ortools.linear_solver import pywraplp
import numpy as np
from .models import DepotCandidate, DemandAssignment, OptimizationResult
import time

class SetCoverOptimizer:
    """
    Solves the Set Covering Problem (SCP).
    Objective: Minimize the number of depots such that every demand point is within R_max.
    """

    def __init__(self, r_max_m: float = 5000.0):
        self.r_max_m = r_max_m

    def optimize(self, demand_coords: np.ndarray, candidate_coords: np.ndarray) -> OptimizationResult:
        """
        Finds the minimum set of depots to cover all demand.
        """
        solver = pywraplp.Solver.CreateSolver('SCIP')
        if not solver:
            raise RuntimeError("SCIP solver not available")

        num_demand = len(demand_coords)
        num_candidates = len(candidate_coords)

        # 1. Coverage Matrix (N x M)
        # a[i, j] = 1 if demand i is covered by candidate j within r_max
        a = np.zeros((num_demand, num_candidates), dtype=int)
        for i in range(num_demand):
            for j in range(num_candidates):
                dist = self._haversine(
                    demand_coords[i, 0], demand_coords[i, 1],
                    candidate_coords[j, 0], candidate_coords[j, 1]
                )
                if dist <= self.r_max_m:
                    a[i, j] = 1

        # 2. Variables
        # y[j] = 1 if depot j is opened
        y = {}
        for j in range(num_candidates):
            y[j] = solver.BoolVar(f'y_{j}')

        # 3. Constraints
        # Every demand point i must be covered by at least one open depot
        for i in range(num_demand):
            solver.Add(sum(a[i, j] * y[j] for j in range(num_candidates)) >= 1)

        # 4. Objective: Minimize total depots
        solver.Minimize(sum(y[j] for j in range(num_candidates)))

        # 5. Solve
        start_time = time.perf_counter()
        status = solver.Solve()
        end_time = time.perf_counter()

        if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
            depots = []
            for j in range(num_candidates):
                if y[j].solution_value() > 0.5:
                    depots.append(DepotCandidate(
                        id=f"setcover_depot_{j}",
                        lat=candidate_coords[j, 0],
                        lng=candidate_coords[j, 1]
                    ))

            # Assignments (to the nearest open depot)
            assignments = []
            total_dist = 0.0
            max_dist = 0.0
            for i in range(num_demand):
                best_dist = float('inf')
                best_depot = None
                for j in range(num_candidates):
                    if y[j].solution_value() > 0.5 and a[i, j] == 1:
                        dist = self._haversine(
                            demand_coords[i, 0], demand_coords[i, 1],
                            candidate_coords[j, 0], candidate_coords[j, 1]
                        )
                        if dist < best_dist:
                            best_dist = dist
                            best_depot = f"setcover_depot_{j}"
                
                assignments.append(DemandAssignment(
                    h3_id=str(i),
                    depot_id=best_depot,
                    distance=best_dist,
                    population_served=0
                ))
                total_dist += best_dist
                max_dist = max(max_dist, best_dist)

            return OptimizationResult(
                method_name="Set Cover",
                depots=depots,
                assignments=assignments,
                total_population_served=0,
                total_cost=len(depots) * 50000.0,
                avg_distance=total_dist / num_demand if num_demand > 0 else 0,
                max_distance=max_dist,
                runtime_sec=end_time - start_time
            )
        else:
            raise RuntimeError("Set Cover solver failed")

    @staticmethod
    def _haversine(lat1, lon1, lat2, lon2) -> float:
        from math import radians, cos, sin, asin, sqrt
        R = 6371000
        dLat, dLon = radians(lat2-lat1), radians(lon2-lon1)
        a = sin(dLat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dLon/2)**2
        return R * 2 * asin(sqrt(a))
