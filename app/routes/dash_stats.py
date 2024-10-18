from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.dash_stats import DashStats  # Assuming DashStats is in a separate file
from app.schemas.dash_stat import DashStatUpdate, DashStatResponse  # You will create these schemas
from typing import List


router = APIRouter()

# READ - Get all DashStats entries
@router.get("/", response_model=List[DashStatResponse])
def get_dash_stats(db: Session = Depends(get_db)):
    return db.query(DashStats).all()

# READ - Get a specific DashStats entry by ID
@router.get("/{dash_stats_id}", response_model=DashStatResponse)
def get_dash_stats_by_id(dash_stats_id: int, db: Session = Depends(get_db)):
    dash_stats = db.query(DashStats).filter(DashStats.id == dash_stats_id).first()
    if not dash_stats:
        raise HTTPException(status_code=404, detail="DashStats not found")
    return dash_stats

# UPDATE - Update a specific DashStats entry by ID
@router.put("/{dash_stats_id}", response_model=DashStatResponse)
def update_dash_stats(dash_stats_id: int, dash_stats: DashStatUpdate, db: Session = Depends(get_db)):
    db_dash_stats = db.query(DashStats).filter(DashStats.id == dash_stats_id).first()
    
    if not db_dash_stats:
        raise HTTPException(status_code=404, detail="DashStats not found")
    
    # Update the fields if provided
    if dash_stats.name is not None:
        db_dash_stats.name = dash_stats.name
    if dash_stats.start_date is not None:
        db_dash_stats.start_date = dash_stats.start_date
    if dash_stats.end_date is not None:
        db_dash_stats.end_date = dash_stats.end_date
    if dash_stats.processing is not None:
        db_dash_stats.processing = dash_stats.processing
    if dash_stats.stats is not None:
        db_dash_stats.stats = dash_stats.stats

    db.commit()
    db.refresh(db_dash_stats)
    return db_dash_stats

# DELETE - Delete a specific DashStats entry by ID
@router.delete("/{dash_stats_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dash_stats(dash_stats_id: int, db: Session = Depends(get_db)):
    dash_stats = db.query(DashStats).filter(DashStats.id == dash_stats_id).first()
    
    if not dash_stats:
        raise HTTPException(status_code=404, detail="DashStats not found")
    
    db.delete(dash_stats)
    db.commit()
    return {"message": "DashStats deleted successfully"}
