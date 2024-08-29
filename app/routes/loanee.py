from fastapi import APIRouter, HTTPException, Depends, Request, Response
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db.models.loanee import Loanee
from app.db.models.gapplicant import GApplicant
from app.schemas.gapplicant import GApplicantCreate, GApplicantResponse
from app.schemas.loanee import LoaneeResponse

router = APIRouter()

data = {
    "example": "This is example graph data"
}

# Route to get all Loanees
@router.get("/", response_model=List[LoaneeResponse])
def get_loanees(db: Session = Depends(get_db)):
    loanees = db.query(Loanee).all()
    # if not loanees:
    #     raise HTTPException(status_code=500, detail="Internal Server Error")
    return loanees