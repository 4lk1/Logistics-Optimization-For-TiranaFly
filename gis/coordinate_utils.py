# filename: gis/coordinate_utils.py
import math
from typing import Tuple, List

# Tirana Municipality Geographic Bounding Box Invariants
TIRANA_MIN_LAT = 41.1500
TIRANA_MAX_LAT = 41.5000
TIRANA_MIN_LON = 19.6000
TIRANA_MAX_LON = 20.2000

def validate_tirana_bounds(lat: float, lon: float) -> bool:
    """Enforces spatial guardrails to prevent out-of-boundary routing."""
    return (TIRANA_MIN_LAT <= lat <= TIRANA_MAX_LAT) and (TIRANA_MIN_LON <= lon <= TIRANA_MAX_LON)

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes great-circle distance between two geodetic coordinate points in kilometers.
    """
    if not (validate_tirana_bounds(lat1, lon1) and validate_tirana_bounds(lat2, lon2)):
        # Log a warning in production, but allow calculation for boundary-spanning paths
        pass

    R = 6371.0  # Mean Earth radius in kilometers
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2) ** 2 + 
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates navigation bearings for drone telemetry dispatch tracking."""
    lat1_rad, lat2_rad = math.radians(lat1), math.radians(lat2)
    delta_lon = math.radians(lon2 - lon1)
    
    y = math.sin(delta_lon) * math.cos(lat2_rad)
    x = (math.cos(lat1_rad) * math.sin(lat2_rad) - 
         math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon))
    
    brng = math.atan2(y, x)
    return (math.degrees(brng) + 360) % 360