"""populate new tables with loanees csv

Revision ID: 4fb5decd63a1
Revises: 7275cb7186b5
Create Date: 2024-09-25 08:03:44.063011

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from faker import Faker
import csv
from app.constants import mapping, marital_status_sex_decoder
from datetime import datetime
import random
from app.db.models.customers import Customers  # Assuming these models already exist
from app.db.models.accounts import Accounts
from app.db.models.loan_applications import LoanApplications
from app.db.models.loans import Loans

# revision identifiers, used by Alembic.
revision: str = '4fb5decd63a1'
down_revision: Union[str, None] = '7275cb7186b5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

fake = Faker()

# Core logic to generate a random full name with 2 to 4 parts
def generate_random_full_name():
    name_parts = random.randint(2, 4)
    return ' '.join(fake.name().split()[:name_parts])

def generate_random_date(start_year=2020, end_year=2024):
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31, 23, 59, 59)  # End of 2024
    return start_date + (end_date - start_date) * random.random()

def upgrade() -> None:
    bind = op.get_bind()
    Session = sessionmaker(bind=bind)
    session = Session()

    # Function to load data into Customers, LoanApplications, and Loans tables
    def split_loanee_data(csv_file):
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Create new customer entry with random name using Faker
                marital_status_sex = marital_status_sex_decoder(row['personal_status_and_sex'])
                customer = Customers(
                    full_name=generate_random_full_name(),  # Randomly generated name
                    sex=marital_status_sex['sex'],  # Assuming 'M' or 'F' from personal status
                    age=int(row['age']),
                    income=round(random.uniform(2000.0, 10000.0), 2),
                    marital_status=marital_status_sex['marital_status'],  # Assuming it's included here
                    telephone=mapping[row['telephone']],
                    foreign_worker=mapping[row['foreign_worker']],
                    date_created=generate_random_date(2015, 2020),  # Random creation date for customers
                    date_updated=generate_random_date(2020, 2024)   # Random update date
                )
                session.add(customer)
                session.flush()  # Flush to get the customer ID (account number will be auto-generated)

                checking_account = Accounts(
                    customer_id=customer.id,
                    account_type='checking',
                    balance=round(random.uniform(1000.0, 5000.0), 2),
                    status='active',
                    date_created=datetime.now(),
                    date_updated=datetime.now()
                )
                
                session.add(checking_account)
                session.flush()

                savings_account = Accounts(
                    customer_id=customer.id,
                    account_type='savings',
                    balance=round(random.uniform(1000.0, 5000.0), 2),
                    status='active',
                    date_created=datetime.now(),
                    date_updated=datetime.now()
                )
                
                session.add(savings_account)
                session.flush()

                # Create loan application for the customer
                loan_application = LoanApplications(
                    customer_id=customer.id,
                    loan_amount_requested=round(float(row['credit_amount']),2),
                    decision='approved',  # Randomly decide approval or rejection
                    decision_date=generate_random_date(2020, 2024),
                    duration_in_months=int(row['duration']),
                    status_of_existing_checking_account=mapping[row['status_of_existing_checking_account']],
                    credit_history=mapping[row['credit_history']],
                    purpose=mapping[row['purpose']],
                    savings_account_bonds=mapping[row['savings_account_bonds']],
                    present_employment_since=mapping[row['present_employment_since']],
                    installment_rate_in_percentage_of_disposable_income=int(row['installment_rate_in_percentage_of_disposable_income']),
                    other_debtors_guarantors=mapping[row['other_debtors_guarantors']],
                    present_residence_since=int(row['present_residence_since']),
                    property=mapping[row['property']],
                    other_installment_plans=mapping[row['other_installment_plans']],
                    housing=mapping[row['housing']],
                    number_of_existing_credits_at_this_bank=int(row['number_of_existing_credits_at_this_bank']),
                    job=mapping[row['job']],
                    number_of_people_being_liable_to_provide_maintenance_for=int(row['number_of_people_being_liable_to_provide_maintenance_for']),
                    date_created=generate_random_date(2020, 2024),  # Random creation date
                    date_updated=generate_random_date(2020, 2024)   # Random update date
                )
                session.add(loan_application)
                session.flush()  # Flush to get the application ID

                # Create loan based on the loan application (assuming decision == 'approved')
                if loan_application.decision == 'approved':
                    loan = Loans(
                        customer_id=customer.id,
                        application_id=loan_application.id,
                        loan_amount=round(float(row['credit_amount']), 2),
                        interest_rate=round(random.uniform(3.0, 10.0), 2),  # Random interest rate
                        duration_in_months=int(row['duration']),
                        outcome=int(row['class']),
                        outcome_date=generate_random_date(2020, 2024),
                        date_created=generate_random_date(2020, 2024),
                        date_updated=generate_random_date(2020, 2024)
                    )
                    session.add(loan)

        session.commit()

    # Call the function to load data into the new tables
    split_loanee_data('loanees.csv')


def downgrade() -> None:
    bind = op.get_bind()
    Session = sessionmaker(bind=bind)
    session = Session()

    # Deleting related data
    session.query(Loans).delete(synchronize_session=False)
    session.query(LoanApplications).delete(synchronize_session=False)
    # session.query(Accounts).delete(synchronize_session=False)
    session.query(Customers).delete(synchronize_session=False)

    session.commit()
