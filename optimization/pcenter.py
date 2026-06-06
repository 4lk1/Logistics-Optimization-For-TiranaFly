from ortools.linear_solver import pywraplp
import numpy as np
from .models import DepotCandidate, DemandAssignment, OptimizationResult
import time

class PCenterOptimizer:
    """
    Min-Max optimization for depot placement.
    Objective: Minimize the maximum distance any demand point has to travel to its nearest depot.
    """

    def __init__(self, p: int = 5):
        self.p = p

    def optimize(self, demand_coords: np.ndarray, candidate_coords: np.ndarray) -> OptimizationResult:
        """
        Solves the P-Center problem.
        """
        solver = pywraplp.Solver.CreateSolver('SCIP')
        if not solver:
            raise RuntimeError("SCIP solver not available")

        num_demand = len(demand_coords)
        num_candidates = len(candidate_coords)

        # 1. Distance Matrix
        dist_matrix = np.zeros((num_demand, num_candidates))
        for i in range(num_demand):
            for j in range(num_candidates):
                dist_matrix[i, j] = self._haversine(
                    demand_coords[i, 0], demand_coords[i, 1],
                    candidate_coords[j, 0], candidate_coords[j, 1]
                )

        # 2. Variables
        # x[i, j] = 1 if demand i is served by depot j
        x = {}
        for i in range(num_demand):
            for j in range(num_candidates):
                x[i, j] = solver.BoolVar(f'x_{i}_{j}')

        # y[j] = 1 if depot j is opened
        y = {}
        for j in range(num_candidates):
            y[j] = solver.BoolVar(f'y_{j}')

        # z = maximum distance (to be minimized)
        z = solver.NumVar(0, float('inf'), 'z')

        # 3. Constraints
        # Each demand assigned to exactly one
        for i in range(num_demand):
            solver.Add(sum(x[i, j] for j in range(num_candidates)) == 1)

        # Only open depots can serve
        for i in range(num_demand):
            for j in range(num_candidates):
                solver.Add(x[i, j] <= y[j])

        # Open exactly p depots
        solver.Add(sum(y[j] for j in range(num_candidates)) == self.p)

        # z must be >= distance of any assigned demand
        for i in range(num_demand):
            solver.Add(z >= sum(x[i, j] * dist_matrix[i, j] for j in range(num_candidates)))

        # 4. Objective
        solver.Minimize(z)

        # 5. Solve
        start_time = time.perf_counter()
        status = solver.Solve()
        end_time = time.perf_counter()

        if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
            depots = []
            for j in range(num_candidates):
                if y[j].solution_value() > 0.5:
                    depots.append(DepotCandidate(
                        id=f"pcenter_depot_{j}",
                        lat=candidate_coords[j, 0],
                        lng=candidate_coords[j, 1]
                    ))

            assignments = []
            total_dist = 0.0
            for i in range(num_demand):
                for j in range(num_candidates):
                    if x[i, j].solution_value() > 0.5:
                        dist = dist_matrix[i, j]
                        assignments.append(DemandAssignment(
                            h3_id=str(i),
                            depot_id=f"pcenter_depot_{j}",
                            distance=dist,
                            population_served=0 # Not primary metric for P-Center
                        ))
                        total_dist += dist

            return OptimizationResult(
                method_name="P-Center",
                depots=depots,
                assignments=assignments,
                total_population_served=0,
                total_cost=len(depots) * 50000.0,
                avg_distance=total_dist / num_demand if num_demand > 0 else 0,
                max_distance=z.solution_value(),
                runtime_sec=end_time - start_time
            )
        else:
            raise RuntimeError("P-Center solver failed")

    @staticmethod
    def _haversine(lat1, lon1, lat2, lon2) -> float:
        from math import radians, cos, sin, asin, sqrt
        R = 6371000
        dLat, dLon = radians(lat2-lat1), radians(lon2-lon1)
        a = sin(dLat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dLon/2)**2
        return R * 2 * asin(sqrt(a))
