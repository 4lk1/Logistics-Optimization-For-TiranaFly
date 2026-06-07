import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Dict, Any, List
import numpy as np

class SimulationVisualizer:
    """Generates visual representations of simulation results."""
    
    @staticmethod
    def plot_kpi_comparison(comparison_df: pd.DataFrame, metrics: List[str] = None):
        """Plots a bar chart comparing metrics across scenarios."""
        if metrics is None:
            metrics = ["mission_success_rate", "avg_delivery_time_min"]
            
        df_melted = comparison_df.melt(id_vars="Scenario", value_vars=metrics)
        
        plt.figure(figsize=(12, 6))
        sns.barplot(data=df_melted, x="Scenario", y="value", hue="variable")
        plt.title("Scenario KPI Comparison")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_sensitivity(sensitivity_df: pd.DataFrame, param_name: str, metric_name: str):
        """Plots a line chart showing sensitivity of a metric to a parameter."""
        plt.figure(figsize=(10, 5))
        plt.plot(sensitivity_df["ParameterValue"], sensitivity_df["MetricMean"], marker='o')
        plt.title(f"Sensitivity: {metric_name} vs {param_name}")
        plt.xlabel(param_name)
        plt.ylabel(metric_name)
        plt.grid(True)
        plt.show()

    @staticmethod
    def plot_resilience_radar(resilience_metrics: Dict[str, float]):
        """Generates a radar chart for resilience dimensions."""
        labels = list(resilience_metrics.keys())
        values = list(resilience_metrics.values())
        
        num_vars = len(labels)
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        values += values[:1]
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.fill(angles, values, color='red', alpha=0.25)
        ax.plot(angles, values, color='red', linewidth=2)
        ax.set_yticklabels([])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels)
        plt.title("Network Resilience Profile")
        plt.show()
