"""permission icon open_type directory

Revision ID: 20261023_0002
Revises: 20260410_0001
Create Date: 2026-10-23

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261023_0002"
down_revision: Union[str, None] = "20260410_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("permissions", sa.Column("icon", sa.String(length=80), nullable=True))
    op.add_column("permissions", sa.Column("open_type", sa.String(length=20), nullable=True))


def downgrade() -> None:
    op.drop_column("permissions", "open_type")
    op.drop_column("permissions", "icon")
