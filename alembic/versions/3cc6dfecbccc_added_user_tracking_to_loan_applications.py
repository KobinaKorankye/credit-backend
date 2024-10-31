"""Added user tracking to loan applications

Revision ID: 3cc6dfecbccc
Revises: edf9b773e818
Create Date: 2024-10-25 12:16:00.806265

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3cc6dfecbccc'
down_revision: Union[str, None] = 'edf9b773e818'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns
    op.add_column('loan_applications', sa.Column('officer_id', sa.Integer(), nullable=True))
    op.add_column('loan_applications', sa.Column('reviewer_id', sa.Integer(), nullable=True))
    op.add_column('loan_applications', sa.Column('approver_id', sa.Integer(), nullable=True))
    
    # Create foreign keys with explicit names
    op.create_foreign_key('fk_loan_applications_officer_id', 'loan_applications', 'users', ['officer_id'], ['id'])
    op.create_foreign_key('fk_loan_applications_reviewer_id', 'loan_applications', 'users', ['reviewer_id'], ['id'])
    op.create_foreign_key('fk_loan_applications_approver_id', 'loan_applications', 'users', ['approver_id'], ['id'])


def downgrade() -> None:
    # Drop foreign keys by name
    op.drop_constraint('fk_loan_applications_officer_id', 'loan_applications', type_='foreignkey')
    op.drop_constraint('fk_loan_applications_reviewer_id', 'loan_applications', type_='foreignkey')
    op.drop_constraint('fk_loan_applications_approver_id', 'loan_applications', type_='foreignkey')
    
    # Drop columns
    op.drop_column('loan_applications', 'officer_id')
    op.drop_column('loan_applications', 'reviewer_id')
    op.drop_column('loan_applications', 'approver_id')
