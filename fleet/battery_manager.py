import time
from typing import List, Dict, Optional
from .models import Battery, Drone, DroneStatus

class BatteryManager:
    """
    Manages battery lifecycles, charging queues, and energy estimation.
    """

    def __init__(self, charge_rate_kwh_h: float = 1.0):
        self.charge_rate = charge_rate_kwh_h

    def estimate_energy_usage(self, distance_km: float, payload_kg: float, wind_speed_mps: float = 0.0) -> float:
        """
        Calculates expected energy consumption.
        E = (base_drag + payload_weight_penalty + wind_drag) * dist
        """
        # Coefficients based on TiranaFly-V1 specs
        alpha = 0.05 # kWh/km base
        beta = 0.01  # kWh/km/kg payload
        gamma = 0.005 # kWh/km/(m/s) wind
        
        return (alpha + beta * payload_kg + gamma * wind_speed_mps) * distance_km

    def update_battery_after_flight(self, battery: Battery, energy_used_kwh: float):
        """Updates battery state after a mission."""
        battery.current_charge_kwh = max(0, battery.current_charge_kwh - energy_used_kwh)
        # SOH degradation: small hit per discharge
        battery.state_of_health -= 0.00005 * (energy_used_kwh / battery.capacity_kwh)
        if battery.current_charge_kwh < 0.1 * battery.capacity_kwh:
            battery.cycle_count += 1

    def charge_battery(self, battery: Battery, duration_h: float):
        """Simulates charging process."""
        charge_added = self.charge_rate * duration_h
        battery.current_charge_kwh = min(battery.capacity_kwh * battery.state_of_health, 
                                          battery.current_charge_kwh + charge_added)
        battery.last_charged = time.time()

    def get_swappable_battery(self, batteries: List[Battery], min_soc: float = 0.9) -> Optional[Battery]:
        """Finds the best available battery for a new mission."""
        best_battery = None
        max_soc = -1.0
        
        for b in batteries:
            if b.soc > min_soc and b.soc > max_soc:
                max_soc = b.soc
                best_battery = b
                
        return best_battery

    def schedule_swaps(self, drones: List[Drone], available_batteries: List[Battery]) -> Dict[str, str]:
        """
        Matches low-battery drones with fully charged batteries.
        Returns a map of drone_id -> battery_id.
        """
        swaps = {}
        # Drones needing swap
        needing_swap = [d for d in drones if d.battery and d.battery.soc < 0.2]
        # Ready batteries
        ready_batteries = sorted([b for b in available_batteries if b.soc > 0.9], 
                                 key=lambda x: x.soc, reverse=True)
        
        for drone in needing_swap:
            if ready_batteries:
                battery = ready_batteries.pop(0)
                swaps[drone.id] = battery.id
                
        return swaps
