"""Many updates

Revision ID: 5def871818b3
Revises: 1bea163978f3
Create Date: 2024-09-19 17:13:58.961189

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5def871818b3'
down_revision: Union[str, None] = '1bea163978f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('customers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('full_name', sa.String(), nullable=False),
    sa.Column('sex', sa.String(), nullable=False),
    sa.Column('marital_status', sa.String(), nullable=False),
    sa.Column('age', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(), server_default="eacquahh@gmail.com", nullable=True),
    sa.Column('mobile', sa.String(), server_default="233201161093", nullable=True),
    sa.Column('income', sa.Numeric(), nullable=True),
    sa.Column('telephone', sa.String(), nullable=False),
    sa.Column('foreign_worker', sa.String(), nullable=False),
    sa.Column('date_created', sa.DateTime(), nullable=False),
    sa.Column('date_updated', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_customers_id'), 'customers', ['id'], unique=False)

    op.create_table('accounts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=False),
    sa.Column('account_number', sa.String(length=12), nullable=False),
    sa.Column('account_type', sa.String(), nullable=False),
    sa.Column('balance', sa.Numeric(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('date_created', sa.DateTime(), nullable=False),
    sa.Column('date_updated', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='CASCADE'),
    sa.UniqueConstraint('account_number'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_accounts_id'), 'accounts', ['id'], unique=False)

    op.create_table('loan_applications',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=False),
    sa.Column('loan_amount_requested', sa.Numeric(), nullable=False),
    sa.Column('decision', sa.String(), nullable=True),
    sa.Column('decision_date', sa.DateTime(), nullable=True),
    sa.Column('notes', sa.String(), nullable=True),
    sa.Column('application_date', sa.DateTime(), nullable=False),
    sa.Column('date_created', sa.DateTime(), nullable=False),
    sa.Column('date_updated', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_loan_applications_id'), 'loan_applications', ['id'], unique=False)

    op.create_table('loans',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=False),
    sa.Column('application_id', sa.Integer(), nullable=False),
    sa.Column('loan_amount', sa.Numeric(), nullable=False),
    sa.Column('interest_rate', sa.Numeric(), nullable=False),
    sa.Column('duration_in_months', sa.Integer(), nullable=False),
    sa.Column('outcome', sa.Integer(), nullable=True),
    sa.Column('outcome_date', sa.DateTime(), nullable=True),
    sa.Column('date_applied', sa.DateTime(), nullable=False),
    sa.Column('date_created', sa.DateTime(), nullable=False),
    sa.Column('date_updated', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['application_id'], ['loan_applications.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_loans_id'), 'loans', ['id'], unique=False)
    # ### end Alembic commands ###



def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_loans_id'), table_name='loans')
    op.drop_table('loans')
    op.drop_index(op.f('ix_loan_applications_id'), table_name='loan_applications')
    op.drop_table('loan_applications')
    op.drop_index(op.f('ix_accounts_id'), table_name='accounts')
    op.drop_table('accounts')
    op.drop_index(op.f('ix_customers_id'), table_name='customers')
    op.drop_table('customers')
    # ### end Alembic commands ###