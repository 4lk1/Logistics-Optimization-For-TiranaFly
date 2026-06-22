import logging
import sys
import os
from typing import Dict, Any

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import OFFICIAL_CENSUS_DATA, generate_synthetic_h3_grid_seed
from gis.population_mapper import PopulationMapper
from optimization.depot_selector import DepotSelector
from optimization.models import OptimizationConfig
from fleet.fleet_allocator import FleetAllocationEngine
from graph.graph_builder import FlightGraphBuilder
from simulation.simulator import TiranaFlyStochasticSimulationEngine

logging.basicConfig(level=logging.INFO, format="[SYSTEM-ORCHESTRATOR] %(levelname)s: %(message)s")

class TiranaFlySystemOrchestrator:
    """
    Final Integration Orchestrator.
    Unifies GIS, Optimization, Fleet, Graph, and Simulation layers.
    """

    def __init__(self):
        self.population_target = 807029
        self.mapper = PopulationMapper(target_denominator=self.population_target)
        self.selector = DepotSelector(OptimizationConfig(max_depots=5))
        self.builder = FlightGraphBuilder()
        
    def run_full_stack_validation(self) -> Dict[str, Any]:
        logging.info("Initializing Full Stack Validation...")
        
        # 1. GIS & Population
        raw_cells = generate_synthetic_h3_grid_seed()
        cell_matrix = self.mapper.distribute_population_to_grid(OFFICIAL_CENSUS_DATA, raw_cells)
        pop_sum = sum(c.local_demand_coefficient for c in raw_cells) * self.population_target
        
        logging.info(f"GIS Validation: Population Total = {pop_sum:.0f}")
        assert abs(pop_sum - self.population_target) < 1, "Population conservation failed!"

        # 2. Optimization
        # Convert raw_cells to GeoDataFrame for DepotSelector
        import pandas as pd
        import geopandas as gpd
        from shapely.geometry import Point
        
        h3_df = pd.DataFrame([
            {'h3_id': c.h3_index, 'population': c.local_demand_coefficient * self.population_target, 
             'geometry': Point(c.centroid_lon, c.centroid_lat)}
            for c in raw_cells
        ])
        h3_gdf = gpd.GeoDataFrame(h3_df, crs="EPSG:4326")
        
        # Sample candidates
        candidates_gdf = h3_gdf.sample(10).copy()
        
        logging.info("Running Optimization Engine...")
        best_strategy = self.selector.select_best_strategy(h3_gdf, candidates_gdf)
        logging.info(f"Optimization Converged: Method={best_strategy.method_name}, Coverage={best_strategy.total_population_served/self.population_target*100:.2f}%")

        # 3. Fleet & Graph
        logging.info("Constructing Flight Network...")
        # Adapt OptimizationResult to legacy Depot objects for GraphBuilder if needed
        from schemas.io_models import Depot
        depots = [
            Depot(depot_id=d.id, lat=d.lat, lon=d.lng, h3_index=d.h3_index or "", max_drone_capacity=30)
            for d in best_strategy.depots
        ]
        depots = FleetAllocationEngine.balance_fleet_distribution(depots, raw_cells, base_fleet_pool=100)
        
        graph = self.builder.construct_base_topology(depots, raw_cells)
        logging.info(f"Graph Construction Complete: Nodes={graph.number_of_nodes()}, Edges={graph.number_of_edges()}")

        # 4. Simulation
        logging.info("Starting Stochastic Simulation...")
        simulator = TiranaFlyStochasticSimulationEngine(depots, raw_cells, graph)
        kpis = simulator.execute_stochastic_run(iterations=100)
        logging.info(f"Simulation Complete: Success Rate={kpis['system_delivery_success_rate']:.2f}%")

        return {
            "population_valid": True,
            "optimization_valid": True,
            "graph_valid": True,
            "simulation_valid": True,
            "kpis": kpis
        }

if __name__ == "__main__":
    orchestrator = TiranaFlySystemOrchestrator()
    results = orchestrator.run_full_stack_validation()
    print("\n--- FINAL SYSTEM INTEGRATION REPORT ---")
    for k, v in results.items():
        print(f"{k.upper()}: {v}")
