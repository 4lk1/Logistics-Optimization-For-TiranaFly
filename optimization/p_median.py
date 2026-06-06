# filename: optimization/p_median.py
import numpy as np
from typing import List, Tuple
from scipy.optimize import milp, Bounds, LinearConstraint
from schemas.io_models import HexCell

def solve_p_median_milp(cells: List[HexCell], p: int, dist_matrix: np.ndarray) -> List[int]:
    """
    Solves the p-median facility location problem exactly using SciPy's MILP solver (HiGHS).
    Falls back to a Teitz-Bart exchange heuristic if the exact solver fails or encounters issues.
    
    Returns:
        List of selected cell indices to host depots.
    """
    n = len(cells)
    weights = np.array([c.local_demand_coefficient for c in cells])
    
    # Variables:
    # x_ij: client i served by candidate facility j (n * n variables)
    # y_j: candidate facility j is open (n variables)
    # total variables = n^2 + n
    # Layout: [x_00, ..., x_0(n-1), x_10, ..., x_(n-1)(n-1), y_0, ..., y_(n-1)]
    
    # Cost coefficients (minimize sum of weighted travel distances)
    c = np.zeros(n * n + n)
    for i in range(n):
        for j in range(n):
            c[i * n + j] = weights[i] * dist_matrix[i, j]
            
    # Constraints:
    # 1. Sum_j x_ij = 1 for all i (n equality constraints)
    A_eq1 = np.zeros((n, n * n + n))
    for i in range(n):
        A_eq1[i, i * n : (i + 1) * n] = 1.0
        
    # 2. Sum_j y_j = p (1 equality constraint)
    A_eq2 = np.zeros((1, n * n + n))
    A_eq2[0, n * n :] = 1.0
    
    # Combine equality constraints
    A_eq = np.vstack([A_eq1, A_eq2])
    b_eq = np.append(np.ones(n), float(p))
    
    # 3. x_ij - y_j <= 0 for all i, j (n^2 upper bound inequality constraints)
    A_ub = np.zeros((n * n, n * n + n))
    for i in range(n):
        for j in range(n):
            row = i * n + j
            A_ub[row, row] = 1.0        # x_ij
            A_ub[row, n * n + j] = -1.0  # -y_j
            
    b_ub = np.zeros(n * n)
    
    # Combine constraints into SciPy LinearConstraint representation:
    # lower_bounds <= A * X <= upper_bounds
    A = np.vstack([A_eq, A_ub])
    lower_bounds = np.append(b_eq, np.full(n * n, -np.inf))
    upper_bounds = np.append(b_eq, b_ub)
    
    linear_constraints = LinearConstraint(A, lower_bounds, upper_bounds)
    
    # Variable bounds: 0 <= X <= 1
    bounds = Bounds(np.zeros(n * n + n), np.ones(n * n + n))
    
    # Integrality: all decision variables are binary (1.0)
    integrality = np.ones(n * n + n)
    
    res = milp(c=c, bounds=bounds, constraints=linear_constraints, integrality=integrality)
    
    if res.success and res.x is not None:
        y_vals = res.x[n * n :]
        selected_indices = [j for j in range(n) if y_vals[j] > 0.5]
        # In case solver outputs slightly more or fewer due to tolerances
        if len(selected_indices) == p:
            return selected_indices
            
    # Fallback to Teitz-Bart exchange heuristic
    return solve_p_median_heuristic(n, p, weights, dist_matrix)

def solve_p_median_heuristic(n: int, p: int, weights: np.ndarray, dist_matrix: np.ndarray) -> List[int]:
    """
    Teitz-Bart local search heuristic for the p-Median problem.
    """
    # 1. Greedy initialization
    selected = []
    uncovered = set(range(n))
    
    for _ in range(p):
        best_candidate = -1
        best_cost = float('inf')
        for j in uncovered:
            temp_selected = selected + [j]
            cost = _evaluate_median_cost(temp_selected, weights, dist_matrix)
            if cost < best_cost:
                best_cost = cost
                best_candidate = j
        if best_candidate != -1:
            selected.append(best_candidate)
            uncovered.remove(best_candidate)
            
    # 2. Teitz-Bart swap exchanges
    improved = True
    while improved:
        improved = False
        for i, current in enumerate(selected):
            best_exchange = current
            best_cost = _evaluate_median_cost(selected, weights, dist_matrix)
            
            for candidate in uncovered:
                temp_selected = list(selected)
                temp_selected[i] = candidate
                cost = _evaluate_median_cost(temp_selected, weights, dist_matrix)
                if cost < best_cost:
                    best_cost = cost
                    best_exchange = candidate
                    
            if best_exchange != current:
                selected[i] = best_exchange
                uncovered.remove(best_exchange)
                uncovered.add(current)
                improved = True
                break # Restart loop search
                
    return selected

def _evaluate_median_cost(selected_indices: List[int], weights: np.ndarray, dist_matrix: np.ndarray) -> float:
    if not selected_indices:
        return float('inf')
    sub_matrix = dist_matrix[:, selected_indices]
    min_distances = np.min(sub_matrix, axis=1)
    return float(np.sum(min_distances * weights))
