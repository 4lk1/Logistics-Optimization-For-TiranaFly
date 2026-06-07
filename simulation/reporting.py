import json
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime

class SimulationReporter:
    """Generates various report formats for simulation and analytics outputs."""
    
    @staticmethod
    def export_to_json(data: Dict[str, Any], file_path: str):
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def export_summary_to_csv(summary: Dict[str, Any], file_path: str):
        """Flat summary export."""
        flat_data = {}
        for metric, stats in summary.items():
            if isinstance(stats, dict):
                for stat_name, val in stats.items():
                    flat_data[f"{metric}_{stat_name}"] = [val]
            else:
                flat_data[metric] = [stats]
        
        df = pd.DataFrame(flat_data)
        df.to_csv(file_path, index=False)

    @staticmethod
    def generate_full_report(scenario_name: str, summary: Dict[str, Any]) -> str:
        """Generates a text-based summary report."""
        report = []
        report.append("=" * 50)
        report.append(f"TiranaFly Simulation Report: {scenario_name}")
        report.append(f"Timestamp: {datetime.now().isoformat()}")
        report.append("=" * 50)
        report.append(f"Total Iterations: {summary.get('total_iterations')}")
        report.append(f"Successful Missions: {summary.get('total_successful_missions_agg')}")
        report.append(f"Failed Missions: {summary.get('total_failed_missions_agg')}")
        report.append("-" * 50)
        
        for metric, stats in summary.items():
            if isinstance(stats, dict) and "mean" in stats:
                report.append(f"{metric:30} | Mean: {stats['mean']:8.2f} | StdDev: {stats['std_dev']:8.2f}")
                
        report.append("=" * 50)
        return "\n".join(report)
