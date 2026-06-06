import pandas as pd
import numpy as np
from typing import List, Dict, Any
from .models import OptimizationResult, CoverageZone

class CoverageOptimizer:
    """
    Analyzes and optimizes population coverage for a given set of depots.
    """

    def __init__(self, target_population: int = 807029):
        self.target_population = target_population

    def analyze_coverage(self, result: OptimizationResult) -> Dict[str, Any]:
        """
        Calculates detailed coverage metrics for an optimization result.
        """
        assignments = result.assignments
        total_served = sum(a.population_served for a in assignments)
        
        coverage_ratio = total_served / self.target_population if self.target_population > 0 else 0
        
        # Group by depot to create CoverageZones
        df = pd.DataFrame([
            {
                'depot_id': a.depot_id,
                'h3_id': a.h3_id,
                'population': a.population_served,
                'distance': a.distance
            } for a in assignments
        ])
        
        zones = []
        if not df.empty:
            for depot_id, group in df.groupby('depot_id'):
                zones.append(CoverageZone(
                    depot_id=str(depot_id),
                    assigned_h3_ids=group['h3_id'].tolist(),
                    total_population=int(group['population'].sum()),
                    avg_distance=group['distance'].mean(),
                    max_distance=group['distance'].max()
                ))

        return {
            "method": result.method_name,
            "population_served": int(total_served),
            "coverage_ratio": float(coverage_ratio),
            "num_depots": len(result.depots),
            "avg_distance": result.avg_distance,
            "max_distance": result.max_distance,
            "zones": zones
        }

    def evaluate_multi_objective(self, result: OptimizationResult, alpha=0.4, beta=0.3, gamma=0.2, delta=0.1) -> float:
        """
        Calculates a unified score based on multiple criteria:
        f = alpha*coverage + beta*cost_inv + gamma*dist_inv + delta*equity_inv
        """
        coverage = sum(a.population_served for a in result.assignments) / self.target_population
        
        # Inverse metrics (normalized)
        # Assuming max cost is 1,000,000, max dist is 20,000
        cost_score = max(0, 1 - (result.total_cost / 1000000.0))
        dist_score = max(0, 1 - (result.avg_distance / 20000.0))
        equity_score = max(0, 1 - (result.max_distance / 25000.0))
        
        score = (alpha * coverage) + (beta * cost_score) + (gamma * dist_score) + (delta * equity_score)
        return score
