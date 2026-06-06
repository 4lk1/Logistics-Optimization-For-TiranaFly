# filename: optimization/set_cover.py
import numpy as np
from typing import List
from scipy.optimize import milp, Bounds, LinearConstraint
from schemas.io_models import HexCell

def solve_set_cover_milp(cells: List[HexCell], radius_km: float, dist_matrix: np.ndarray) -> List[int]:
    """
    Solves the Set Covering Location Problem (SCLP) exactly using SciPy's MILP solver.
    Minimizes the number of depots built such that all clients are covered within a radius.
    Falls back to a greedy set covering heuristic if the solver fails.
    
    Returns:
        List of selected cell indices hosting depots.
    """
    n = len(cells)
    if n == 0:
        return []
        
    # Cost coefficient vector: minimize sum y_j
    c = np.ones(n)
    
    # A_ij = 1 if dist(i, j) <= radius_km, else 0
    # Constraint: Sum_j A_ij * y_j >= 1 for all i
    A = (dist_matrix <= radius_km).astype(float)
    
    # Represent as SciPy LinearConstraint: lower_bounds <= A * y <= upper_bounds
    lower_bounds = np.ones(n)
    upper_bounds = np.full(n, np.inf)
    
    linear_constraints = LinearConstraint(A, lower_bounds, upper_bounds)
    
    # Variable bounds: 0 <= y_j <= 1
    bounds = Bounds(np.zeros(n), np.ones(n))
    
    # Integrality: all variables are binary (1.0)
    integrality = np.ones(n)
    
    res = milp(c=c, bounds=bounds, constraints=linear_constraints, integrality=integrality)
    
    if res.success and res.x is not None:
        selected_indices = [j for j in range(n) if res.x[j] > 0.5]
        return selected_indices
        
    # Fallback to greedy heuristic
    return solve_set_cover_greedy(n, radius_km, dist_matrix)

def solve_set_cover_greedy(n: int, radius_km: float, dist_matrix: np.ndarray) -> List[int]:
    """
    Greedy Set Cover heuristic.
    """
    uncovered = set(range(n))
    selected = []
    
    while uncovered:
        best_candidate = -1
        best_coverage = set()
        
        for j in range(n):
            covered = set([i for i in uncovered if dist_matrix[i, j] <= radius_km])
            if len(covered) > len(best_coverage):
                best_coverage = covered
                best_candidate = j
                
        if best_candidate == -1 or not best_coverage:
            # If any nodes are completely isolated (islands exceeding radius), cover them individually
            if uncovered:
                isolated_node = list(uncovered)[0]
                selected.append(isolated_node)
                uncovered.remove(isolated_node)
                continue
            break
            
        selected.append(best_candidate)
        uncovered -= best_coverage
        
    return selected
