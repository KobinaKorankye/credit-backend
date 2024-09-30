from sqlalchemy import Column, Integer, String, DateTime, Date, func, event, Numeric, select
from sqlalchemy.orm import Session

from app.db.database import Base

class Customers(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    sex = Column(String, nullable=False)  # 'M' or 'F'
    age = Column(Integer, nullable=False)
    marital_status = Column(String, nullable=False)
    income = Column(Numeric, default=3000)  # Decimal income value
    telephone = Column(String, nullable=False)
    foreign_worker = Column(String, nullable=False)  # 'Y' or 'N'
    date_created = Column(DateTime, default=func.now(), nullable=False)
    date_updated = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

# # Event listener to automatically generate a 12-digit account number
# @event.listens_for(Customers, 'before_insert')
# def generate_account_number(mapper, connection, target):
#     # Use SQLAlchemy's select() method instead of a raw SQL string
#     stmt = select(Customers.account_number).order_by(Customers.id.desc()).limit(1)
#     last_customer = connection.execute(stmt).fetchone()

#     if last_customer and last_customer[0]:
#         last_account_number = int(last_customer[0])
#         new_account_number = str(last_account_number + 1).zfill(12)
#     else:
#         new_account_number = '000000000001'
    
#     target.account_number = new_account_number
