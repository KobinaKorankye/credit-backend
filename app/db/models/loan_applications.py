from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.db.database import Base

class LoanApplications(Base):
    __tablename__ = 'loan_applications'

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)
    
    # Decision fields
    decision = Column(String, nullable=True)  # 'approved' or 'rejected'
    decision_date = Column(DateTime, nullable=True)  # Date when the decision was made
    notes = Column(String, nullable=True)  # Approval or rejection notes

    # Additional fields from the Loanee table

    # These fields may be altered in the actual loan
    duration_in_months = Column(Integer, nullable=False)
    loan_amount_requested = Column(Numeric, nullable=False)
    
    # The others
    status_of_existing_checking_account = Column(String, nullable=False)
    credit_history = Column(String, nullable=False)
    purpose = Column(String, nullable=False)
    savings_account_bonds = Column(String, nullable=False)
    present_employment_since = Column(String, nullable=False)
    installment_rate_in_percentage_of_disposable_income = Column(Integer, nullable=False)
    other_debtors_guarantors = Column(String, nullable=False)
    present_residence_since = Column(Integer, nullable=False)
    property = Column(String, nullable=False)
    other_installment_plans = Column(String, nullable=False)
    housing = Column(String, nullable=False)
    number_of_existing_credits_at_this_bank = Column(Integer, nullable=False)
    job = Column(String, nullable=False)
    number_of_people_being_liable_to_provide_maintenance_for = Column(Integer, nullable=False)

    # The possibly redundant ones to take care of non-customers
    nc_info = Column(JSONB, nullable=True)

    # # The below fields will be captured in the nc_info
    # full_name = Column(String, nullable=False)
    # age = Column(Integer, nullable=False)
    # sex = Column(String, nullable=False)
    # marital_status = Column(String, nullable=False)
    # telephone = Column(String, nullable=False)
    # foreign_worker = Column(String, nullable=False)
    # income = Column(Integer, default=3000)

    # Timestamps
    date_created = Column(DateTime, default=func.now(), nullable=False)
    date_updated = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship with the customer (if needed)
    customer = relationship("Customers")
