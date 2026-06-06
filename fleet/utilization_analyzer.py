from typing import List, Dict, Any
from .models import DepotFleet, DroneStatus, FlightMission, FleetMetrics

class UtilizationAnalyzer:
    """
    Calculates operational KPIs for the fleet and depots.
    """

    @staticmethod
    def calculate_fleet_utilization(fleet: DepotFleet) -> float:
        """Percentage of drones not in IDLE or OUT_OF_SERVICE status."""
        total = len(fleet.drones)
        if total == 0: return 0.0
        
        active = len([d for d in fleet.drones if d.status in [
            DroneStatus.EN_ROUTE, DroneStatus.RETURNING, DroneStatus.CHARGING
        ]])
        
        return active / total

    @staticmethod
    def analyze_missions(missions: List[FlightMission]) -> Dict[str, float]:
        """Analyzes mission data for efficiency metrics."""
        if not missions:
            return {"avg_distance_m": 0.0, "total_distance_m": 0.0}
            
        total_dist = sum(m.distance_m for m in missions)
        avg_dist = total_dist / len(missions)
        
        return {
            "avg_distance_m": avg_dist,
            "total_distance_m": total_dist,
            "count": float(len(missions))
        }

    @staticmethod
    def get_depot_kpis(fleet: DepotFleet, completed_missions: List[FlightMission]) -> FleetMetrics:
        """Aggregates all metrics into a FleetMetrics object."""
        util = UtilizationAnalyzer.calculate_fleet_utilization(fleet)
        mission_stats = UtilizationAnalyzer.analyze_missions(completed_missions)
        
        # In a real system, these would be tracked over time
        return FleetMetrics(
            utilization_rate=util,
            avg_wait_time_s=300.0, # Placeholder
            mission_success_rate=1.0, # Placeholder
            energy_efficiency_kwh_km=0.12 # Placeholder
        )
