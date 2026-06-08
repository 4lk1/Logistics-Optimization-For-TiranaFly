# filename: api/routes/population.py
from fastapi import APIRouter
from typing import List, Dict, Any
from main import OFFICIAL_CENSUS_DATA, generate_synthetic_h3_grid_seed
from gis.population_mapper import PopulationMapper

router = APIRouter(tags=["Demographics & Spatial Population Mapping"])

@router.get("/census")
async def get_census_data() -> List[Dict[str, Any]]:
    """Returns official baseline demographics from the 2023 Census."""
    return OFFICIAL_CENSUS_DATA

@router.get("/grid")
async def get_grid_cells() -> List[Dict[str, Any]]:
    """Returns the generated and population-weighted H3-style operational grid cells."""
    mapper = PopulationMapper(target_denominator=807029)
    raw_cells = generate_synthetic_h3_grid_seed()
    cell_matrix = mapper.distribute_population_to_grid(OFFICIAL_CENSUS_DATA, raw_cells)
    return cell_matrix
