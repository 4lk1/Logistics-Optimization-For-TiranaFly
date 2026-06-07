from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from uuid import UUID, uuid4
import time
from schemas.io_models import Depot, Drone, Battery, FlightEdge, Route, AdministrativeUnit

@dataclass
class DroneTwin:
    """Digital Twin of a Drone for simulation state tracking."""
    base: Drone
    battery: Battery
    current_lat: float
    current_lon: float
    status: str = "IDLE"
    last_update: float = field(default_factory=time.time)
    odometer_km: float = 0.0
    missions_completed: int = 0
    failure_count: int = 0
    health_index: float = 1.0  # 0.0 to 1.0
    
    def update_position(self, lat: float, lon: float, distance_delta: float):
        self.current_lat = lat
        self.current_lon = lon
        self.odometer_km += distance_delta
        self.last_update = time.time()
        
    def consume_energy(self, amount_wh: float):
        self.battery.current_charge_wh = max(0.0, self.battery.current_charge_wh - amount_wh)
        
    def check_health(self):
        # Simplistic health model based on odometer and battery state
        self.health_index = max(0.0, 1.0 - (self.odometer_km / 10000.0) - (1.0 - self.battery.state_of_health_pct / 100.0))

@dataclass
class DepotTwin:
    """Digital Twin of a Depot managing its local resources."""
    base: Depot
    drones: List[DroneTwin] = field(default_factory=list)
    battery_pool: List[Battery] = field(default_factory=list)
    is_operational: bool = True
    power_grid_health: float = 1.0
    communication_latency_ms: float = 20.0
    uptime_seconds: float = 0.0
    
    def get_available_drones(self) -> List[DroneTwin]:
        return [d for d in self.drones if d.status == "IDLE" and d.battery.charge_ratio > 0.8]

    def fail(self):
        self.is_operational = False
        for d in self.drones:
            if d.status == "IDLE":
                d.status = "OUT_OF_SERVICE"

@dataclass
class RouteTwin:
    """Digital Twin of a flight route with dynamic conditions."""
    base: Route
    congestion_factor: float = 1.0
    weather_penalty: float = 1.0
    is_active: bool = True
    active_drones: int = 0
    
    @property
    def effective_traversal_time(self) -> float:
        return self.base.estimated_time_seconds * self.congestion_factor * self.weather_penalty

@dataclass
class AdministrativeUnitTwin:
    """Digital Twin of an administrative unit for demand modeling."""
    base: AdministrativeUnit
    population_density_multiplier: float = 1.0
    current_demand_surge: float = 1.0
    active_requests: int = 0
    
    def simulate_growth(self, rate: float):
        self.base.population = int(self.base.population * (1 + rate))

@dataclass
class MunicipalityTwin:
    """Digital Twin of the entire Municipality (Tirana)."""
    name: str = "Tirana"
    units: List[AdministrativeUnitTwin] = field(default_factory=list)
    total_area_km2: float = 41.8  # Urban area approx
    
    @property
    def aggregate_population(self) -> int:
        return sum(u.base.population for u in self.units)

@dataclass
class FleetTwin:
    """Digital Twin of the entire operational fleet."""
    depots: List[DepotTwin] = field(default_factory=list)
    total_drones: int = 0
    active_missions: int = 0
    
    def sync_counts(self):
        self.total_drones = sum(len(d.drones) for d in self.depots)

@dataclass
class NetworkTwin:
    """Digital Twin of the entire graph and airspace."""
    routes: List[RouteTwin] = field(default_factory=list)
    restricted_zones: List[Dict[str, Any]] = field(default_factory=list)
    global_weather_impact: float = 1.0

@dataclass
class SystemTwin:
    """The complete Digital Twin of the TiranaFly Ecosystem."""
    municipality: MunicipalityTwin
    fleet: FleetTwin
    network: NetworkTwin
    simulation_clock: float = 0.0
    tick_rate_sec: float = 1.0
    
    def step(self):
        self.simulation_clock += self.tick_rate_sec
        # Logic for system-wide state propagation would go here
