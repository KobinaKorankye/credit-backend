from pydantic import BaseModel
from typing import Optional

class LoaneeBase(BaseModel):
    status_of_existing_checking_account: str
    duration: int
    credit_history: str
    purpose: str
    credit_amount: int
    savings_account_bonds: str
    present_employment_since: str
    installment_rate_in_percentage_of_disposable_income: int
    personal_status_and_sex: str
    other_debtors_guarantors: str
    present_residence_since: int
    property: str
    age: int
    other_installment_plans: str
    housing: str
    number_of_existing_credits_at_this_bank: int
    job: str
    number_of_people_being_liable_to_provide_maintenance_for: int
    telephone: str
    foreign_worker: str
    class_: int
    income: Optional[int] = 3000  # Default value if not provided

class LoaneeCreate(LoaneeBase):
    pass

class LoaneeResponse(LoaneeBase):
    id: int

    class Config:
        orm_mode = True