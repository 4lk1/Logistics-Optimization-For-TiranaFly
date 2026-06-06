from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.services.gis_service import GISService
from backend.schemas.spatial import AdministrativeUnitSchema, HexCellSchema
from typing import List

router = APIRouter()

@router.post("/initialize", status_code=201)
def initialize_gis_data(db: Session = Depends(get_db)):
    """Initializes the spatial database with Tirana boundaries and H3 cells."""
    try:
        GISService.initialize_spatial_data(db)
        return {"message": "GIS data initialized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin-units", response_model=List[AdministrativeUnitSchema])
def get_admin_units(db: Session = Depends(get_db)):
    return GISService.get_administrative_units(db)

@router.get("/h3-cells", response_model=List[HexCellSchema])
def get_h3_cells(db: Session = Depends(get_db)):
    return GISService.get_all_hex_cells(db)
