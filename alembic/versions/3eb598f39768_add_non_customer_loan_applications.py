"""add non_customer loan applications

Revision ID: 3eb598f39768
Revises: 4fb5decd63a1
Create Date: 2024-09-26 08:41:52.690789

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
from app.db.models.loans import Loans 
from app.db.models.loan_applications import LoanApplications

# revision identifiers, used by Alembic.
revision: str = '3eb598f39768'
down_revision: Union[str, None] = '4fb5decd63a1'
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

    # Function to load non-customer applicants data into LoanApplications tables
    def split_loanee_data(csv_file):
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for i, row in enumerate(reader):

                if i == 1000:
                    break

                # Create new customer entry with random name using Faker
                marital_status_sex = marital_status_sex_decoder(row['personal_status_and_sex'])
                nc_info = {
                    "full_name": generate_random_full_name(),  # Randomly generated name
                    "sex": marital_status_sex['sex'],  # Assuming 'M' or 'F' from personal status
                    "age": int(row['age']),
                    "income": round(random.uniform(2000.0, 10000.0), 2),
                    "marital_status": marital_status_sex['marital_status'],  # Assuming it's included here
                    "telephone": mapping[row['telephone']],
                    "mobile": '233201161093',
                    "email": 'eacquahh@gmail.com',
                    "foreign_worker": mapping[row['foreign_worker']]
                }

                # Create loan application for the customer
                loan_application = LoanApplications(
                    loan_amount_requested=round(random.uniform(2000.0, 10000.0), 2),
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
                    nc_info=nc_info,
                    date_created=generate_random_date(2020, 2024),  # Random creation date
                    date_updated=generate_random_date(2020, 2024)   # Random update date
                )
                session.add(loan_application)
                session.flush()  # Flush to get the application ID

        session.commit()

    # Call the function to load data into the new tables
    split_loanee_data('loanees.csv')


def downgrade() -> None:
    bind = op.get_bind()
    Session = sessionmaker(bind=bind)
    session = Session()

    # Deleting related data
    # session.query(Loans).delete(synchronize_session=False)
    session.query(LoanApplications).delete(synchronize_session=False)

    session.commit()
