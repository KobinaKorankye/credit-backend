"""Initial migration

Revision ID: 8cf8f026ce5b
Revises: 
Create Date: 2024-08-29 08:38:30.059046

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8cf8f026ce5b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('gapplicants',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('status_of_existing_checking_account', sa.String(), nullable=False),
    sa.Column('duration', sa.Integer(), nullable=False),
    sa.Column('credit_history', sa.String(), nullable=False),
    sa.Column('purpose', sa.String(), nullable=False),
    sa.Column('credit_amount', sa.Integer(), nullable=False),
    sa.Column('savings_account_bonds', sa.String(), nullable=False),
    sa.Column('present_employment_since', sa.String(), nullable=False),
    sa.Column('installment_rate_in_percentage_of_disposable_income', sa.Integer(), nullable=False),
    sa.Column('personal_status_and_sex', sa.String(), nullable=False),
    sa.Column('other_debtors_guarantors', sa.String(), nullable=False),
    sa.Column('present_residence_since', sa.Integer(), nullable=False),
    sa.Column('property', sa.String(), nullable=False),
    sa.Column('age', sa.Integer(), nullable=False),
    sa.Column('other_installment_plans', sa.String(), nullable=False),
    sa.Column('housing', sa.String(), nullable=False),
    sa.Column('number_of_existing_credits_at_this_bank', sa.Integer(), nullable=False),
    sa.Column('job', sa.String(), nullable=False),
    sa.Column('number_of_people_being_liable_to_provide_maintenance_for', sa.Integer(), nullable=False),
    sa.Column('telephone', sa.String(), nullable=False),
    sa.Column('foreign_worker', sa.String(), nullable=False),
    sa.Column('approved', sa.Integer(), nullable=True),
    sa.Column('income', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_gapplicants_id'), 'gapplicants', ['id'], unique=False)
    op.create_table('loanees',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('status_of_existing_checking_account', sa.String(), nullable=False),
    sa.Column('duration', sa.Integer(), nullable=False),
    sa.Column('credit_history', sa.String(), nullable=False),
    sa.Column('purpose', sa.String(), nullable=False),
    sa.Column('credit_amount', sa.Integer(), nullable=False),
    sa.Column('savings_account_bonds', sa.String(), nullable=False),
    sa.Column('present_employment_since', sa.String(), nullable=False),
    sa.Column('installment_rate_in_percentage_of_disposable_income', sa.Integer(), nullable=False),
    sa.Column('personal_status_and_sex', sa.String(), nullable=False),
    sa.Column('other_debtors_guarantors', sa.String(), nullable=False),
    sa.Column('present_residence_since', sa.Integer(), nullable=False),
    sa.Column('property', sa.String(), nullable=False),
    sa.Column('age', sa.Integer(), nullable=False),
    sa.Column('other_installment_plans', sa.String(), nullable=False),
    sa.Column('housing', sa.String(), nullable=False),
    sa.Column('number_of_existing_credits_at_this_bank', sa.Integer(), nullable=False),
    sa.Column('job', sa.String(), nullable=False),
    sa.Column('number_of_people_being_liable_to_provide_maintenance_for', sa.Integer(), nullable=False),
    sa.Column('telephone', sa.String(), nullable=False),
    sa.Column('foreign_worker', sa.String(), nullable=False),
    sa.Column('class_', sa.Integer(), nullable=False),
    sa.Column('income', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_loanees_id'), 'loanees', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_loanees_id'), table_name='loanees')
    op.drop_table('loanees')
    op.drop_index(op.f('ix_gapplicants_id'), table_name='gapplicants')
    op.drop_table('gapplicants')
    # ### end Alembic commands ###
