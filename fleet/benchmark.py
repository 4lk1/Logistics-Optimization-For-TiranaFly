import pandas as pd
from typing import List, Dict, Any
import datetime
from .demand_forecaster import DemandForecaster
from .fleet_allocator import FleetAllocator

class FleetBenchmark:
    """
    Compares fleet performance across different operational scenarios.
    """

    def __init__(self, forecaster: DemandForecaster, allocator: FleetAllocator):
        self.forecaster = forecaster
        self.allocator = allocator

    def run_scenarios(self) -> pd.DataFrame:
        """
        Runs benchmarks for Normal, Peak, and Holiday scenarios.
        """
        scenarios = [
            ("Normal Tuesday 10AM", datetime.datetime(2026, 6, 9, 10, 0)),
            ("Friday Evening Peak", datetime.datetime(2026, 6, 12, 19, 0)),
            ("Sunday Night Low", datetime.datetime(2026, 6, 14, 23, 0)),
            ("Holiday Spike (Simulated)", None)
        ]
        
        results = []
        for name, dt in scenarios:
            if dt:
                arrival_rate = self.forecaster.get_total_expected_demand(dt)
            else:
                # Simulated spike
                arrival_rate = (self.forecaster.total_h3_pop / 1000.0) * self.forecaster.BASE_ORDER_RATE * 0.5 # 50% pop ordering at once
            
            required_fleet = self.allocator.calculate_required_fleet(arrival_rate)
            utilization = self.allocator.estimate_utilization(arrival_rate, required_fleet)
            
            results.append({
                "Scenario": name,
                "Arrival Rate (ord/h)": round(arrival_rate, 2),
                "Required Fleet": required_fleet,
                "Expected Utilization": round(utilization, 2)
            })
            
        return pd.DataFrame(results)

    def print_benchmark(self):
        df = self.run_scenarios()
        print("\n--- TiranaFly Fleet Benchmarks ---")
        print(df.to_string(index=False))
        print("----------------------------------\n")
