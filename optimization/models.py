from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import numpy as np

@dataclass(frozen=True)
class DepotCandidate:
    """Represents a potential location for a drone depot."""
    id: str
    lat: float
    lng: float
    fixed_cost: float = 50000.0
    capacity: int = 1000
    h3_index: Optional[str] = None

@dataclass(frozen=True)
class DemandAssignment:
    """Represents the assignment of a demand cell to a specific depot."""
    h3_id: str
    depot_id: str
    distance: float
    population_served: int

@dataclass(frozen=True)
class CoverageZone:
    """Represents the service area of a depot."""
    depot_id: str
    assigned_h3_ids: List[str]
    total_population: int
    avg_distance: float
    max_distance: float

@dataclass(frozen=True)
class OptimizationResult:
    """Summary of an optimization run."""
    method_name: str
    depots: List[DepotCandidate]
    assignments: List[DemandAssignment]
    total_population_served: int
    total_cost: float
    avg_distance: float
    max_distance: float
    runtime_sec: float
    metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class OptimizationConfig:
    """Configuration for multi-objective optimization."""
    alpha_coverage: float = 0.4  # Weight for population coverage
    beta_cost: float = 0.3      # Weight for infrastructure cost
    gamma_distance: float = 0.2  # Weight for average distance
    delta_equity: float = 0.1    # Weight for service fairness (min-max)
    max_depots: int = 10
    service_radius_m: float = 5000.0
    total_population: int = 807029
