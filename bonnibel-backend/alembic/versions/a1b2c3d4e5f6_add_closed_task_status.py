"""add CLOSED to taskstatus enum

Revision ID: a1b2c3d4e5f6
Revises: 61147419395c
Create Date: 2026-06-14 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '61147419395c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Status CLOSED jest używany przez request_close i UI; brakowało go w enumie DB.
    op.execute("ALTER TYPE taskstatus ADD VALUE IF NOT EXISTS 'CLOSED'")


def downgrade() -> None:
    # PostgreSQL nie wspiera usuwania wartości z enuma — świadomie pomijamy.
    pass
