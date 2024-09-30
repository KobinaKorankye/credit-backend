from sqlalchemy import Column, Integer, String, DateTime, Date, func, event, Numeric, ForeignKey, select
from sqlalchemy.orm import Session
from app.db.database import Base

class Accounts(Base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)  # Foreign key to customers table
    account_number = Column(String(12), unique=True, nullable=False)  # Sequential 12-digit account number
    account_type = Column(String, nullable=False)  # Account type (e.g., 'checking', 'savings')
    balance = Column(Numeric, nullable=False)  # Balance as a Decimal value
    status = Column(String, nullable=False)  # Status of the account ('active', 'inactive', etc.)
    date_created = Column(DateTime, default=func.now(), nullable=False)
    date_updated = Column(DateTime, default=func.now(), nullable=False)

# Event listener to automatically generate a 12-digit account number
@event.listens_for(Accounts, 'before_insert')
def generate_account_number(mapper, connection, target):
    # Use SQLAlchemy's select() method instead of a raw SQL string
    stmt = select(Accounts.account_number).order_by(Accounts.id.desc()).limit(1)
    last_account = connection.execute(stmt).fetchone()

    if last_account and last_account[0]:
        last_account_number = int(last_account[0])
        new_account_number = str(last_account_number + 1).zfill(12)
    else:
        new_account_number = '000000000001'
    
    target.account_number = new_account_number