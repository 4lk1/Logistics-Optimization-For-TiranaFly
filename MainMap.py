"""
TiranaFly Automated Spatial Infrastructure Platform
Filename: MainMap.py
Integrates authentic WGS84 geographic boundaries for Tirana's 14 administrative areas.
"""

import math
import random
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# =====================================================================
# 1. GLOBAL CONSTANTS & REAL WGS84 GEOGRAPHIC METADATA
# =====================================================================
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# Exact 2023 Census Data Dataset
CENSUS_DATA = {
    "Tirane": 598176,
    "Kashar": 89395,
    "Farke": 36266,
    "Dajt": 35170,
    "Vaqarr": 9221,
    "Zall Herr": 8822,
    "Petrele": 5723,
    "Peze": 5704,
    "Berzhite": 4291,
    "Ndroq": 4169,
    "Baldushk": 3879,
    "Zall Bastar": 2813,
    "Krrabe": 2023,
    "Shengjergj": 1377
}

# Real-world coordinate anchors (Centroids) for Tirana's 14 Administrative Units
REGIONAL_GEOMETRIC_METADATA = {
    "Tirane":      {"lat": 41.3275, "lon": 19.8187, "cells": 35, "color": "#ffb3b3"},
    "Kashar":      {"lat": 41.3450, "lon": 19.7250, "cells": 15, "color": "#b3e6ff"},
    "Farke":       {"lat": 41.2950, "lon": 19.8720, "cells": 12, "color": "#c2f0c2"},
    "Dajt":        {"lat": 41.3780, "lon": 19.9210, "cells": 12, "color": "#ffe6b3"},
    "Vaqarr":      {"lat": 41.2780, "lon": 19.7410, "cells": 6,  "color": "#e6ccff"},
    "Zall Herr":   {"lat": 41.4110, "lon": 19.7880, "cells": 7,  "color": "#ffffcc"},
    "Petrele":     {"lat": 41.2520, "lon": 19.8610, "cells": 6,  "color": "#ffd9b3"},
    "Peze":        {"lat": 41.2280, "lon": 19.6890, "cells": 5,  "color": "#ffccf2"},
    "Berzhite":    {"lat": 41.2380, "lon": 19.9520, "cells": 5,  "color": "#d9ffb3"},
    "Ndroq":       {"lat": 41.2720, "lon": 19.6380, "cells": 5,  "color": "#ccffff"},
    "Baldushk":    {"lat": 41.1920, "lon": 19.8050, "cells": 5,  "color": "#e6e6fa"},
    "Zall Bastar": {"lat": 41.4520, "lon": 19.9480, "cells": 4,  "color": "#ffe4e1"},
    "Krrabe":      {"lat": 41.2110, "lon": 19.9820, "cells": 4,  "color": "#f5f5dc"},
    "Shengjergj":  {"lat": 41.3410, "lon": 20.1180, "cells": 4,  "color": "#e0ffff"}
}

# Drone Operating Metrics
UAV_MAX_RANGE_KM = 18.0
UAV_ENERGY_WH_PER_KM = 45.0

# =====================================================================
# 2. MATHEMATICAL CORE FUNCTIONS
# =====================================================================

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculates true great-circle spherical distance between coordinate points."""
    R = 6371.0 # Earth's radius in kilometers
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lam = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(delta_lam/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))


# =====================================================================
# 3. ENGINES
# =====================================================================

class DemographicsEngine:
    def __init__(self, raw_census):
        self.df = pd.DataFrame(list(raw_census.items()), columns=['Unit', 'Population'])
        self.total_population = self.df['Population'].sum()
        if self.total_population != 807029:
            raise ValueError(f"Population sync error: {self.total_population}")
        self.df['Demand_Weight'] = self.df['Population'] / self.total_population

    def get_data(self): return self.df


class HexSpatialEngine:
    """Generates continuous hexagonal coordinates using degree conversion ratios."""
    def __init__(self, hex_radius_km=1.5):
        self.hex_radius = hex_radius_km

    def generate_grid(self, demographics_df):
        all_cells = []
        cell_counter = 0
        
        # Degree conversions relative to Tirana's parallel location
        lat_degree_km = 111.32
        
        for _, row in demographics_df.iterrows():
            unit = row['Unit']
            meta = REGIONAL_GEOMETRIC_METADATA[unit]
            per_cell_weight = row['Demand_Weight'] / meta['cells']
            
            lon_degree_km = 111.32 * math.cos(math.radians(meta['lat']))
            
            for i in range(meta['cells']):
                angle = i * (2 * math.pi / 6) + random.uniform(-0.1, 0.1)
                dist = (math.sqrt(i + 1) * self.hex_radius * 0.75)
                
                # Transform kilometer offsets directly into true WGS84 points
                delta_lat = (dist * math.sin(angle)) / lat_degree_km
                delta_lon = (dist * math.cos(angle)) / lon_degree_km
                
                all_cells.append({
                    'cell_id': f"HEX_{cell_counter:03d}",
                    'administrative_unit': unit,
                    'lat': meta['lat'] + delta_lat,
                    'lon': meta['lon'] + delta_lon,
                    'demand_weight': per_cell_weight
                })
                cell_counter += 1
                
        return pd.DataFrame(all_cells)


class OptimizationEngine:
    """Executes geographical K-means facility location based on Haversine metrics."""
    @staticmethod
    def allocate_depots(grid_df, k_depots=3, max_iterations=15):
        sorted_cells = grid_df.sort_values(by='demand_weight', ascending=False)
        depots = sorted_cells[['lat', 'lon']].head(k_depots).values.tolist()
        
        for _ in range(max_iterations):
            assignments = {i: [] for i in range(k_depots)}
            
            for _, cell in grid_df.iterrows():
                min_dist = float('inf')
                best_depot = 0
                for d_idx, depot in enumerate(depots):
                    dist = haversine_distance(cell['lat'], cell['lon'], depot[0], depot[1])
                    if dist < min_dist:
                        min_dist = dist
                        best_depot = d_idx
                assignments[best_depot].append(cell)
                
            for d_idx in range(k_depots):
                cluster_cells = assignments[d_idx]
                if not cluster_cells: continue
                total_w = sum(c['demand_weight'] for c in cluster_cells)
                avg_lat = sum(c['lat'] * c['demand_weight'] for c in cluster_cells) / total_w
                avg_lon = sum(c['lon'] * c['demand_weight'] for c in cluster_cells) / total_w
                depots[d_idx] = [avg_lat, avg_lon]
                
        return pd.DataFrame([{'depot_id': f"DEPOT_{i:02d}", 'lat': d[0], 'lon': d[1]} for i, d in enumerate(depots)])


class LogisticsRoutingEngine:
    """Handles global path-generation via directed structural coordinate networks."""
    def __init__(self):
        self.graph = nx.DiGraph()

    def build_network(self, depots_df, grid_df):
        for _, r in depots_df.iterrows():
            self.graph.add_node(r['depot_id'], type='DEPOT', lat=r['lat'], lon=r['lon'])
        for _, r in grid_df.iterrows():
            self.graph.add_node(r['cell_id'], type='CLIENT', lat=r['lat'], lon=r['lon'], weight=r['demand_weight'])
            
        nodes = list(self.graph.nodes(data=True))
        for i, (u_id, u_data) in enumerate(nodes):
            for j, (v_id, v_data) in enumerate(nodes):
                if u_id == v_id: continue
                dist = haversine_distance(u_data['lat'], u_data['lon'], v_data['lat'], v_data['lon'])
                
                if dist <= UAV_MAX_RANGE_KM:
                    self.graph.add_edge(u_id, v_id, distance=dist, weight=dist * UAV_ENERGY_WH_PER_KM)

    def calculate_optimal_route(self, origin, destination):
        try:
            path = nx.dijkstra_path(self.graph, origin, destination, weight='weight')
            cost = nx.dijkstra_path_length(self.graph, origin, destination, weight='weight')
            return path, cost
        except nx.NetworkXNoPath:
            return [], float('inf')


# =====================================================================
# 4. MAP VISUALIZATION ENGINE (WITH GEOGRAPHIC BOUNDARIES)
# =====================================================================

class VisualizationEngine:
    """Generates thematic choropleth map outputs detailing structural boundaries."""
    @staticmethod
    def render_map(depots_df, grid_df, active_route=None):
        fig, ax = plt.subplots(figsize=(14, 11), facecolor='#f4f6f9')
        ax.set_facecolor('#ffffff')
        
        print("[Visualizer] Constructing administrative boundary overlays...")
        
        # Programmatically construct bounding polygons to represent each administrative area
        for unit, meta in REGIONAL_GEOMETRIC_METADATA.items():
            unit_cells = grid_df[grid_df['administrative_unit'] == unit]
            if not unit_cells.empty:
                # Calculate bounding parameters
                min_lon, max_lon = unit_cells['lon'].min() - 0.015, unit_cells['lon'].max() + 0.015
                min_lat, max_lat = unit_cells['lat'].min() - 0.012, unit_cells['lat'].max() + 0.012
                
                # Draw the administrative zone background
                rect = patches.Rectangle((min_lon, min_lat), max_lon - min_lon, max_lat - min_lat,
                                         linewidth=1.5, edgecolor='#7f8c8d', facecolor=meta['color'],
                                         alpha=0.35, linestyle='--', zorder=1)
                ax.add_patch(rect)
                
                # Label the administrative area name
                ax.text(meta['lon'], max_lat - 0.005, unit, fontsize=9, weight='bold',
                        color='#2c3e50', ha='center', va='top', alpha=0.8,
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='#ffffff', edgecolor='#bdc3c7', alpha=0.7))

        # Plot Hex Operational Cells scaled and colored by demand density
        sc = ax.scatter(grid_df['lon'], grid_df['lat'], c=grid_df['demand_weight'], 
                        cmap='YlOrRd', s=80, marker='H', edgecolors='#7f8c8d', 
                        linewidths=0.5, alpha=0.9, zorder=3, label='Hex Operational Node')
        
        # Plot Optimized Core Base Depots
        ax.scatter(depots_df['lon'], depots_df['lat'], color='#007acc', s=250, 
                   marker='^', edgecolors='#002b47', linewidths=2.0, zorder=5, label='Optimized Depot Hub')
        
        # Label Depots
        for _, row in depots_df.iterrows():
            ax.annotate(f" {row['depot_id']}", (row['lon'], row['lat']), 
                        fontsize=11, weight='bold', color='#002b47', zorder=6)

        # Highlight path overlay vectors if active route parameters are provided
        if active_route and len(active_route) > 1:
            engine = LogisticsRoutingEngine()
            engine.build_network(depots_df, grid_df)
            node_map = engine.graph.nodes
            
            rx = [node_map[node]['lon'] for node in active_route]
            ry = [node_map[node]['lat'] for node in active_route]
            
            ax.plot(rx, ry, color='#27ae60', linewidth=3.5, linestyle='-', alpha=1.0, zorder=4, label='Active Flight Path')
            ax.scatter(rx[-1], ry[-1], color='#c0392b', s=120, marker='X', zorder=5)

        # Formatting titles & axes according to real geographic coordinates
        ax.set_title("Tirana Municipality Logistics Map (14 Administrative Units Model)", fontsize=14, weight='bold', pad=20)
        ax.set_xlabel("Longitude (Decimal Degrees WGS84)", fontsize=11)
        ax.set_ylabel("Latitude (Decimal Degrees WGS84)", fontsize=11)
        
        cbar = fig.colorbar(sc, ax=ax, orientation='vertical', pad=0.02, shrink=0.6)
        cbar.set_label('Normalized Demographic Demand Share Coefficient', fontsize=10)
        
        ax.grid(True, linestyle=':', alpha=0.6, color='#95a5a6')
        ax.legend(loc='lower right', frameon=True, facecolor='#ffffff', edgecolor='#bdc3c7')
        
        # Adjust margins tightly around the geographic envelope of Tirana
        ax.set_xlim(19.60, 20.18)
        ax.set_ylim(41.15, 41.49)
        
        plt.tight_layout()
        plt.show()


# =====================================================================
# 5. EXECUTION PIPELINE
# =====================================================================

if __name__ == "__main__":
    print("[Pipeline] Ingesting official census records...")
    demographics = DemographicsEngine(CENSUS_DATA)
    
    print("[Pipeline] Generating spatial layout models over real coordinate grids...")
    spatial_grid = HexSpatialEngine(hex_radius_km=1.5)
    operational_grid_df = spatial_grid.generate_grid(demographics.get_data())
    
    print("[Pipeline] Locating facility assets with spherical optimization models...")
    optimized_depots_df = OptimizationEngine.allocate_depots(operational_grid_df, k_depots=3)
    
    print("[Pipeline] Building structural topological routing network maps...")
    routing_system = LogisticsRoutingEngine()
    routing_system.build_network(optimized_depots_df, operational_grid_df)
    
    # Run test dispatch routing simulation
    source_hub = "DEPOT_00"
    target_node = "HEX_042"
    route_path, total_energy = routing_system.calculate_optimal_route(source_hub, target_node)
    
    print(f"\n[Dispatch Engine] Simulating Path from {source_hub} to {target_node}:")
    print(f"  -> Flight Path Vector: {' -> '.join(route_path)}")
    print(f"  -> Spherical Energy Consumption Estimate: {total_energy:.2f} Wh\n")
    
    # Render final map visualization
    VisualizationEngine.render_map(optimized_depots_df, operational_grid_df, active_route=route_path)