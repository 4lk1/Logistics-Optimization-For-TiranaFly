from dataclasses import dataclass, field
from typing import List, Dict, Any
import numpy as np

@dataclass
class SimulationKPIs:
    coverage_pct: float = 0.0
    demand_served_pct: float = 0.0
    avg_delivery_time_min: float = 0.0
    total_energy_kwh: float = 0.0
    fleet_utilization_pct: float = 0.0
    mission_success_rate: float = 0.0
    battery_health_index: float = 0.0
    network_robustness_index: float = 0.0
    total_failed_missions: int = 0
    total_successful_missions: int = 0

class KPIEngine:
    """Aggregates and computes Key Performance Indicators."""
    
    def __init__(self):
        self.reset()

    def reset(self):
        self.metrics = SimulationKPIs()
        self._delivery_times = []
        self._energy_consumptions = []
        self._battery_healths = []
        self._utilization_samples = []

    def record_mission_success(self, duration_min: float, energy_kwh: float):
        self.metrics.total_successful_missions += 1
        self._delivery_times.append(duration_min)
        self._energy_consumptions.append(energy_kwh)

    def record_mission_failure(self):
        self.metrics.total_failed_missions += 1

    def record_fleet_state(self, utilization_pct: float, avg_battery_health: float):
        self._utilization_samples.append(utilization_pct)
        self._battery_healths.append(avg_battery_health)

    def finalize(self) -> SimulationKPIs:
        total = self.metrics.total_successful_missions + self.metrics.total_failed_missions
        if total > 0:
            self.metrics.mission_success_rate = (self.metrics.total_successful_missions / total) * 100.0
        
        if self._delivery_times:
            self.metrics.avg_delivery_time_min = float(np.mean(self._delivery_times))
            
        if self._energy_consumptions:
            self.metrics.total_energy_kwh = float(np.sum(self._energy_consumptions))
            
        if self._utilization_samples:
            self.metrics.fleet_utilization_pct = float(np.mean(self._utilization_samples))
            
        if self._battery_healths:
            self.metrics.battery_health_index = float(np.mean(self._battery_healths))
            
        return self.metrics
