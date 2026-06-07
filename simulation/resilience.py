from typing import List, Dict
from simulation.models import SystemTwin

class ResilienceEngine:
    """Computes resilience and robustness metrics for the system."""
    
    def calculate_metrics(self, system: SystemTwin) -> Dict[str, float]:
        """Calculates multi-dimensional resilience scores."""
        return {
            "network_robustness": self._network_robustness(system),
            "fleet_availability": self._fleet_availability(system),
            "depot_redundancy": self._depot_redundancy(system),
            "overall_resilience_score": self._overall_score(system)
        }

    def _network_robustness(self, system: SystemTwin) -> float:
        total_routes = len(system.network.routes)
        if total_routes == 0: return 0.0
        active_routes = sum(1 for r in system.network.routes if r.is_active)
        # Weight by congestion
        avg_congestion = sum(r.congestion_factor for r in system.network.routes) / total_routes
        return (active_routes / total_routes) * (1.0 / avg_congestion)

    def _fleet_availability(self, system: SystemTwin) -> float:
        total_drones = system.fleet.total_drones
        if total_drones == 0: return 0.0
        available = sum(len(d.get_available_drones()) for d in system.fleet.depots)
        return available / total_drones

    def _depot_redundancy(self, system: SystemTwin) -> float:
        total_depots = len(system.fleet.depots)
        if total_depots == 0: return 0.0
        operational = sum(1 for d in system.fleet.depots if d.is_operational)
        return operational / total_depots

    def _overall_score(self, system: SystemTwin) -> float:
        nr = self._network_robustness(system)
        fa = self._fleet_availability(system)
        dr = self._depot_redundancy(system)
        # Weighted harmonic mean for resilience (penalizes low scores in any dimension)
        if nr == 0 or fa == 0 or dr == 0: return 0.0
        return 3 / (1/nr + 1/fa + 1/dr)
