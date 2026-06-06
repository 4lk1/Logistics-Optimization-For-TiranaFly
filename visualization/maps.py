# filename: visualization/maps.py
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import List, Optional
import pandas as pd
from schemas.io_models import Depot, HexCell

class LogisticsMapVisualizer:
    @staticmethod
    def render_static_map_grid(depots: List[Depot], cells: List[HexCell], active_path: Optional[List[str]] = None) -> None:
        fig, ax = plt.subplots(figsize=(12, 10), facecolor="#f5f6fa")
        ax.set_facecolor("#ffffff")
        
        # Plot the background cell matrices
        lons = [c.centroid_lon for c in cells]
        lats = [c.centroid_lat for c in cells]
        weights = [c.local_demand_coefficient for c in cells]
        
        sc = ax.scatter(
            lons, lats, c=weights, cmap="YlOrRd", s=70, 
            marker="H", edgecolors="#2f3640", alpha=0.85, zorder=3,
            label="Hex Demand Center"
        )
        
        # Plot the selected depot centers
        d_lons = [d.lon for d in depots]
        d_lats = [d.lat for d in depots]
        ax.scatter(
            d_lons, d_lats, color="#00a8ff", s=220, 
            marker="^", edgecolors="#192a56", linewidths=2.0, zorder=5,
            label="Optimized Base Depot"
        )
        
        # Overlay annotations onto the layout
        for d in depots:
            ax.annotate(
                f" {d.depot_id} (Fleet={d.assigned_fleet_size})", 
                (d.lon, d.lat), fontsize=9, weight="bold", color="#192a56", zorder=6
            )
            
        ax.set_title("TiranaFly Spatial Infrastructure Map Layer (Dual-Layer Core Model Grid Layout)", fontsize=12, weight="bold")
        ax.set_xlabel("Longitude (Degrees WGS84)")
        ax.set_ylabel("Latitude (Degrees WGS84)")
        
        cbar = fig.colorbar(sc, ax=ax, shrink=0.6)
        cbar.set_label("Normalized Administrative Population Weight Scaling")
        
        ax.grid(True, linestyle=":", alpha=0.6, color="#718093")
        ax.legend(loc="lower right")
        
        # Zoom map into Tirana's geographic bounding box
        ax.set_xlim(19.60, 20.20)
        ax.set_ylim(41.15, 41.50)
        
        plt.tight_layout()
        plt.savefig("tiranafly_network_layout.png", dpi=300)
        plt.close()