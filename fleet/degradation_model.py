from .models import Drone, Battery

class DegradationModel:
    """
    Models the physical degradation of UAV components over time.
    """

    @staticmethod
    def calculate_battery_soh(battery: Battery) -> float:
        """
        Predicts State of Health based on cycle count and age.
        Linear degradation model for simplicity.
        """
        cycle_hit = battery.cycle_count * 0.0002
        # Age hit: 1% per month (approx 0.0003 per day)
        # This is a placeholder for actual age calculation
        age_hit = 0.01 
        
        new_soh = max(0.0, 1.0 - (cycle_hit + age_hit))
        return new_soh

    @staticmethod
    def predict_maintenance_need(drone: Drone) -> bool:
        """
        Determines if a drone requires maintenance based on flight hours.
        Threshold: 100 flight hours.
        """
        flight_hours = drone.total_flight_time_s / 3600.0
        # Check time since last maintenance
        # In a real system, we'd compare drone.last_maintenance_timestamp
        
        return flight_hours > 100.0

    @staticmethod
    def apply_environmental_effects(base_capacity: float, temp_c: float) -> float:
        """
        Adjusts battery capacity based on ambient temperature.
        Drones lose efficiency in extreme cold/heat.
        """
        if temp_c < 0:
            # 1% loss per degree below zero
            return base_capacity * (1.0 + (temp_c * 0.01))
        elif temp_c > 35:
            # 0.5% loss per degree above 35
            return base_capacity * (1.0 - ((temp_c - 35) * 0.005))
        return base_capacity
