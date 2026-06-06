# filename: fleet/battery_optimizer.py
import math

class BatteryConsumptionEngine:
    def __init__(self, empty_mass_kg: float = 9.5, max_payload_kg: float = 5.0, voltage: float = 44.4):
        self.m_empty = empty_mass_kg
        self.m_max_load = max_payload_kg
        self.g = 9.81
        self.v_nominal = voltage
        self.propulsion_efficiency = 0.72

    def calculate_edge_energy_expenditure_wh(self, distance_km: float, payload_kg: float, speed_m_s: float = 15.0) -> float:
        """
        Calculates expected Wh energy consumption using standard aerodynamic momentum theory.
        """
        if payload_kg > self.m_max_load:
            raise ValueError(f"Payload limit breached: {payload_kg}kg exceeds max {self.m_max_load}kg capacity.")
            
        total_mass = self.m_empty + payload_kg
        
        # Power structural thrust requirements equation
        thrust_n = total_mass * self.g
        induced_power_watts = (thrust_n ** 1.5) / math.sqrt(2 * 1.225 * 0.55) # Assumes standard air density & rotor disk area
        profile_power_watts = 0.5 * 1.225 * (speed_m_s ** 3) * 0.02 * 0.4     # Blade drag profile approximation
        
        total_power_watts = (induced_power_watts / self.propulsion_efficiency) + profile_power_watts + 45.0
        duration_hours = (distance_km) / (speed_m_s * 3.6)
        
        return float(total_power_watts * duration_hours)