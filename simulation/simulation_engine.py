import random
from typing import List, Dict, Any, Optional
from simulation.models import SystemTwin, DroneTwin, DepotTwin, RouteTwin
from simulation.weather_simulator import WeatherSimulator
from simulation.demand_simulator import DemandSimulator
from simulation.depot_failure import DepotFailureSimulator
from simulation.battery_failure import BatteryFailureSimulator
from simulation.route_stress import RouteStressTester
from simulation.kpi_engine import KPIEngine, SimulationKPIs

class SimulationEngine:
    """The central orchestrator for the TiranaFly Digital Twin simulation."""
    
    def __init__(self, system_twin: SystemTwin):
        self.system = system_twin
        self.weather_sim = WeatherSimulator()
        self.demand_sim = DemandSimulator(self.system.municipality.units)
        self.depot_failure_sim = DepotFailureSimulator()
        self.battery_failure_sim = BatteryFailureSimulator()
        self.route_stress_tester = RouteStressTester()
        self.kpi_engine = KPIEngine()
        
        self.active_missions: List[Dict[str, Any]] = []

    def run_simulation(self, hours: float = 24.0, scenario_config: Dict[str, Any] = None) -> SimulationKPIs:
        """Runs the simulation for a specified duration."""
        self.kpi_engine.reset()
        total_steps = int((hours * 3600) / self.system.tick_rate_sec)
        tick_hr = self.system.tick_rate_sec / 3600.0

        for step in range(total_steps):
            sim_hour = (self.system.simulation_clock / 3600.0) % 24
            
            # 1. Update Environment
            self.weather_sim.step()
            impact = self.weather_sim.get_impact_factors()
            self.system.network.global_weather_impact = impact["energy_multiplier"]

            # 2. Simulate Demand
            new_requests = self.demand_sim.generate_step_demand(sim_hour, tick_hr, scenario_config)
            self._dispatch_missions(new_requests)

            # 3. Simulate Failures
            self.depot_failure_sim.apply_failures(self.system.fleet.depots)
            all_drones = [drone for depot in self.system.fleet.depots for drone in depot.drones]
            self.battery_failure_sim.simulate_degradation(all_drones)

            # 4. Update Network Stress
            self.route_stress_tester.update_network_stress(self.system.network)

            # 5. Move Drones & Process Missions
            self._update_missions(self.system.tick_rate_sec, impact)

            # 6. Record Metrics
            self._record_step_metrics(all_drones)

            # Advance clock
            self.system.step()

        return self.kpi_engine.finalize()

    def _dispatch_missions(self, requests: List[Dict[str, Any]]):
        for req in requests:
            # Find closest operational depot with available drone
            assigned = False
            for depot in self.system.fleet.depots:
                if not depot.is_operational: continue
                
                available_drones = depot.get_available_drones()
                if available_drones:
                    drone = available_drones[0]
                    drone.status = "EN_ROUTE"
                    
                    # Create mission
                    mission = {
                        "drone": drone,
                        "depot": depot,
                        "target_unit_id": req["unit_id"],
                        "remaining_dist_km": random.uniform(2.0, 8.0), # Simplified
                        "energy_cost_wh_km": drone.base.empty_mass_kg * 1.2, # Simplified
                        "start_time": self.system.simulation_clock
                    }
                    self.active_missions.append(mission)
                    assigned = True
                    break
            
            if not assigned:
                self.kpi_engine.record_mission_failure()

    def _update_missions(self, tick_sec: float, weather_impact: Dict[str, Any]):
        completed = []
        for mission in self.active_missions:
            drone = mission["drone"]
            
            # Speed in km/s (baseline 60 km/h = 0.016 km/s)
            speed = (60.0 / 3600.0) / weather_impact["time_multiplier"]
            dist_moved = speed * tick_sec
            
            mission["remaining_dist_km"] -= dist_moved
            energy_used = dist_moved * mission["energy_cost_wh_km"] * weather_impact["energy_multiplier"]
            drone.consume_energy(energy_used)
            drone.update_position(drone.current_lat, drone.current_lon, dist_moved)

            if drone.battery.charge_ratio < 0.1:
                drone.status = "OUT_OF_SERVICE"
                self.kpi_engine.record_mission_failure()
                completed.append(mission)
            elif mission["remaining_dist_km"] <= 0:
                drone.status = "IDLE"
                drone.missions_completed += 1
                duration_min = (self.system.simulation_clock - mission["start_time"]) / 60.0
                self.kpi_engine.record_mission_success(duration_min, energy_used / 1000.0)
                completed.append(mission)

        for m in completed:
            self.active_missions.remove(m)

    def _record_step_metrics(self, all_drones: List[DroneTwin]):
        if not all_drones: return
        utilization = sum(1 for d in all_drones if d.status == "EN_ROUTE") / len(all_drones)
        avg_health = sum(d.health_index for d in all_drones) / len(all_drones)
        self.kpi_engine.record_fleet_state(utilization * 100, avg_health * 100)
