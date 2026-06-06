from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.services.fleet_service import FleetService
from backend.schemas.spatial import DroneSchema
from typing import List

router = APIRouter()

@router.get("/status", response_model=List[DroneSchema])
def get_fleet_status(db: Session = Depends(get_db)):
    return FleetService.get_fleet_status(db)

@router.post("/initialize/{depot_id}")
def initialize_fleet(depot_id: str, num_drones: int = 5, db: Session = Depends(get_db)):
    success = FleetService.initialize_fleet(db, depot_id, num_drones)
    if not success:
        raise HTTPException(status_code=404, detail="Depot not found")
    return {"message": f"Initialized {num_drones} drones at depot {depot_id}"}
