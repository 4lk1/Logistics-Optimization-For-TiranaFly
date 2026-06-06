from typing import List, Optional, Tuple
from .models import Drone, FlightMission, DroneStatus, DepotFleet
from .battery_manager import BatteryManager

class DroneScheduler:
    """
    Schedules missions by matching requirements with available drones.
    """

    def __init__(self, battery_manager: BatteryManager):
        self.battery_manager = battery_manager

    def find_available_drone(self, fleet: DepotFleet, mission: FlightMission) -> Optional[Drone]:
        """
        Selects an available drone that satisfies mission requirements.
        """
        # Requirements
        dist_km = mission.distance_m / 1000.0
        energy_req = self.battery_manager.estimate_energy_usage(dist_km, mission.payload_kg)
        
        # Buffer factor (e.g., 20% reserve)
        energy_req *= 1.2
        
        best_drone = None
        min_extra_energy = float('inf')
        
        for drone in fleet.drones:
            if drone.status != DroneStatus.AVAILABLE:
                continue
            
            if drone.battery and drone.battery.current_charge_kwh >= energy_req:
                extra = drone.battery.current_charge_kwh - energy_req
                if extra < min_extra_energy:
                    min_extra_energy = extra
                    best_drone = drone
                    
        return best_drone

    def assign_mission(self, drone: Drone, mission: FlightMission):
        """Finalizes the assignment and updates drone status."""
        drone.status = DroneStatus.EN_ROUTE
        mission.drone_id = drone.id
        mission.start_time = 0.0 # Placeholder for actual time

    def get_fleet_capacity(self, fleet: DepotFleet) -> int:
        """Returns the number of drones currently available for missions."""
        return len([d for d in fleet.drones if d.status == DroneStatus.AVAILABLE])
