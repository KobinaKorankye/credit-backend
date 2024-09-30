from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.loans import Loans
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# Schema for the response to map the original Loanee structure
class LoanResponse(BaseModel):
    id: int
    customer_id: Optional[int] = None
    full_name: str
    sex: str
    age: int
    marital_status: str
    income: float
    telephone: str
    foreign_worker: str
    loan_amount: float
    status_of_existing_checking_account: str
    duration_in_months: int
    credit_history: str
    purpose: str
    savings_account_bonds: str
    present_employment_since: str
    installment_rate_in_percentage_of_disposable_income: int
    other_debtors_guarantors: str
    present_residence_since: int
    property: str
    other_installment_plans: str
    housing: str
    number_of_existing_credits_at_this_bank: int
    job: str
    number_of_people_being_liable_to_provide_maintenance_for: int
    outcome: Optional[str] = None  # e.g., 'approved', 'defaulted', 'repaid'
    outcome_date: Optional[datetime] = None  # The date of the loan outcome

    class Config:
        orm_mode = True  # Enable automatic conversion from ORM objects to Pydantic models


@router.get("/", response_model=List[LoanResponse])
def get_loanees(db: Session = Depends(get_db)):
    # Query the Loans table and access related LoanApplications and Customers via relationships
    loans = db.query(Loans).all()

    if not loans:
        raise HTTPException(status_code=404, detail="No loans found")

    # Transform the data to match the LoanResponse structure
    response_data = []
    for loan in loans:
        application = loan.application  # Access related loan application
        customer = application.customer  # Access related customer

        loan_response = LoanResponse(
            id=loan.id,
            customer_id=customer.id,
            full_name=customer.full_name,
            sex=customer.sex,
            age=customer.age,
            marital_status=customer.marital_status,
            income=customer.income,
            telephone=customer.telephone,
            foreign_worker=customer.foreign_worker,
            loan_amount=loan.loan_amount,
            status_of_existing_checking_account=application.status_of_existing_checking_account,
            duration_in_months=loan.duration_in_months,
            credit_history=application.credit_history,
            purpose=application.purpose,
            savings_account_bonds=application.savings_account_bonds,
            present_employment_since=application.present_employment_since,
            installment_rate_in_percentage_of_disposable_income=application.installment_rate_in_percentage_of_disposable_income,
            other_debtors_guarantors=application.other_debtors_guarantors,
            present_residence_since=application.present_residence_since,
            property=application.property,
            other_installment_plans=application.other_installment_plans,
            housing=application.housing,
            number_of_existing_credits_at_this_bank=application.number_of_existing_credits_at_this_bank,
            job=application.job,
            number_of_people_being_liable_to_provide_maintenance_for=application.number_of_people_being_liable_to_provide_maintenance_for,
            outcome=loan.outcome,  # Use loan outcome (e.g., 'approved', 'defaulted', 'repaid')
            outcome_date=loan.outcome_date  # Use loan outcome date
        )

        response_data.append(loan_response)

    return response_data
