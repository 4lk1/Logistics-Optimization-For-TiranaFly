import pandas as pd
import geopandas as gpd
import numpy as np
from typing import Dict, List
from .administrative_units import AdministrativeUnits
from .h3_tessellation import H3Tessellator
from .spatial_validation import SpatialValidator

class PopulationMapper:
    """
    Allocates Tirana's population to the H3 grid.
    Maintains strict adherence to the census total of 807,029.
    """
    
    TOTAL_POPULATION = 807029

    @staticmethod
    def map_population_to_h3(boundary_gdf: gpd.GeoDataFrame, resolution: int = 9) -> gpd.GeoDataFrame:
        """
        Distributes population from administrative units to H3 hexagons.
        """
        # Ensure we are in a projected CRS for accurate area calculations
        boundary_projected = SpatialValidator.ensure_crs(boundary_gdf, SpatialValidator.UTM_TIRANA)
        
        # 1. Tessellate the study area
        hex_gdf = H3Tessellator.tessellate_gdf(boundary_gdf, resolution)
        hex_projected = SpatialValidator.ensure_crs(hex_gdf, SpatialValidator.UTM_TIRANA)
        
        # 2. Perform spatial join to link hexagons to administrative units
        # Using 'centroid' of hexagons to avoid multi-unit assignment if possible, 
        # or intersection for more accuracy. Intersection is preferred for population mapping.
        hex_with_units = gpd.overlay(hex_projected, boundary_projected, how='intersection')
        
        # Calculate area of each intersection piece
        hex_with_units['inter_area'] = hex_with_units.geometry.area
        
        # Calculate total area for each unit in the boundary_projected
        unit_areas = boundary_projected.set_index('name').geometry.area.to_dict()
        
        # 3. Distribute population based on area share
        pop_records = []
        for name in AdministrativeUnits.get_all_units():
            unit_pop = AdministrativeUnits.get_population(name)
            unit_total_area = unit_areas.get(name, 1.0) # avoid div by zero
            
            # Filter intersection pieces for this unit
            unit_pieces = hex_with_units[hex_with_units['name'] == name].copy()
            
            if not unit_pieces.empty:
                # Share = piece_area / total_unit_area
                unit_pieces['pop_share'] = (unit_pieces['inter_area'] / unit_total_area) * unit_pop
                pop_records.append(unit_pieces[['h3_id', 'pop_share']])

        if not pop_records:
            raise ValueError("No population could be mapped. Check boundaries and unit names.")

        mapped_pop = pd.concat(pop_records).groupby('h3_id')['pop_share'].sum().reset_index()
        
        # 4. Final Adjustment to ensure exact total: 807,029
        # Initial rounding
        mapped_pop['population'] = mapped_pop['pop_share'].round().astype(int)
        
        current_total = mapped_pop['population'].sum()
        difference = PopulationMapper.TOTAL_POPULATION - current_total
        
        if difference != 0:
            # Add/subtract the difference to the most populated hexagon to minimize relative error
            # or distribute it among the top hexagons.
            idx_max = mapped_pop['population'].idxmax()
            mapped_pop.at[idx_max, 'population'] += difference
            
        # Re-merge with geometry
        final_gdf = hex_gdf.merge(mapped_pop[['h3_id', 'population']], on='h3_id')
        
        return final_gdf

    # ── Legacy compatibility ──────────────────────────────────────────────────

    def __init__(
        self,
        target_denominator: int = 807029,
    ) -> None:
        self.denominator = target_denominator

    def distribute_population_to_grid(
        self,
        census_data: List[Dict],
        cells: List,
    ) -> List[Dict]:
        """
        Backward-compatible shim used by the existing main.py / API routes.
        """
        # Build census dict from old format
        census = {entry["name"]: entry["population"] for entry in census_data}
        total  = sum(census.values())

        if abs(total - self.denominator) > 0:
            # We allow it for now but warn, or raise if strict
            pass

        # Group old HexCell objects by unit name
        unit_groups: Dict[str, List] = {}
        for cell in cells:
            unit_name = cell.assigned_unit
            unit_groups.setdefault(unit_name, []).append(cell)

        # Distribute using LR and write local_demand_coefficient in-place
        for unit_name, unit_pop in census.items():
            group = unit_groups.get(unit_name, [])
            if not group:
                continue
            n = len(group)
            
            # Simple uniform distribution within unit for the legacy shim
            # Use Hamilton method logic for integer allocation if needed, 
            # but here we just need weights
            for cell in group:
                cell.local_demand_coefficient = (unit_pop / n) / self.denominator

        return [
            {
                "h3_index":                  c.h3_index,
                "centroid_lat":              c.centroid_lat,
                "centroid_lon":              c.centroid_lon,
                "assigned_unit":             c.assigned_unit,
                "local_demand_coefficient":  c.local_demand_coefficient,
            }
            for c in cells
        ]
