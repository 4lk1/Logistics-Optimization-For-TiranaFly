import geopandas as gpd
from shapely.geometry import base
from typing import Union, Tuple

class SpatialValidator:
    """
    Handles Coordinate Reference System (CRS) validation and spatial integrity checks.
    Primary CRS: EPSG:4326 (WGS 84) for GeoJSON/H3 compatibility.
    Projected CRS: EPSG:32634 (UTM Zone 34N) for accurate distance and area calculations in Tirana.
    """
    
    WGS84 = "EPSG:4326"
    UTM_TIRANA = "EPSG:32634"

    @staticmethod
    def validate_crs(gdf: gpd.GeoDataFrame, target_crs: str = WGS84) -> bool:
        """Validates if the GeoDataFrame is in the expected CRS."""
        if gdf.crs is None:
            raise ValueError("GeoDataFrame has no CRS defined.")
        return gdf.crs.to_string().upper() == target_crs.upper()

    @staticmethod
    def ensure_crs(gdf: gpd.GeoDataFrame, target_crs: str = WGS84) -> gpd.GeoDataFrame:
        """Ensures the GeoDataFrame is in the target CRS, transforming if necessary."""
        if gdf.crs is None:
            gdf.set_crs(target_crs, inplace=True)
        elif not SpatialValidator.validate_crs(gdf, target_crs):
            gdf = gdf.to_crs(target_crs)
        return gdf

    @staticmethod
    def validate_geometry(geometry: Union[gpd.GeoSeries, base.BaseGeometry]) -> bool:
        """Checks if geometries are valid (no self-intersections, etc.)."""
        if isinstance(geometry, gpd.GeoSeries):
            return geometry.is_valid.all()
        return geometry.is_valid

    @staticmethod
    def check_overlap(gdf: gpd.GeoDataFrame) -> bool:
        """Verifies that administrative units do not overlap significantly."""
        # Simple check: sum of areas should be close to area of union
        # In production, we'd do pairwise intersection checks
        union_area = gdf.unary_union.area
        sum_area = gdf.area.sum()
        # Allow for small floating point differences
        return abs(union_area - sum_area) / union_area < 0.001
