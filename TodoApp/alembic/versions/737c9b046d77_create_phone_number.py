"""Create phone number

Revision ID: 737c9b046d77
Revises: 
Create Date: 2026-10-22 16:34:30.892541

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '737c9b046d77'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('phone_number', sa.String(), nullable=True))
def downgrade() -> None:
    op.drop_column('users', 'phone_number')