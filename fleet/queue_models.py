import numpy as np
from typing import Dict, Any

class QueueingModels:
    """
    Implements analytical models for depot operations and waiting times.
    """

    @staticmethod
    def mm1_model(arrival_rate: float, service_rate: float) -> Dict[str, float]:
        """
        M/M/1 Queue: Poisson arrivals, exponential service, single drone.
        """
        if arrival_rate >= service_rate:
            return {"rho": arrival_rate/service_rate, "stable": False}
        
        rho = arrival_rate / service_rate
        l = rho / (1 - rho)
        lq = rho**2 / (1 - rho)
        w = 1 / (service_rate - arrival_rate)
        wq = rho / (service_rate - arrival_rate)
        
        return {
            "rho": rho,
            "L": l, "Lq": lq,
            "W": w, "Wq": wq,
            "stable": True
        }

    @staticmethod
    def mmc_model(arrival_rate: float, service_rate: float, c: int) -> Dict[str, float]:
        """
        M/M/c Queue: Poisson arrivals, exponential service, c drones.
        """
        rho = arrival_rate / (c * service_rate)
        
        if rho >= 1:
            return {"rho": rho, "stable": False}
        
        # Calculate P0 (probability of 0 in system)
        sum_p0 = sum([(arrival_rate/service_rate)**n / np.math.factorial(n) for n in range(c)])
        sum_p0 += ((arrival_rate/service_rate)**c / (np.math.factorial(c) * (1 - rho)))
        p0 = 1 / sum_p0
        
        # Lq (Expected number of customers in queue)
        lq = (p0 * (arrival_rate/service_rate)**c * rho) / (np.math.factorial(c) * (1 - rho)**2)
        
        # Wq, W, L
        wq = lq / arrival_rate
        w = wq + (1 / service_rate)
        l = arrival_rate * w
        
        # Probability of waiting
        p_wait = (p0 * (arrival_rate/service_rate)**c) / (np.math.factorial(c) * (1 - rho))
        
        return {
            "rho": rho,
            "L": l, "Lq": lq,
            "W": w, "Wq": wq,
            "P_wait": p_wait,
            "stable": True
        }

    @staticmethod
    def mg1_model(arrival_rate: float, service_rate: float, service_std: float) -> Dict[str, float]:
        """
        M/G/1 Queue: General service distribution (e.g., constant or uniform flight times).
        """
        rho = arrival_rate / service_rate
        if rho >= 1:
            return {"rho": rho, "stable": False}
            
        # Pollaczek-Khinchine formula
        lq = (arrival_rate**2 * (1/service_rate**2 + service_std**2)) / (2 * (1 - rho))
        wq = lq / arrival_rate
        w = wq + (1 / service_rate)
        l = arrival_rate * w
        
        return {
            "rho": rho,
            "L": l, "Lq": lq,
            "W": w, "Wq": wq,
            "stable": True
        }
