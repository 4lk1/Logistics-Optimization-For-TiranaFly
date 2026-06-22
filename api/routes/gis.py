# filename: api/routes/gis.py
from fastapi import APIRouter
from typing import List, Dict, Any
from main import OFFICIAL_CENSUS_DATA, generate_synthetic_h3_grid_seed
from gis.population_mapper import PopulationMapper

router = APIRouter(tags=["GIS Foundation"])

@router.post("/initialize", status_code=201)
async def initialize_gis_data():
    """No-op initialization for POC."""
    return {"message": "GIS data initialized successfully (Mock)"}

@router.get("/admin-units")
async def get_admin_units() -> List[Dict[str, Any]]:
    """Returns official baseline demographics from the 2023 Census."""
    units = []
    for idx, item in enumerate(OFFICIAL_CENSUS_DATA):
        units.append({
            "id": idx + 1,
            "name": item["name"],
            "population": item["population"],
            "geom": None # Simple POC
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
            "h3_index": cell.h3_index,
            "population": int(cell.local_demand_coefficient * 807029),
            "geom": {
                "type": "Point",
                "coordinates": [cell.centroid_lon, cell.centroid_lat]
            }
        })
    return results
