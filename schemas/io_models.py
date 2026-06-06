# filename: schemas/io_models.py
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from pydantic import BaseModel, Field, field_validator
import numpy as np

@dataclass
class AdministrativeUnit:
    name: str
    population: int
    geojson_polygon: Dict
    demand_weight: float = 0.0

    def __post_init__(self):
        if self.population < 0:
            raise ValueError(f"Population invariant violation on {self.name}: cannot be negative.")

@dataclass
class HexCell:
    h3_index: str
    centroid_lat: float
    centroid_lon: float
    boundary_coordinates: List[Tuple[float, float]]
    assigned_unit: str
    local_demand_coefficient: float = 0.0

@dataclass
class DemandNode:
    node_id: str
    lat: float
    lon: float
    associated_h3_index: str
    normalized_demand: float
    peak_factor: float = 1.0

@dataclass
class Depot:
    depot_id: str
    lat: float
    lon: float
    h3_index: str
    max_drone_capacity: int
    active_fleet_count: int = 0
    charging_slots_available: int = 16
    assigned_fleet_size: int = 0

@dataclass
class Drone:
    drone_id: str
    model: str = "TF-2026-FleetMaster"
    max_payload_kg: float = 5.0
    empty_mass_kg: float = 9.5
    current_payload_kg: float = 0.0
    status: str = "IDLE"  # IDLE, EN_ROUTE, CHARGING, MAINTENANCE

@dataclass
class Battery:
    battery_id: str
    capacity_wh: float = 1200.0
    current_charge_wh: float = 1200.0
    state_of_health_pct: float = 100.0

    @property
    def charge_ratio(self) -> float:
        return self.current_charge_wh / self.capacity_wh

@dataclass
class FlightEdge:
    origin_id: str
    destination_id: str
    distance_km: float
    energy_cost_wh: float
    traversal_time_sec: float
    risk_coefficient: float = 1.0

@dataclass
class Route:
    route_id: str
    ordered_node_ids: List[str]
    total_distance_km: float
    total_energy_wh: float
    estimated_time_seconds: float

@dataclass
class SimulationResult:
    scenario_name: str
    total_orders_processed: int
    successful_deliveries: int
    failed_deliveries: int
    average_wait_time_sec: float
    bottleneck_depot_ids: List[str]

@dataclass
class OptimizationResult:
    algorithm_run: str
    selected_depot_coordinates: List[Tuple[float, float]]
    coverage_percentage: float
    mean_squared_error: float