from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.services.optimization_service import OptimizationService
from backend.schemas.spatial import OptimizationResultSchema
from typing import List

router = APIRouter()

@router.post("/run", response_model=OptimizationResultSchema)
def run_optimization(max_depots: int = 10, db: Session = Depends(get_db)):
    """Triggers the full depot placement optimization engine."""
    try:
        result = OptimizationService.run_full_optimization(db, max_depots)
        # We need to fetch the DB model to return it as schema
        return OptimizationService.get_latest_result(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/latest", response_model=OptimizationResultSchema)
def get_latest_optimization(db: Session = Depends(get_db)):
    result = OptimizationService.get_latest_result(db)
    if not result:
        raise HTTPException(status_code=404, detail="No optimization results found")
    return result
