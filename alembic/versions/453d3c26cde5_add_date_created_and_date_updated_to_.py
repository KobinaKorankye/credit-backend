"""Add date_created and date_updated to GApplicant

Revision ID: 453d3c26cde5
Revises: adaf0a84eb7f
Create Date: 2024-09-10 17:18:45.903608

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import func


# revision identifiers, used by Alembic.
revision: str = '453d3c26cde5'
down_revision: Union[str, None] = 'adaf0a84eb7f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('gapplicants', sa.Column('date_created', sa.DateTime(),server_default=func.now(), nullable=False))
    op.add_column('gapplicants', sa.Column('date_updated', sa.DateTime(),server_default=func.now(), nullable=False))
    op.add_column('loanees', sa.Column('date_created', sa.DateTime(),server_default=func.now(), nullable=False))
    op.add_column('loanees', sa.Column('date_updated', sa.DateTime(),server_default=func.now(), nullable=False))
    # ### end Alembic commands ###

def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('loanees', 'date_updated')
    op.drop_column('loanees', 'date_created')
    op.drop_column('gapplicants', 'date_updated')
    op.drop_column('gapplicants', 'date_created')
    # ### end Alembic commands ###
