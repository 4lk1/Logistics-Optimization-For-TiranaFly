import pytest
from simulation.models import SystemTwin, MunicipalityTwin, FleetTwin, NetworkTwin, DepotTwin, DroneTwin
from simulation.simulation_engine import SimulationEngine
from simulation.weather_simulator import WeatherSimulator
from simulation.demand_simulator import DemandSimulator
from schemas.io_models import Depot, Drone, Battery, AdministrativeUnit

@pytest.fixture
def mock_system():
    # Setup a minimal system twin
    unit = AdministrativeUnit(name="TestUnit", population=10000, geojson_polygon={})
    unit_twin = AdministrativeUnitTwin(base=unit)
    municipality = MunicipalityTwin(units=[unit_twin])
    
    depot_base = Depot(depot_id="D1", lat=41.3, lon=19.8, h3_index="883901", max_drone_capacity=10)
    drone_base = Drone(drone_id="DR1")
    battery = Battery(battery_id="B1")
    drone_twin = DroneTwin(base=drone_base, battery=battery, current_lat=41.3, current_lon=19.8)
    
    depot_twin = DepotTwin(base=depot_base, drones=[drone_twin])
    fleet = FleetTwin(depots=[depot_twin])
    network = NetworkTwin(routes=[])
    
    return SystemTwin(municipality=municipality, fleet=fleet, network=network)

def test_weather_simulator():
    sim = WeatherSimulator()
    sim.step()
    impact = sim.get_impact_factors()
    assert "energy_multiplier" in impact
    assert "time_multiplier" in impact

def test_demand_simulator(mock_system):
    sim = DemandSimulator(mock_system.municipality.units)
    requests = sim.generate_step_demand(12.0, 1.0)
    assert isinstance(requests, list)

def test_simulation_engine_run(mock_system):
    engine = SimulationEngine(mock_system)
    kpis = engine.run_simulation(hours=0.1) # Short run
    assert kpis.total_successful_missions + kpis.total_failed_missions >= 0

def test_resilience_calculation(mock_system):
    from simulation.resilience import ResilienceEngine
    engine = ResilienceEngine()
    metrics = engine.calculate_metrics(mock_system)
    assert metrics["overall_resilience_score"] >= 0.0

from simulation.models import AdministrativeUnitTwin # Fix for mock_system if needed
