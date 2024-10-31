from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.customer import CustomerResponse
from app.schemas.user import ShowUser
from app.db.models import LoanApplications, Customers, Loans, Accounts, Users
from typing import List, Optional, Union
from datetime import datetime
import random

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
    officer_notes: Optional[str] = None
    reviewer_notes: Optional[str] = None
    approver_notes: Optional[str] = None

    # Nested dictionary for customer-related fields (if customer exists)
    customer: Optional[Union[CustomerResponse, dict]] = None
    officer: Optional[Union[ShowUser, dict]] = None
    reviewer: Optional[Union[ShowUser, dict]] = None
    approver: Optional[Union[ShowUser, dict]] = None

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
    elif decision == "review":
        query = query.filter(LoanApplications.decision.contains("review"))
    elif decision == "finalize":
        query = query.filter(LoanApplications.decision.contains("finalize"))

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

        print(application.officer)
        print(type(application.officer))

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
                officer_notes=application.officer_notes,
                reviewer_notes=application.reviewer_notes,
                approver_notes=application.approver_notes,
                customer=customer_data,  # Populate customer field as a dictionary
                officer=ShowUser.from_orm(application.officer) if application.officer else None,
                reviewer=ShowUser.from_orm(application.reviewer) if application.reviewer else None,
                approver=ShowUser.from_orm(application.approver) if application.approver else None,
                nc_info=application.nc_info  # No nc_info when customer exists
            )
        )

    return response_data


from dateutil.parser import parse as parseISO
from dateutil.relativedelta import relativedelta
from datetime import date as dt_date


class LoanApplicationUpdate(BaseModel):
    loan_amount_requested: Optional[float] = None
    duration_in_months: Optional[int] = None
    status_of_existing_checking_account: Optional[str] = None
    credit_history: Optional[str] = None
    purpose: Optional[str] = None
    savings_account_bonds: Optional[str] = None
    present_employment_since: Optional[str] = None
    installment_rate_in_percentage_of_disposable_income: Optional[int] = None
    other_debtors_guarantors: Optional[str] = None
    present_residence_since: Optional[int] = None
    property: Optional[str] = None
    other_installment_plans: Optional[str] = None
    housing: Optional[str] = None
    number_of_existing_credits_at_this_bank: Optional[int] = None
    job: Optional[str] = None
    number_of_people_being_liable_to_provide_maintenance_for: Optional[int] = None
    decision: Optional[str] = None  # 'approved' or 'rejected'
    decision_date: Optional[datetime] = None
    user_id: Optional[int] = None
    officer_notes: Optional[str] = None
    reviewer_notes: Optional[str] = None
    approver_notes: Optional[str] = None

    class Config:
        orm_mode = True


@router.put("/decision/{loan_application_id}", response_model=LoanApplicationResponse)
async def update_loan_application(
    loan_application_id: int,
    application_data: LoanApplicationUpdate,
    db: Session = Depends(get_db)
):
    # Start a transaction
    try:
        # Fetch the existing loan application by id
        application = db.query(LoanApplications).filter(LoanApplications.id == loan_application_id).first()

        # If the application is not found, raise a 404 error
        if not application:
            raise HTTPException(status_code=404, detail="Loan application not found")
        
        # If the decision is rejected, just update the decision-related fields
        if application_data.decision == 'finalize-approve' or application_data.decision == 'finalize-reject':
            application.decision = application_data.decision
            application.reviewer_id = application_data.user_id
            if application_data.reviewer_notes is not None:
                application.reviewer_notes = application_data.reviewer_notes

            # Commit the changes for rejection
            db.commit()
            db.refresh(application)
            return application
        elif application_data.decision == 'review-approve' or application_data.decision == 'review-reject':
            application.decision = application_data.decision
            application.officer_id = application_data.user_id
            if application_data.officer_notes is not None:
                application.officer_notes = application_data.officer_notes

            # Commit the changes for rejection
            db.commit()
            db.refresh(application)
            return application
        # If the decision is rejected, just update the decision-related fields
        elif application_data.decision == 'rejected':
            application.decision = application_data.decision
            application.decision_date = datetime.now()
            application.approver_id = application_data.user_id

            if application_data.approver_notes is not None:
                application.approver_notes = application_data.approver_notes

            # Commit the changes for rejection
            db.commit()
            db.refresh(application)
            return application

        # If the decision is approved
        elif application_data.decision == 'approved':
            application.decision = application_data.decision
            application.decision_date = datetime.now()
            application.approver_id = application_data.user_id
            if application_data.approver_notes is not None:
                application.approver_notes = application_data.approver_notes

            if application.customer_id is None:
                # Create a new customer from nc_info
                nc_info = application.nc_info
                new_customer = Customers(
                    full_name=nc_info['full_name'],
                    sex=nc_info['sex'],
                    age=nc_info['age'],
                    marital_status=nc_info['marital_status'],
                    income=nc_info.get('income', 3000),
                    telephone=nc_info['telephone'],
                    email=nc_info.get('email', 'eacquahh@gmail.com'),
                    mobile=nc_info.get('mobile', '233201161093'),
                    foreign_worker=nc_info['foreign_worker'],
                )
                db.add(new_customer)
                db.flush()  # Ensure the customer ID is generated but not committed

                # Update the loan application's customer_id and clear nc_info
                application.customer_id = new_customer.id
                application.nc_info = None

            # Create a new loan for the customer
            interest_rate = random.uniform(3.0, 10.0)  # Random interest rate between 3% and 10%
            new_loan = Loans(
                customer_id=application.customer_id,
                application_id=application.id,
                loan_amount=application.loan_amount_requested,
                interest_rate=interest_rate,
                duration_in_months=application.duration_in_months,
            )
            db.add(new_loan)
            db.flush()  # Ensure the loan is prepared but not committed

            # Create a new checking account for the customer
            new_account = Accounts(
                customer_id=application.customer_id,
                account_type='checking',
                balance=application.loan_amount_requested,  # Disburse the loan amount into the balance
                status='active'
            )
            db.add(new_account)

            # Commit all changes if everything is successful
            db.commit()
            db.refresh(application)

            return application

        else:
            raise HTTPException(status_code=400, detail="Invalid decision")

    except Exception as e:
        db.rollback()  # Roll back in case of any error
        print(e)
        raise HTTPException(status_code=500, detail="An error occurred during processing")


@router.put("/{loan_application_id}", response_model=LoanApplicationResponse)
async def update_loan_application(
    loan_application_id: int,
    application_data: LoanApplicationUpdate,
    db: Session = Depends(get_db)
):
    # Fetch the existing loan application by id
    application = db.query(LoanApplications).filter(LoanApplications.id == loan_application_id).first()

    # If the application is not found, raise a 404 error
    if not application:
        raise HTTPException(status_code=404, detail="Loan application not found")

    # Update only the fields that are provided in the request
    for key, value in application_data.dict(exclude_unset=True).items():
        setattr(application, key, value)

    # Commit the changes to the database
    db.commit()
    db.refresh(application)  # Refresh the instance with the updated data

    return application

@router.get("/filter-loan-applications-by-date", response_model=List[LoanApplicationResponse])
async def filter_loan_applications_by_date(
    filterType: Optional[str] = Query("all"),
    date: Optional[dt_date] = Query(None),
    startDate: Optional[dt_date] = Query(None),
    endDate: Optional[dt_date] = Query(None),
    db: Session = Depends(get_db)
):
    # Base query
    query = db.query(LoanApplications)
    
    if filterType == 'all':
        # No filtering, return all applications
        results = query.all()

    elif filterType == 'today':
        # Filter for today
        results = query.filter(LoanApplications.date_created == dt_date.today()).all()

    elif filterType == 'week':
        # Filter for current week (Monday to Sunday)
        today = dt_date.today()
        start_of_week = today - relativedelta(weekday=0)  # Monday
        results = query.filter(LoanApplications.date_created >= start_of_week).all()

    elif filterType == 'month':
        # Filter for current month
        today = dt_date.today()
        first_of_month = today.replace(day=1)
        results = query.filter(LoanApplications.date_created >= first_of_month).all()

    elif filterType == 'year':
        # Filter for current year
        today = dt_date.today()
        first_of_year = today.replace(month=1, day=1)
        results = query.filter(LoanApplications.date_created >= first_of_year).all()

    elif filterType == 'date' and date:
        # Filter for a specific date
        results = query.filter(LoanApplications.date_created == date).all()

    elif filterType == 'date_range' and startDate and endDate:
        # Filter for a date range
        results = query.filter(LoanApplications.date_created.between(startDate, endDate)).all()

    else:
        raise HTTPException(status_code=400, detail="Invalid filter_type or missing date information")

    return results
