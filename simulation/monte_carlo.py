import copy
from typing import List, Dict, Any
import numpy as np
from simulation.simulation_engine import SimulationEngine
from simulation.models import SystemTwin

class MonteCarloEngine:
    """Runs multiple simulation iterations to perform statistical analysis."""
    
    def __init__(self, system_twin: SystemTwin):
        self.base_system = system_twin

    def run_monte_carlo(self, iterations: int = 100, hours: float = 24.0, scenario_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Executes N runs and aggregates statistics."""
        results = []
        
        for i in range(iterations):
            # Create a deep copy of the system for each run to ensure independence
            system_copy = copy.deepcopy(self.base_system)
            engine = SimulationEngine(system_copy)
            
            kpis = engine.run_simulation(hours=hours, scenario_config=scenario_config)
            results.append(kpis)

        return self._aggregate_results(results)

    def _aggregate_results(self, results: List[Any]) -> Dict[str, Any]:
        """Computes statistical metrics across all runs."""
        metrics_keys = [
            "mission_success_rate", "avg_delivery_time_min", 
            "total_energy_kwh", "fleet_utilization_pct", 
            "battery_health_index"
        ]
        
        summary = {}
        for key in metrics_keys:
            values = [getattr(r, key) for r in results]
            summary[key] = {
                "mean": float(np.mean(values)),
                "median": float(np.median(values)),
                "std_dev": float(np.std(values)),
                "min": float(np.min(values)),
                "max": float(np.max(values)),
                "ci_95": self._confidence_interval(values)
            }
            
        summary["total_iterations"] = len(results)
        summary["total_successful_missions_agg"] = sum(r.total_successful_missions for r in results)
        summary["total_failed_missions_agg"] = sum(r.total_failed_missions for r in results)
        
        return summary

    def _confidence_interval(self, data: List[float], confidence: float = 0.95) -> tuple:
        a = 1.0 * np.array(data)
        n = len(a)
        if n < 2: return (0.0, 0.0)
        m, se = np.mean(a), float(np.std(a, ddof=1) / np.sqrt(n))
        h = se * 1.96 # Approx for 95%
        return (float(m - h), float(m + h))
