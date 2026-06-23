# filename: api/routes/gis.py
from fastapi import APIRouter
from typing import List, Dict, Any
import h3
from main import OFFICIAL_CENSUS_DATA, generate_synthetic_h3_grid_seed
from gis.population_mapper import PopulationMapper

router = APIRouter(tags=["GIS Foundation"])

def h3_boundary_polygon(h3_index: str) -> List[List[float]]:
    """Returns one closed GeoJSON polygon ring for an H3 cell."""
    if hasattr(h3, "cell_to_boundary"):
        boundary = [[lng, lat] for lat, lng in h3.cell_to_boundary(h3_index)]
    else:
        boundary = [list(coord) for coord in h3.h3_to_geo_boundary(h3_index, geo_json=True)]

    if boundary and boundary[0] != boundary[-1]:
        boundary.append(boundary[0])

    return boundary

def build_admin_unit_geometry(unit_name: str, cells) -> Dict[str, Any]:
    """Builds separated administrative coverage from H3 cells assigned to a unit."""
    polygons = []
    for cell in cells:
        if cell.assigned_unit == unit_name:
            polygons.append([h3_boundary_polygon(cell.h3_index)])

    return {
        "type": "MultiPolygon",
        "coordinates": polygons,
    }

@router.post("/initialize", status_code=201)
async def initialize_gis_data():
    """No-op initialization for POC."""
    return {"message": "GIS data initialized successfully (Mock)"}

@router.get("/admin-units")
async def get_admin_units() -> List[Dict[str, Any]]:
    """Returns official baseline demographics from the 2023 Census."""
    units = []
    raw_cells = generate_synthetic_h3_grid_seed()
    for idx, item in enumerate(OFFICIAL_CENSUS_DATA):
        units.append({
            "id": idx + 1,
            "name": item["name"],
            "population": item["population"],
            "geom": build_admin_unit_geometry(item["name"], raw_cells),
        })
    return units

@router.get("/h3-cells")
async def get_h3_cells() -> List[Dict[str, Any]]:
    """Returns the generated and population-weighted H3-style operational grid cells."""
    mapper = PopulationMapper(target_denominator=807029)
    raw_cells = generate_synthetic_h3_grid_seed()
    cell_matrix = mapper.distribute_population_to_grid(OFFICIAL_CENSUS_DATA, raw_cells)
    
    results = []
    for cell in cell_matrix:
        results.append({
            "h3_index": cell["h3_index"],
            "population": int(cell["local_demand_coefficient"] * 807029),
            "centroid_lat": cell["centroid_lat"],
            "centroid_lon": cell["centroid_lon"],
            "assigned_unit": cell["assigned_unit"],
            "geom": {
                "type": "Point",
                "coordinates": [cell["centroid_lon"], cell["centroid_lat"]]
            }
        })
    return results
