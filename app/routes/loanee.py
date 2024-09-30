from fastapi import APIRouter, HTTPException, Depends, Request, Response
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db.models.loanee import Loanee
from app.schemas.loanee import LoaneeCreate, LoaneeUpdate, LoaneeResponse

router = APIRouter()

# Route to get all Loanees
@router.get("/", response_model=List[LoaneeResponse])
def get_loanees(db: Session = Depends(get_db)):
    loanees = db.query(Loanee).all()
    return loanees

# Route to create a new Loanee
@router.post("/", response_model=LoaneeResponse, status_code=201)
def create_loanee(loanee_data: LoaneeCreate, db: Session = Depends(get_db)):
    new_loanee = Loanee(**loanee_data.dict())
    db.add(new_loanee)
    db.commit()
    db.refresh(new_loanee)
    return new_loanee

# Route to update an existing Loanee
@router.put("/", response_model=LoaneeResponse)
def update_loanee(loanee_data: LoaneeUpdate, db: Session = Depends(get_db)):
    loanee = db.query(Loanee).filter(Loanee.id == loanee_data.id).first()
    
    if not loanee:
        raise HTTPException(status_code=404, detail="Loanee not found")
    
    # Update fields as necessary (this is just an example)
    if loanee_data.approve is not None:
        loanee.approve = loanee_data.approve
    
    db.commit()
    db.refresh(loanee)
    return loanee

# Route to delete an existing Loanee
@router.delete("/{loanee_id}", response_model=LoaneeResponse)
def delete_loanee(loanee_id: int, db: Session = Depends(get_db)):
    loanee = db.query(Loanee).filter(Loanee.id == loanee_id).first()
    
    if not loanee:
        raise HTTPException(status_code=404, detail="Loanee not found")
    
    db.delete(loanee)
    db.commit()
    return loanee
