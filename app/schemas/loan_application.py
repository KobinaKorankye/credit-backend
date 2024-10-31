from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from typing import List, Optional
from datetime import datetime

class LoanApplicationBase(BaseModel):
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
        

class LoanApplicationCreate(LoanApplicationBase):
    pass

class LoanApplicationUpdate(LoanApplicationBase):
    id: int