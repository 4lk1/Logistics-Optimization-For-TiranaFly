# filename: main.py
import logging
import h3
from schemas.io_models import HexCell, Depot
from gis.population_mapper import PopulationMapper
from optimization.depot_selector import DepotLocationOptimizer
from fleet.fleet_allocator import FleetAllocationEngine
from graph.graph_builder import FlightGraphBuilder
from graph.graph_pruner import NetworkTopologyPruner
from simulation.simulator import TiranaFlyStochasticSimulationEngine
from visualization.maps import LogisticsMapVisualizer
from gis.coordinate_utils import (
    TIRANA_MAX_LAT,
    TIRANA_MAX_LON,
    TIRANA_MIN_LAT,
    TIRANA_MIN_LON,
    haversine_distance,
    validate_tirana_bounds,
)
from optimization.facility_location import FacilityLocationComparativeHarness
from fleet.queue_models import DepotQueueEngine
from fleet.battery_optimizer import BatteryConsumptionEngine
from typing import List

logging.basicConfig(level=logging.INFO, format="[%(asctime)s - %(levelname)s] %(message)s")

# Official Census 2023 Population Data (MANDATORY BASLINE)
OFFICIAL_CENSUS_DATA = [
    {"name": "Tirane", "population": 598176},
    {"name": "Kashar", "population": 89395},
    {"name": "Dajt", "population": 35170},
    {"name": "Farke", "population": 36266},
    {"name": "Petrele", "population": 5723},
    {"name": "Vaqarr", "population": 9221},
    {"name": "Peze", "population": 5704},
    {"name": "Ndroq", "population": 4169},
    {"name": "Baldushk", "population": 3879},
    {"name": "Berzhite", "population": 4291},
    {"name": "Krrabe", "population": 2023},
    {"name": "Zall Bastar", "population": 2813},
    {"name": "Zall Herr", "population": 8822},
    {"name": "Shengjergj", "population": 1377}
]

# Total Population P = 807,029
MUNICIPALITY_TOTAL_POPULATION = 807029
H3_GRID_RESOLUTION = 8

ADMIN_UNIT_ANCHORS = {
    "Tirane": (41.3275, 19.8187),
    "Kashar": (41.3450, 19.7250),
    "Farke": (41.2950, 19.8720),
    "Dajt": (41.3780, 19.9210),
    "Vaqarr": (41.2780, 19.7410),
    "Zall Herr": (41.4110, 19.7880),
    "Petrele": (41.2520, 19.8610),
    "Peze": (41.2280, 19.6890),
    "Berzhite": (41.2380, 19.9520),
    "Ndroq": (41.2720, 19.6380),
    "Baldushk": (41.1920, 19.8050),
    "Zall Bastar": (41.4520, 19.9480),
    "Krrabe": (41.2110, 19.9820),
    "Shengjergj": (41.3410, 20.1180),
}

def lat_lon_to_h3(lat: float, lon: float, resolution: int) -> str:
    """Support both h3-py v3 and v4 naming."""
    if hasattr(h3, "latlng_to_cell"):
        return h3.latlng_to_cell(lat, lon, resolution)
    return h3.geo_to_h3(lat, lon, resolution)

def h3_to_lat_lon(h3_index: str) -> tuple[float, float]:
    """Support both h3-py v3 and v4 naming."""
    if hasattr(h3, "cell_to_latlng"):
        return h3.cell_to_latlng(h3_index)
    return h3.h3_to_geo(h3_index)

def nearest_admin_unit(lat: float, lon: float) -> str:
    """Assign a generated H3 cell to the nearest census anchor."""
    return min(
        ADMIN_UNIT_ANCHORS,
        key=lambda name: haversine_distance(lat, lon, *ADMIN_UNIT_ANCHORS[name]),
    )

def generate_synthetic_h3_grid_seed() -> List[HexCell]:
    """Generates full H3 coverage across Tirana's operational bounding box."""
    cells = []
    hexes = set()
    lat_step = 0.006
    lon_step = 0.008

    lat = TIRANA_MIN_LAT
    while lat <= TIRANA_MAX_LAT:
        lon = TIRANA_MIN_LON
        while lon <= TIRANA_MAX_LON:
            hexes.add(lat_lon_to_h3(lat, lon, H3_GRID_RESOLUTION))
            lon += lon_step
        lat += lat_step

    for h3_str in sorted(hexes):
        cell_lat, cell_lon = h3_to_lat_lon(h3_str)
        if not validate_tirana_bounds(cell_lat, cell_lon):
            continue

        cells.append(HexCell(
            h3_index=h3_str,
            centroid_lat=cell_lat,
            centroid_lon=cell_lon,
            boundary_coordinates=[],
            assigned_unit=nearest_admin_unit(cell_lat, cell_lon),
        ))
    return cells

def execute_production_pipeline():
    logging.info("------------------------------------------------------------------------")
    logging.info("             TIRANAFLY LOGISTICS INFRASTRUCTURE GENERATION ENGINE       ")
    logging.info("------------------------------------------------------------------------")
    
    # 1. Load census demographics and verify structural invariants
    mapper = PopulationMapper(target_denominator=MUNICIPALITY_TOTAL_POPULATION)
    raw_cells = generate_synthetic_h3_grid_seed()
    cell_matrix = mapper.distribute_population_to_grid(OFFICIAL_CENSUS_DATA, raw_cells)
    
    # 2. Run facility location optimization to select depot hubs
    optimizer = DepotLocationOptimizer(target_hubs=3)
    centroid_coords = optimizer.execute_weighted_kmeans(raw_cells)
    
    depots = []
    for idx, (lat, lon) in enumerate(centroid_coords):
        depots.append(Depot(
            depot_id=f"DEPOT_{idx:02d}", lat=lat, lon=lon,
            h3_index=f"881e263ad00000{idx}", max_drone_capacity=30
        ))
    logging.info(f"Facility allocation optimization converged successfully. Selected {len(depots)} hub centroids.")

    # 3. Balance fleet distributions using regional queueing models
    depots = FleetAllocationEngine.balance_fleet_distribution(depots, raw_cells, base_fleet_pool=65)
    
    # 4. Construct the topology graph and prune paths that exceed drone range limits
    builder = FlightGraphBuilder()
    base_graph = builder.construct_base_topology(depots, raw_cells)
    
    pruner = NetworkTopologyPruner(max_range_km=24.0, power_coeff_wh_km=45.0)
    flight_network = pruner.prune_and_weight_edges(base_graph)
    logging.info(f"Topological edge pruning complete. Active corridors: {flight_network.number_of_edges()}")

    # 5. Run a stochastic simulation to analyze network performance
    simulator = TiranaFlyStochasticSimulationEngine(depots, raw_cells, flight_network)
    sim_kpis = simulator.execute_stochastic_run(iterations=250)
    
    print("\n=======================================================================")
    print("                     SYSTEM PRODUCTION STATUS OVERVIEW                 ")
    print("=======================================================================")
    print(f"  -> Total Regional Inhabitants Processed : {mapper.denominator} Inhabitants")
    print(f"  -> Total Edge Corridor Network Paths    : {flight_network.number_of_edges()} Lines")
    print(f"  -> Simulated Flights Executed           : {sim_kpis['total_orders_processed']} Sorties")
    print(f"  -> Automated Delivery Success Rate      : {sim_kpis['system_delivery_success_rate']:.2f} %")
    print(f"  -> Average System Turnaround Duration   : {sim_kpis['average_delivery_wait_time_sec']:.2f} Sec")
    print("=======================================================================\n")

    # 6. Export visualization maps to file storage
    LogisticsMapVisualizer.render_static_map_grid(depots, raw_cells)
    logging.info("Pipeline processing cycle complete. Network layouts saved to local disk storage.")

if __name__ == "__main__":
    execute_production_pipeline()
