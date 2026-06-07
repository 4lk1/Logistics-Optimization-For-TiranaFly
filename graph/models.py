from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any
from uuid import UUID, uuid4
import h3

@dataclass(frozen=True)
class BaseGraphNode:
    """Base class for all graph vertices."""
    id: str = field(default_factory=lambda: str(uuid4()))
    lat: float = 0.0
    lng: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class H3Node(BaseGraphNode):
    """Represents a hexagonal H3 cell vertex."""
    h3_index: str = ""
    population: int = 0
    
    def __post_init__(self):
        if not self.h3_index:
            raise ValueError("h3_index is required for H3Node")
        # Validate H3 index
        if not h3.is_valid_cell(self.h3_index):
            raise ValueError(f"Invalid H3 index: {self.h3_index}")

@dataclass(frozen=True)
class DepotNode(BaseGraphNode):
    """Represents a drone launch/recharge facility."""
    capacity: int = 0
    recharge_rate: float = 0.0  # units/hour

@dataclass(frozen=True)
class DemandNode(BaseGraphNode):
    """Represents a specific delivery destination or customer location."""
    priority: int = 1
    demand_volume: float = 0.0

@dataclass(frozen=True)
class WaypointNode(BaseGraphNode):
    """Represents an intermediate routing point or airspace corridor marker."""
    altitude_agl: float = 120.0

@dataclass(frozen=True)
class BaseEdge:
    """Base class for all graph edges."""
    origin: str
    destination: str
    distance: float  # meters
    flight_time: float  # seconds
    energy_cost: float  # kWh
    risk_score: float  # 0.0 to 1.0
    weather_penalty: float = 1.0  # multiplier
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class FlightEdge(BaseEdge):
    """General flight path between two nodes."""
    pass

@dataclass(frozen=True)
class NeighborEdge(BaseEdge):
    """Connection between adjacent H3 cells."""
    pass

@dataclass(frozen=True)
class DepotConnection(BaseEdge):
    """Connection between a Depot and the H3 network."""
    pass

@dataclass(frozen=True)
class ServiceEdge(BaseEdge):
    """Edge representing a service action (e.g., delivery, pickup)."""
    service_time: float = 0.0

@dataclass
class GraphWeightConfig:
    """Configurable weights for the cost function w(i,j)."""
    alpha_distance: float = 0.4
    beta_time: float = 0.3
    gamma_energy: float = 0.2
    delta_risk: float = 0.1

    def calculate_weight(self, edge: BaseEdge) -> float:
        """
        Calculates w(i,j) = alpha*dist + beta*time + gamma*energy + delta*risk.
        Applies weather_penalty to the final score.
        """
        raw_weight = (
            self.alpha_distance * edge.distance +
            self.beta_time * edge.flight_time +
            self.gamma_energy * edge.energy_cost +
            self.delta_risk * edge.risk_score
        )
        return raw_weight * edge.weather_penalty
