from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Optional, Any
from uuid import UUID, uuid4
import time

class DroneStatus(Enum):
    IDLE = auto()
    CHARGING = auto()
    AVAILABLE = auto()
    EN_ROUTE = auto()
    RETURNING = auto()
    MAINTENANCE = auto()
    OUT_OF_SERVICE = auto()

@dataclass
class Battery:
    """Represents a drone battery with health and charge tracking."""
    id: str = field(default_factory=lambda: str(uuid4()))
    capacity_kwh: float = 1.5
    current_charge_kwh: float = 1.5
    cycle_count: int = 0
    state_of_health: float = 1.0  # 0.0 to 1.0
    last_charged: float = field(default_factory=time.time)

    @property
    def soc(self) -> float:
        """State of Charge percentage."""
        return self.current_charge_kwh / self.capacity_kwh if self.capacity_kwh > 0 else 0.0

@dataclass
class Drone:
    """Represents a UAV in the fleet."""
    id: str = field(default_factory=lambda: str(uuid4()))
    model: str = "TiranaFly-V1"
    status: DroneStatus = DroneStatus.IDLE
    battery: Optional[Battery] = None
    max_payload_kg: float = 5.0
    fixed_energy_consumption: float = 0.05  # kWh/km base
    total_flight_time_s: float = 0.0
    last_maintenance_timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FlightMission:
    """Represents a delivery or service mission."""
    id: str = field(default_factory=lambda: str(uuid4()))
    origin_id: str
    destination_h3: str
    drone_id: Optional[str] = None
    payload_kg: float = 1.0
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    estimated_duration_s: float = 0.0
    estimated_energy_kwh: float = 0.0
    distance_m: float = 0.0

@dataclass
class DepotFleet:
    """Represents the collection of drones and batteries at a depot."""
    depot_id: str
    drones: List[Drone] = field(default_factory=list)
    batteries: List[Battery] = field(default_factory=list)
    charging_stations: int = 5

@dataclass
class FleetSnapshot:
    """A point-in-time state of the entire fleet."""
    timestamp: float = field(default_factory=time.time)
    status_counts: Dict[DroneStatus, int] = field(default_factory=dict)
    avg_soc: float = 0.0
    total_drones: int = 0

@dataclass
class MaintenanceEvent:
    """Logs a maintenance action."""
    drone_id: str
    timestamp: float = field(default_factory=time.time)
    description: str = ""
    cost: float = 0.0

@dataclass
class FleetMetrics:
    """Aggregated performance metrics."""
    utilization_rate: float = 0.0
    avg_wait_time_s: float = 0.0
    mission_success_rate: float = 0.0
    energy_efficiency_kwh_km: float = 0.0
    downtime_hours: float = 0.0
