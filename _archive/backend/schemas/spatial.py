from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any

class SpatialBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class AdministrativeUnitSchema(SpatialBase):
    id: int
    name: str
    population: int
    # GeoJSON representation as dict
    geom: Any

class HexCellSchema(SpatialBase):
    h3_index: str
    population: int
    geom: Any

class DepotSchema(SpatialBase):
    id: str
    name: str
    capacity: int
    geom: Any

class DroneSchema(SpatialBase):
    id: str
    model: str
    status: str
    depot_id: str

class BatterySchema(SpatialBase):
    id: str
    soc: float
    soh: float
    cycle_count: int

class MissionSchema(SpatialBase):
    id: str
    drone_id: str
    status: str
    payload_kg: float

class OptimizationResultSchema(SpatialBase):
    id: int
    method: str
    timestamp: Any
    data: Any
