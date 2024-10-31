from sqlalchemy import Column, Integer, String, DateTime, func
from app.db.database import Base

class Loanee(Base):
    __tablename__ = 'loanees'

    id = Column(Integer, primary_key=True, index=True)
    status_of_existing_checking_account = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)
    credit_history = Column(String, nullable=False)
    purpose = Column(String, nullable=False)
    credit_amount = Column(Integer, nullable=False)
    savings_account_bonds = Column(String, nullable=False)
    present_employment_since = Column(String, nullable=False)
    installment_rate_in_percentage_of_disposable_income = Column(Integer, nullable=False)
    personal_status_and_sex = Column(String, nullable=False)
    other_debtors_guarantors = Column(String, nullable=False)
    present_residence_since = Column(Integer, nullable=False)
    property = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    other_installment_plans = Column(String, nullable=False)
    housing = Column(String, nullable=False)
    number_of_existing_credits_at_this_bank = Column(Integer, nullable=False)
    job = Column(String, nullable=False)
    number_of_people_being_liable_to_provide_maintenance_for = Column(Integer, nullable=False)
    telephone = Column(String, nullable=False)
    foreign_worker = Column(String, nullable=False)
    class_ = Column(Integer, nullable=False)  # Avoid using `class` as it's a reserved keyword
    income = Column(Integer, default=3000)  # Default value

    
    # New fields for tracking creation and update times
    # date_created = Column(DateTime, default=func.now(), nullable=False)
    # date_updated = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
