from typing import List, Dict
from simulation.models import NetworkTwin, RouteTwin

class RouteStressTester:
    """Analyzes and applies stress factors to the flight network."""
    
    def __init__(self, saturation_threshold: int = 15):
        self.saturation_threshold = saturation_threshold

    def update_network_stress(self, network: NetworkTwin):
        for route in network.routes:
            # Apply dynamic congestion based on traffic
            self._apply_congestion(route)
            
            # Check for route failure due to weather or airspace restrictions
            if network.global_weather_impact > 1.8:
                route.is_active = False
            else:
                route.is_active = True

    def _apply_congestion(self, route: RouteTwin):
        """Congestion increases non-linearly as drones approach threshold."""
        if route.active_drones == 0:
            route.congestion_factor = 1.0
            return

        ratio = route.active_drones / self.saturation_threshold
        if ratio > 1.0:
            route.congestion_factor = 5.0  # Extreme delay
            route.is_active = False
        else:
            route.congestion_factor = 1.0 + (ratio ** 2) * 2.0

    def get_bottleneck_routes(self, network: NetworkTwin) -> List[RouteTwin]:
        return [r for r in network.routes if r.congestion_factor > 2.0]
