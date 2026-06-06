from typing import List, Dict, Any
from .models import DepotFleet, DroneStatus, Drone

class ResilienceAnalyzer:
    """
    Simulates operational disruptions and analyzes system recovery.
    """

    @staticmethod
    def simulate_depot_failure(fleet: DepotFleet) -> Dict[str, Any]:
        """Marks all drones at a depot as OUT_OF_SERVICE."""
        for drone in fleet.drones:
            drone.status = DroneStatus.OUT_OF_SERVICE
            
        return {
            "depot_id": fleet.depot_id,
            "drones_impacted": len(fleet.drones),
            "status": "OFFLINE"
        }

    @staticmethod
    def simulate_random_failures(fleet: DepotFleet, failure_rate: float = 0.05) -> List[str]:
        """Simulates random drone hardware failures."""
        import random
        failed_ids = []
        for drone in fleet.drones:
            if drone.status != DroneStatus.OUT_OF_SERVICE and random.random() < failure_rate:
                drone.status = DroneStatus.MAINTENANCE
                failed_ids.append(drone.id)
        return failed_ids

    @staticmethod
    def calculate_recovery_time(failed_drones: List[Drone]) -> float:
        """Estimates time in hours to return drones to service."""
        # Assume average 4 hours per maintenance event
        return len(failed_drones) * 4.0

    @staticmethod
    def analyze_capacity_loss(fleet: DepotFleet) -> float:
        """Returns the percentage of fleet currently unavailable."""
        total = len(fleet.drones)
        if total == 0: return 0.0
        
        unavailable = len([d for d in fleet.drones if d.status in [
            DroneStatus.MAINTENANCE, DroneStatus.OUT_OF_SERVICE
        ]])
        
        return unavailable / total
