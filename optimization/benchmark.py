import pandas as pd
from typing import List, Dict, Any
from .models import OptimizationResult

class BenchmarkSystem:
    """
    Compares different optimization methods based on key performance indicators.
    """

    def __init__(self, results: List[OptimizationResult]):
        self.results = results

    def generate_report(self) -> pd.DataFrame:
        """
        Creates a comparison table of all results.
        """
        data = []
        for res in self.results:
            data.append({
                "Method": res.method_name,
                "Coverage (%)": (res.total_population_served / 807029.0) * 100,
                "Num Depots": len(res.depots),
                "Cost ($)": res.total_cost,
                "Avg Dist (m)": res.avg_distance,
                "Max Dist (m)": res.max_distance,
                "Runtime (s)": res.runtime_sec,
                "MOO Score": res.metrics.get('moo_score', 0.0)
            })
            
        return pd.DataFrame(data).sort_values(by="MOO Score", ascending=False)

    def print_summary(self):
        df = self.generate_report()
        print("\n--- TiranaFly Optimization Benchmark ---")
        print(df.to_string(index=False))
        print("---------------------------------------\n")
