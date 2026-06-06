import unittest
import datetime
from fleet.models import Drone, Battery, DroneStatus, DepotFleet, FlightMission
from fleet.demand_forecaster import DemandForecaster
from fleet.queue_models import QueueingModels
from fleet.fleet_allocator import FleetAllocator
from fleet.battery_manager import BatteryManager
from fleet.drone_scheduler import DroneScheduler
from fleet.dispatch_engine import DispatchEngine

class TestFleetEngine(unittest.TestCase):

    def setUp(self):
        self.h3_pop = {"h1": 5000, "h2": 10000}
        self.forecaster = DemandForecaster(self.h3_pop)
        self.allocator = FleetAllocator(service_rate_per_drone=2.0)
        self.battery_manager = BatteryManager()
        self.scheduler = DroneScheduler(self.battery_manager)
        self.dispatch = DispatchEngine(self.scheduler, self.battery_manager)
        
        # Setup mock fleet
        self.battery = Battery(capacity_kwh=1.5, current_charge_kwh=1.5)
        self.drone = Drone(id="drone_1", status=DroneStatus.AVAILABLE, battery=self.battery)
        self.fleet = DepotFleet(depot_id="depot_A", drones=[self.drone])

    def test_demand_forecast(self):
        dt = datetime.datetime(2026, 6, 12, 19, 0) # Friday 7PM
        demand = self.forecaster.predict_demand("h2", dt)
        self.assertGreater(demand, 0)
        self.assertGreater(self.forecaster.get_total_expected_demand(dt), 0)

    def test_queue_models(self):
        # M/M/1
        metrics = QueueingModels.mm1_model(1.5, 2.0)
        self.assertTrue(metrics["stable"])
        self.assertEqual(metrics["rho"], 0.75)
        
        # M/M/c
        metrics_c = QueueingModels.mmc_model(3.0, 2.0, 2)
        self.assertTrue(metrics_c["stable"])
        self.assertEqual(metrics_c["rho"], 0.75)

    def test_fleet_allocation(self):
        # 10 orders/hour, service rate 2/h per drone
        needed = self.allocator.calculate_required_fleet(10.0, target_wait_time_s=600.0)
        self.assertGreater(needed, 5) # Must be > rho=1 threshold

    def test_dispatch_workflow(self):
        # Valid dispatch
        mission = self.dispatch.dispatch_order(self.fleet, "h1", 5000, 1.0)
        self.assertIsNotNone(mission)
        self.assertEqual(self.drone.status, DroneStatus.EN_ROUTE)
        
        # Complete mission
        self.dispatch.complete_mission(self.fleet, mission.id)
        self.assertEqual(self.drone.status, DroneStatus.AVAILABLE)
        self.assertLess(self.drone.battery.current_charge_kwh, 1.5)

    def test_battery_swaps(self):
        low_battery = Battery(current_charge_kwh=0.1)
        self.drone.battery = low_battery
        
        full_battery = Battery(current_charge_kwh=1.5)
        swaps = self.battery_manager.schedule_swaps([self.drone], [full_battery])
        self.assertIn(self.drone.id, swaps)
        self.assertEqual(swaps[self.drone.id], full_battery.id)

if __name__ == '__main__':
    unittest.main()
