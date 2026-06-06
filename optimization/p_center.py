# filename: optimization/p_center.py
import numpy as np
from typing import List, Tuple
from scipy.optimize import milp, Bounds, LinearConstraint
from schemas.io_models import HexCell

def solve_p_center_milp(cells: List[HexCell], p: int, dist_matrix: np.ndarray) -> List[int]:
    """
    Solves the p-center minimax facility location problem exactly using SciPy's MILP solver.
    Falls back to a bisection search greedy coverage heuristic if the exact solver fails.
    
    Returns:
        List of selected cell indices hosting depots.
    """
    n = len(cells)
    if n <= p:
        return list(range(n))
        
    # Variables:
    # x_ij: client i served by facility j (n^2 variables)
    # y_j: facility j is open (n variables)
    # Z: minimax maximum distance (1 variable)
    # total variables = n^2 + n + 1
    # Layout: [x_00, ..., x_(n-1)(n-1), y_0, ..., y_(n-1), Z]
    
    # Minimize Z
    c = np.zeros(n * n + n + 1)
    c[-1] = 1.0
    
    # Constraints:
    # 1. Sum_j x_ij = 1 for all i (n equality constraints)
    A_eq1 = np.zeros((n, n * n + n + 1))
    for i in range(n):
        A_eq1[i, i * n : (i + 1) * n] = 1.0
        
    # 2. Sum_j y_j = p (1 equality constraint)
    A_eq2 = np.zeros((1, n * n + n + 1))
    A_eq2[0, n * n : n * n + n] = 1.0
    
    A_eq = np.vstack([A_eq1, A_eq2])
    b_eq = np.append(np.ones(n), float(p))
    
    # 3. x_ij - y_j <= 0 (n^2 inequality constraints)
    A_ub1 = np.zeros((n * n, n * n + n + 1))
    for i in range(n):
        for j in range(n):
            row = i * n + j
            A_ub1[row, row] = 1.0
            A_ub1[row, n * n + j] = -1.0
            
    # 4. Sum_j d_ij * x_ij - Z <= 0 (n minimax inequality constraints)
    A_ub2 = np.zeros((n, n * n + n + 1))
    for i in range(n):
        for j in range(n):
            A_ub2[i, i * n + j] = dist_matrix[i, j]
        A_ub2[i, -1] = -1.0 # -Z
        
    A_ub = np.vstack([A_ub1, A_ub2])
    b_ub = np.zeros(n * n + n)
    
    # Combine constraints
    # lower_bounds <= A * X <= upper_bounds
    A = np.vstack([A_eq, A_ub])
    lower_bounds = np.append(b_eq, np.full(n * n + n, -np.inf))
    upper_bounds = np.append(b_eq, b_ub)
    
    linear_constraints = LinearConstraint(A, lower_bounds, upper_bounds)
    
    # Variable bounds: x_ij, y_j are in [0, 1], Z is in [0, inf]
    lb = np.zeros(n * n + n + 1)
    ub = np.append(np.ones(n * n + n), np.inf)
    bounds = Bounds(lb, ub)
    
    # Integrality: x_ij, y_j are binary (1.0), Z is continuous (0.0)
    integrality = np.append(np.ones(n * n + n), 0.0)
    
    res = milp(c=c, bounds=bounds, constraints=linear_constraints, integrality=integrality)
    
    if res.success and res.x is not None:
        y_vals = res.x[n * n : n * n + n]
        selected_indices = [j for j in range(n) if y_vals[j] > 0.5]
        if len(selected_indices) == p:
            return selected_indices
            
    # Fallback to Bisection + Greedy cover heuristic
    return solve_p_center_heuristic(n, p, dist_matrix)

def solve_p_center_heuristic(n: int, p: int, dist_matrix: np.ndarray) -> List[int]:
    """
    Finds a p-center solution by binary searching over all unique pairwise distances
    and verifying feasibility with a greedy set cover solver.
    """
    unique_dists = np.unique(dist_matrix)
    low = 0
    high = len(unique_dists) - 1
    best_selected = list(range(p))
    
    while low <= high:
        mid = (low + high) // 2
        radius = unique_dists[mid]
        
        # Test feasibility of covering all nodes with at most p hubs at maximum radius
        selected = _run_greedy_set_cover(n, radius, dist_matrix)
        if len(selected) <= p:
            # Feasible! Record and try to make the maximum radius smaller
            best_selected = selected
            high = mid - 1
        else:
            # Infeasible, need to allow a larger radius
            low = mid + 1
            
    # Pad selected set if we used fewer than p depots
    if len(best_selected) < p:
        remaining = set(range(n)) - set(best_selected)
        while len(best_selected) < p and remaining:
            sub = dist_matrix[:, list(best_selected)]
            min_dist = np.min(sub, axis=1)
            best_node = list(remaining)[np.argmax(min_dist[list(remaining)])]
            best_selected.append(best_node)
            remaining.remove(best_node)
            
    return best_selected[:p]

def _run_greedy_set_cover(n: int, radius: float, dist_matrix: np.ndarray) -> List[int]:
    uncovered = set(range(n))
    selected = []
    
    while uncovered:
        best_candidate = -1
        best_coverage = set()
        
        for j in range(n):
            covered = set([i for i in uncovered if dist_matrix[i, j] <= radius])
            if len(covered) > len(best_coverage):
                best_coverage = covered
                best_candidate = j
                
        if best_candidate == -1 or not best_coverage:
            break
            
        selected.append(best_candidate)
        uncovered -= best_coverage
        
    return selected
