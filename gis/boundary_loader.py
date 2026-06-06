import geopandas as gpd
import json
import os
from shapely.geometry import shape, Polygon
from .spatial_validation import SpatialValidator

class BoundaryLoader:
    """
    Loads and processes Tirana administrative boundaries.
    Supports GeoJSON and Shapefile formats.
    Ensures correct CRS and geometric validity.
    """

    DEFAULT_PATH = "data/tirana_boundaries.geojson"

    @staticmethod
    def load_boundaries(file_path: str = DEFAULT_PATH) -> gpd.GeoDataFrame:
        """
        Loads boundaries from a file. 
        If file doesn't exist, it can be extended to fetch from a spatial DB or 
        generate representative synthetic boundaries for Tirana.
        """
        if not os.path.exists(file_path):
            # For Phase 1 demonstration, if the file is missing, we return 
            # a representative bounding area for Tirana divided into 14 units.
            return BoundaryLoader._generate_synthetic_tirana()

        gdf = gpd.read_file(file_path)
        gdf = SpatialValidator.ensure_crs(gdf, SpatialValidator.WGS84)
        
        if not SpatialValidator.validate_geometry(gdf):
            # Attempt to fix invalid geometries
            gdf.geometry = gdf.geometry.buffer(0)
            
        return gdf

    @staticmethod
    def _generate_synthetic_tirana() -> gpd.GeoDataFrame:
        """
        Generates 14 representative administrative units for Tirana 
        to ensure the system is functional without external data.
        Centered around 41.3275 N, 19.8189 E.
        """
        from .administrative_units import AdministrativeUnits
        units = AdministrativeUnits.get_all_units()
        
        # Simple grid-based split for representation
        # Tirana Urban center is approx 0.05 x 0.05 degrees
        base_lat, base_lng = 41.3275, 19.8189
        step = 0.01
        
        polygons = []
        for i, name in enumerate(units):
            # Create a small offset polygon for each unit
            row, col = divmod(i, 4)
            minx = base_lng + (col - 2) * step
            maxx = minx + step
            miny = base_lat + (row - 2) * step
            maxy = miny + step
            polygons.append(Polygon([(minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy)]))
            
        gdf = gpd.GeoDataFrame({
            'name': units,
            'unit_type': 'Administrative Unit'
        }, geometry=polygons, crs="EPSG:4326")
        
        return gdf
