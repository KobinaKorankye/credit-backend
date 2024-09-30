from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from app.db.database import Base

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)
    purpose = Column(String, nullable=False)
    credit_amount = Column(Integer, nullable=False)

    # New fields for tracking creation and update times
    date_created = Column(DateTime, default=func.now(), nullable=False)
    date_updated = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Field for specifying filter operations
    filters = Column(JSONB, nullable=True)

    # Field for storing array of objects
    eligible_customers = Column(JSONB, nullable=True)
