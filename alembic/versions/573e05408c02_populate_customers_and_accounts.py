"""populate customers and accounts

Revision ID: 573e05408c02
Revises: 5def871818b3
Create Date: 2024-09-19 17:15:58.961189

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.orm import sessionmaker
from faker import Faker
from datetime import datetime
import random
from app.db.models.customers import Customers  # Assuming these models already exist
from app.db.models.accounts import Accounts

revision: str = '573e05408c02'
down_revision: Union[str, None] = '5def871818b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Faker instance to generate random but realistic data
fake = Faker()

# Core logic to generate a random full name with 2 to 4 parts
def generate_random_full_name():
    name_parts = random.randint(2, 4)
    return ' '.join(fake.name().split()[:name_parts])

# Generate random sex ('M' or 'F')
def generate_random_sex():
    return random.choice(['male', 'female'])

# Generate sequential account numbers
def generate_sequential_account_number(last_account_number):
    if last_account_number:
        return str(int(last_account_number) + 1).zfill(12)
    else:
        return '000000000001'

# Generate random foreign worker status ('Y' or 'N')
def generate_random_foreign_worker():
    return random.choice(['Yes', 'No'])

# Generate random status of checking account
def generate_random_account_status():
    return random.choice(['active', 'inactive', 'closed'])

def upgrade():
    bind = op.get_bind()
    Session = sessionmaker(bind=bind)
    session = Session()

    # Get the last account number from the customers table
    result = session.query(Accounts.account_number).order_by(Accounts.id.desc()).first()
    last_account_number = result[0] if result else None

    for i in range(2000):  # Generate 100 random customers
        full_name = generate_random_full_name()

        # Create the customer
        customer = Customers(
            full_name=full_name,
            sex=generate_random_sex(),
            marital_status=random.choice(['single','married', 'separated','divorced']),
            age=random.randint(18, 65),
            email="eacquahh@gmail.com",
            mobile="233201161093",
            income=round(random.uniform(2000.0, 10000.0), 2),
            telephone=random.choice(['Yes, registered', 'None']),
            foreign_worker=generate_random_foreign_worker(),
            date_created=datetime.now(),
            date_updated=datetime.now()
        )
        session.add(customer)
        session.flush()  # Flush here to make sure customer ID is generated

        randomChoice = random.choice([True, False])
        # Add random accounts for each customer
        if randomChoice:
            account_number = generate_sequential_account_number(last_account_number)
            last_account_number = account_number  # Update for the next iteration
            checking_account = Accounts(
                customer_id=customer.id,
                account_number=account_number,
                account_type='checking',
                balance=round(random.uniform(1000.0, 5000.0), 2),
                status=generate_random_account_status(),
                date_created=datetime.now(),
                date_updated=datetime.now()
            )

            session.add(checking_account)
            session.flush()

        if (not randomChoice) or random.choice([True, False]):
            account_number = generate_sequential_account_number(last_account_number)
            last_account_number = account_number  # Update for the next iteration
            savings_account = Accounts(
                customer_id=customer.id,
                account_number=account_number,
                account_type='savings',
                balance=round(random.uniform(1000.0, 5000.0), 2),
                status=generate_random_account_status(),
                date_created=datetime.now(),
                date_updated=datetime.now()
            )

            session.add(savings_account)
            session.flush()

        session.commit()

def downgrade():
    bind = op.get_bind()
    Session = sessionmaker(bind=bind)
    session = Session()

    session.query(Accounts).delete(synchronize_session=False)
    session.query(Customers).delete(synchronize_session=False)
    session.commit()
