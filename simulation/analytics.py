from typing import List, Dict, Any
import pandas as pd
import numpy as np

class SimulationAnalytics:
    """Provides advanced analytics on simulation results."""
    
    @staticmethod
    def compare_scenarios(scenario_results: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
        """
        Compares multiple scenarios based on mean values.
        scenario_results format: {"scenario_name": monte_carlo_summary}
        """
        data = []
        for name, summary in scenario_results.items():
            row = {"Scenario": name}
            for metric, stats in summary.items():
                if isinstance(stats, dict) and "mean" in stats:
                    row[metric] = stats["mean"]
            data.append(row)
            
        return pd.DataFrame(data)

    @staticmethod
    def identify_bottlenecks(system_states: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identifies depots or routes with consistently high utilization or congestion."""
        # Analysis logic based on system state history
        return {
            "top_congested_routes": [],
            "max_utilized_depots": []
        }

    @staticmethod
    def sensitivity_analysis(metric: str, variations: Dict[float, Dict[str, Any]]) -> pd.DataFrame:
        """Analyzes how a metric changes with varying input parameters."""
        data = []
        for var_val, summary in variations.items():
            data.append({
                "ParameterValue": var_val,
                "MetricMean": summary[metric]["mean"]
            })
        return pd.DataFrame(data)
