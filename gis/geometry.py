# filename: gis/geometry.py
from shapely.geometry import Polygon, Point, box
from typing import List, Tuple, Dict, Any

class SpatialGeometryEngine:
    @staticmethod
    def compute_polygon_intersection_area(poly1: Polygon, poly2: Polygon) -> float:
        if not poly1.intersects(poly2):
            return 0.0
        return poly1.intersection(poly2).area

    @staticmethod
    def is_point_within_boundary(lat: float, lon: float, polygon: Polygon) -> bool:
        point = Point(lon, lat)
        return polygon.contains(point)

    @staticmethod
    def construct_bounding_box(coords: List[Tuple[float, float]]) -> box:
        lons = [c[1] for c in coords]
        lats = [c[0] for c in coords]
        return box(min(lons), min(lats), max(lons), max(lats))