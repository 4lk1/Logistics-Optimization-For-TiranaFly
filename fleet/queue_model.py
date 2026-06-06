# filename: fleet/queue_model.py
import math
from typing import Dict, Any

class DepotQueueEngine:
    @staticmethod
    def calculate_mmc_metrics(lambda_arrival: float, mu_service: float, c_drones: int) -> Dict[str, float]:
        """
        Computes analytical performance metrics for a birth-death queueing model.
        
        lambda_arrival: Mean order arrival rate (orders/hour)
        mu_service: Mean turnaround delivery rate per drone (deliveries/hour)
        c_drones: Available active drone count at the target depot hub
        """
        if c_drones <= 0:
            return {"utilization_ratio": float('inf'), "expected_wait_time_min": float('inf'), "system_stable": 0.0}
            
        rho = lambda_arrival / (c_drones * mu_service)
        
        if rho >= 1.0:
            return {
                "utilization_ratio": rho,
                "average_queue_length": float('inf'),
                "expected_wait_time_min": float('inf'),
                "system_stable": 0.0
            }
            
        # Calculate system idle state probability (P_0)
        sum_terms = sum([(lambda_arrival / mu_service)**n / math.factorial(n) for n in range(c_drones)])
        tail_term = ((lambda_arrival / mu_service)**c_drones / (math.factorial(c_drones) * (1 - rho)))
        p0 = 1.0 / (sum_terms + tail_term)
        
        # Determine expected queue length (L_q) via Erlang-C derivation components
        lq = (p0 * ((lambda_arrival / mu_service)**c_drones) * rho) / (math.factorial(c_drones) * ((1 - rho)**2))
        wq = lq / lambda_arrival  # Wait time in hours via Little's Law
        
        return {
            "utilization_ratio": rho,
            "average_queue_length": lq,
            "expected_wait_time_min": wq * 60.0,  # Converted to minutes
            "system_stable": 1.0
        }