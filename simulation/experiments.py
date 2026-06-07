from typing import Dict, Any, List
from simulation.monte_carlo import MonteCarloEngine
from simulation.scenario_manager import ScenarioManager
from simulation.models import SystemTwin
from simulation.reporting import SimulationReporter
from simulation.analytics import SimulationAnalytics

class ExperimentRunner:
    """Orchestrates high-level experiments and comparisons."""
    
    def __init__(self, system_twin: SystemTwin):
        self.system = system_twin
        self.mc_engine = MonteCarloEngine(system_twin)

    def run_experiment_suite(self, scenario_keys: List[str], iterations: int = 10) -> Dict[str, Any]:
        """Runs a set of scenarios and returns comparative analysis."""
        results = {}
        for key in scenario_keys:
            print(f"Running Scenario: {key}...")
            config = ScenarioManager.get_scenario(key)
            results[key] = self.mc_engine.run_monte_carlo(
                iterations=iterations, 
                hours=24.0, 
                scenario_config=config
            )
        
        comparison_df = SimulationAnalytics.compare_scenarios(results)
        return {
            "individual_results": results,
            "comparison_table": comparison_df
        }

    def run_stress_test(self, load_multipliers: List[float], iterations: int = 5) -> Dict[float, Any]:
        """Runs the same baseline scenario with increasing load."""
        variations = {}
        for mult in load_multipliers:
            print(f"Stress Test - Load Multiplier: {mult}")
            config = ScenarioManager.get_scenario("baseline").copy()
            config["global_multiplier"] = mult
            variations[mult] = self.mc_engine.run_monte_carlo(
                iterations=iterations,
                hours=12.0,
                scenario_config=config
            )
            
        return variations
