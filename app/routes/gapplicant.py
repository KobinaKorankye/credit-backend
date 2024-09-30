from fastapi import APIRouter, HTTPException, Depends, Request, Response
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db.models.loanee import Loanee
from app.db.models.gapplicant import GApplicant
from app.schemas.gapplicant import GApplicantCreate, GApplicantUpdate, GApplicantResponse
from app.schemas.loanee import LoaneeResponse

router = APIRouter()

# Route to get all GApplicants
@router.get("/", response_model=List[GApplicantResponse])
def get_gapplicants(db: Session = Depends(get_db)):
    gapplicants = db.query(GApplicant).all()
    # if not gapplicants:
    #     raise HTTPException(status_code=500, detail="Internal Server Error")
    return gapplicants

# Route to create a new GApplicant
@router.post("/", response_model=GApplicantResponse, status_code=201)
def create_gapplicant(gapplicant_data: GApplicantCreate, db: Session = Depends(get_db)):
    new_gapplicant = GApplicant(**gapplicant_data.dict())
    db.add(new_gapplicant)
    db.commit()
    db.refresh(new_gapplicant)
    return new_gapplicant

# Route to update an existing GApplicant
@router.put("/", response_model=GApplicantResponse)
def update_gapplicant(gapplicant_data: GApplicantUpdate, db: Session = Depends(get_db)):
    gapplicant = db.query(GApplicant).filter(GApplicant.id == gapplicant_data.id).first()
    
    if not gapplicant:
        raise HTTPException(status_code=404, detail="GApplicant not found")
    
    if gapplicant_data.approve is not None:
        gapplicant.approve = gapplicant_data.approve
    
    db.commit()
    db.refresh(gapplicant)
    return gapplicant

@router.delete("/{gapplicant_id}", response_model=GApplicantResponse)
def delete_gapplicant(gapplicant_id: int, db: Session = Depends(get_db)):
    gapplicant = db.query(GApplicant).filter(GApplicant.id == gapplicant_id).first()
    
    if not gapplicant:
        raise HTTPException(status_code=404, detail="GApplicant not found")
    
    db.delete(gapplicant)
    db.commit()
