from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.loan_applications import LoanApplications
from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel

router = APIRouter()

# Response schema with customer as a nested dictionary
class LoanApplicationResponse(BaseModel):
    id: int
    loan_amount_requested: float
    duration_in_months: int
    status_of_existing_checking_account: str
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
    decision: Optional[str] = None # 'approved' or 'rejected'
    decision_date: Optional[datetime] = None
    notes: Optional[str] = None

    # Nested dictionary for customer-related fields (if customer exists)
    customer: Optional[dict] = None

    # nc_info-related fields (non-customer info if customer is null)
    nc_info: Optional[dict] = None

    class Config:
        orm_mode = True


@router.get("", response_model=List[LoanApplicationResponse])
def get_loan_applications(
    db: Session = Depends(get_db),
    decision: Optional[str] = Query(
        None,
        description="Filter loan applications by decision status. Can be 'approved', 'rejected', 'pending', or 'processed'."
    )
):
    # Base query
    query = db.query(LoanApplications)
    
    # Filter based on the query param
    if decision == "approved":
        query = query.filter(LoanApplications.decision == "approved")
    elif decision == "rejected":
        query = query.filter(LoanApplications.decision == "rejected")
    elif decision == "pending":
        query = query.filter(LoanApplications.decision.is_(None))
    elif decision == "processed":
        query = query.filter(LoanApplications.decision.is_not(None))

    loan_applications = query.all()

    response_data = []
    for application in loan_applications:
        customer = application.customer

        # Populate customer as a nested dictionary
        customer_data = {
            "id": customer.id,
            "full_name": customer.full_name,
            "sex": customer.sex,
            "age": customer.age,
            "marital_status": customer.marital_status,
            "telephone": customer.telephone,
            "foreign_worker": customer.foreign_worker,
            "income": customer.income,
        } if customer else None

        # Append the loan application data to the response
        response_data.append(
            LoanApplicationResponse(
                id=application.id,
                customer_id=application.customer_id,
                loan_amount_requested=application.loan_amount_requested,
                duration_in_months=application.duration_in_months,
                status_of_existing_checking_account=application.status_of_existing_checking_account,
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
                decision=application.decision,
                decision_date=application.decision_date,
                notes=application.notes,
                customer=customer_data,  # Populate customer field as a dictionary
                nc_info=application.nc_info  # No nc_info when customer exists
            )
        )

    return response_data
