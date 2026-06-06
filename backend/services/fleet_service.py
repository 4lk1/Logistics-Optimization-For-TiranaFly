from sqlalchemy.orm import Session
from backend.db.models.spatial import Drone, Depot, Battery, Mission
from fleet.models import DroneStatus as FleetDroneStatus
from fleet.dispatch_engine import DispatchEngine
from fleet.drone_scheduler import DroneScheduler
from fleet.battery_manager import BatteryManager
from typing import List

class FleetService:
    @staticmethod
    def get_fleet_status(db: Session):
        return db.query(Drone).all()

    @staticmethod
    def initialize_fleet(db: Session, depot_id: str, num_drones: int = 5):
        """Seeds a depot with drones and batteries."""
        depot = db.query(Depot).filter(Depot.id == depot_id).first()
        if not depot:
            return None
            
        for i in range(num_drones):
            batt = Battery(id=f"batt_{depot_id}_{i}", soc=1.0, soh=1.0, cycle_count=0)
            db.add(batt)
            drone = Drone(
                id=f"drone_{depot_id}_{i}",
                model="TiranaFly-V1",
                status="AVAILABLE",
                depot_id=depot_id,
                battery=batt
            )
            db.add(drone)
            
        db.commit()
        return True

    @staticmethod
    def dispatch_mission(db: Session, depot_id: str, dest_h3: str, distance_m: float):
        """Orchestrates mission dispatch via Fleet Engine."""
        # This would involve loading state into Fleet Engine classes
        # and then saving back to DB. Simplified here.
        drone = db.query(Drone).filter(Drone.depot_id == depot_id, Drone.status == "AVAILABLE").first()
        if not drone:
            return None
            
        drone.status = "EN_ROUTE"
        mission = Mission(
            id=f"miss_{drone.id}_{dest_h3}",
            drone_id=drone.id,
            status="ACTIVE",
            payload_kg=1.0
        )
        db.add(mission)
        db.commit()
        return mission
