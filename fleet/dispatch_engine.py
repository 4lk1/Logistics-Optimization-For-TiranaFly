from typing import List, Dict, Optional
from .models import FlightMission, DepotFleet, DroneStatus
from .drone_scheduler import DroneScheduler
from .battery_manager import BatteryManager

class DispatchEngine:
    """
    Core engine for processing delivery requests and orchestrating missions.
    """

    def __init__(self, scheduler: DroneScheduler, battery_manager: BatteryManager):
        self.scheduler = scheduler
        self.battery_manager = battery_manager
        self.active_missions: List[FlightMission] = []
        self.completed_missions: List[FlightMission] = []

    def dispatch_order(self, fleet: DepotFleet, destination_h3: str, distance_m: float, payload_kg: float) -> Optional[FlightMission]:
        """
        Orchestrates the dispatch workflow:
        Order -> Mission Creation -> Drone Selection -> Assignment.
        """
        # 1. Create Mission
        mission = FlightMission(
            origin_id=fleet.depot_id,
            destination_h3=destination_h3,
            distance_m=distance_m,
            payload_kg=payload_kg
        )
        
        # 2. Find Drone
        drone = self.scheduler.find_available_drone(fleet, mission)
        
        if drone:
            # 3. Assign and Start
            self.scheduler.assign_mission(drone, mission)
            self.active_missions.append(mission)
            return mission
        
        return None

    def complete_mission(self, fleet: DepotFleet, mission_id: str):
        """Processes mission completion and returns drone to idle/charging."""
        mission = next((m for m in self.active_missions if m.id == mission_id), None)
        if not mission:
            return
            
        drone = next((d for d in fleet.drones if d.id == mission.drone_id), None)
        if drone:
            # Update battery
            dist_km = mission.distance_m / 1000.0
            energy_used = self.battery_manager.estimate_energy_usage(dist_km, mission.payload_kg)
            # Round trip energy (return empty)
            energy_used += self.battery_manager.estimate_energy_usage(dist_km, 0.0)
            
            if drone.battery:
                self.battery_manager.update_battery_after_flight(drone.battery, energy_used)
                
                # Check if charging needed
                if drone.battery.soc < 0.3:
                    drone.status = DroneStatus.CHARGING
                else:
                    drone.status = DroneStatus.AVAILABLE
            
        self.active_missions.remove(mission)
        self.completed_missions.append(mission)

    def get_system_status(self) -> Dict[str, Any]:
        """Returns high-level operational stats."""
        return {
            "active_missions": len(self.active_missions),
            "completed_missions": len(self.completed_missions)
        }
