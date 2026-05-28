"""Add pull request review statuses

Revision ID: 8b6f7e3ac41a
Revises: 2794f40e7c2d
Create Date: 2026-05-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "8b6f7e3ac41a"
down_revision: Union[str, Sequence[str], None] = "2794f40e7c2d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE pullrequeststatus ADD VALUE IF NOT EXISTS 'APPROVED'")
    op.execute("ALTER TYPE pullrequeststatus ADD VALUE IF NOT EXISTS 'REJECTED'")


def downgrade() -> None:
    # PostgreSQL does not support dropping enum values directly.
    pass
