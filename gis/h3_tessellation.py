import h3
import geopandas as gpd
from shapely.geometry import Polygon, mapping
from typing import List, Set

class H3Tessellator:
    """
    Handles H3 grid generation for spatial indexing and population mapping.
    Uses H3 resolution 8 (approx 0.7 sq km) or 9 (approx 0.1 sq km) for urban delivery.
    """

    @staticmethod
    def get_hexagons(geometry: Polygon, resolution: int = 9) -> List[str]:
        """
        Generates a list of H3 hexagon IDs that cover the given geometry.
        """
        # Convert shapely geometry to GeoJSON-like mapping for H3
        geojson = mapping(geometry)
        
        # H3 polyfill expects coordinates in [[lat, lng], ...] or similar
        # But shapely and GeoJSON use [lng, lat].
        # H3-py v3 uses [lat, lng] for polyfill if it's a simple polygon.
        
        # We'll use a more robust way to handle the polyfill
        # Extract coordinates and ensure they are (lat, lng)
        poly_coords = []
        if geojson['type'] == 'Polygon':
            for ring in geojson['coordinates']:
                poly_coords.append([(lat, lng) for lng, lat in ring])
        
        # Note: h3.polyfill in v3 takes (geojson_dict, res)
        # However, it expects the geojson to have (lat, lng) order in coordinates if not careful.
        # Actually, h3.polyfill(geojson, res) expects GeoJSON (lng, lat)
        
        hexagons = h3.polyfill(geojson, resolution, geo_json_mode=True)
        return list(hexagons)

    @staticmethod
    def hexagons_to_gdf(hex_ids: List[str]) -> gpd.GeoDataFrame:
        """
        Converts a list of H3 hexagon IDs to a GeoDataFrame.
        """
        polygons = []
        for h in hex_ids:
            # h3.h3_to_geo_boundary(h, True) returns (lng, lat)
            boundary = h3.h3_to_geo_boundary(h, geo_json=True)
            polygons.append(Polygon(boundary))
        
        gdf = gpd.GeoDataFrame({'h3_id': hex_ids}, geometry=polygons, crs="EPSG:4326")
        return gdf

    @staticmethod
    def tessellate_gdf(gdf: gpd.GeoDataFrame, resolution: int = 9) -> gpd.GeoDataFrame:
        """
        Tessellates all geometries in a GeoDataFrame into H3 hexagons.
        """
        all_hexes = set()
        for geom in gdf.geometry:
            hexes = H3Tessellator.get_hexagons(geom, resolution)
            all_hexes.update(hexes)
            
        return H3Tessellator.hexagons_to_gdf(list(all_hexes))
