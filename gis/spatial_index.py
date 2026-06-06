# filename: gis/spatial_index.py
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
from typing import List, Dict, Any, Optional

class SpatialIndexEngine:
    def __init__(self):
        self.gdf: Optional[gpd.GeoDataFrame] = None

    def build_index(self, records: List[Dict[str, Any]], lat_col: str = "lat", lon_col: str = "lon") -> None:
        df = pd.DataFrame(records)
        geometry = [Point(xy) for xy in zip(df[lon_col], df[lat_col])]
        self.gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
        # Force build of spatial index (R-Tree via PyGEOS/Shapely internals)
        self.gdf.sindex

    def query_nearest(self, target_lat: float, target_lon: float, max_items: int = 1) -> gpd.GeoDataFrame:
        if self.gdf is None or self.gdf.empty:
            raise ValueError("Spatial index layer not initialized.")
        target_pt = Point(target_lon, target_lat)
        nearest_geom = self.gdf.sindex.nearest(target_pt, return_all=False, max_distance=None)
        return self.gdf.iloc[nearest_geom[1]]