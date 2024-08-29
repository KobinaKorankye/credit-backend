"""populate loanees

Revision ID: 4ef47f180389
Revises: 8cf8f026ce5b
Create Date: 2024-08-29 09:38:52.830859

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import csv
from sqlalchemy.orm import sessionmaker
from app.db.models.gapplicant import GApplicant
from app.db.models.loanee import Loanee


# revision identifiers, used by Alembic.
revision: str = '4ef47f180389'
down_revision: Union[str, None] = '8cf8f026ce5b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Bind the current migration context to SQLAlchemy ORM session
    bind = op.get_bind()
    Session = sessionmaker(bind=bind)
    session = Session()

    # Function to load data into Loanee table
    def load_loanee_data(csv_file):
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                loanee = Loanee(
                    id=int(row['id']),
                    status_of_existing_checking_account=row['status_of_existing_checking_account'],
                    duration=int(row['duration']),
                    credit_history=row['credit_history'],
                    purpose=row['purpose'],
                    credit_amount=int(row['credit_amount']),
                    savings_account_bonds=row['savings_account_bonds'],
                    present_employment_since=row['present_employment_since'],
                    installment_rate_in_percentage_of_disposable_income=int(row['installment_rate_in_percentage_of_disposable_income']),
                    personal_status_and_sex=row['personal_status_and_sex'],
                    other_debtors_guarantors=row['other_debtors_guarantors'],
                    present_residence_since=int(row['present_residence_since']),
                    property=row['property'],
                    age=int(row['age']),
                    other_installment_plans=row['other_installment_plans'],
                    housing=row['housing'],
                    number_of_existing_credits_at_this_bank=int(row['number_of_existing_credits_at_this_bank']),
                    job=row['job'],
                    number_of_people_being_liable_to_provide_maintenance_for=int(row['number_of_people_being_liable_to_provide_maintenance_for']),
                    telephone=row['telephone'],
                    foreign_worker=row['foreign_worker'],
                    class_=int(row['class']),
                    income=3000  # Default to 3000
                )
                session.add(loanee)
        session.commit()

    # Load data from CSVs
    load_loanee_data('loanees.csv')

def downgrade():
    # Optionally, delete data on downgrade
    bind = op.get_bind()
    Session = sessionmaker(bind=bind)
    session = Session()

    session.query(Loanee).filter(Loanee.id >= 0, Loanee.id <= 999).delete(synchronize_session=False)
    session.commit()
