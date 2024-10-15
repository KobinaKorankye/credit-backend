from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.database import Base

class Loans(Base):
    __tablename__ = 'loans'

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id', ondelete='CASCADE'), nullable=False)
    application_id = Column(Integer, ForeignKey('loan_applications.id', ondelete='CASCADE'), nullable=False)  # Links to application
    loan_amount = Column(Numeric, nullable=False)
    interest_rate = Column(Numeric, nullable=False)
    duration_in_months = Column(Integer, nullable=False)
    
    # Outcome fields
    outcome = Column(Integer, nullable=True)  # e.g., 'defaulted', 'repaid'
    outcome_date = Column(DateTime, nullable=True)  # Date when the final outcome occurred

    # Timestamps
    date_created = Column(DateTime, default=func.now(), nullable=False)
    date_updated = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    application = relationship("LoanApplications")
    customer = relationship("Customers")
