"""add email metadata to movements

Revision ID: a1b2c3d4e5f6
Revises: 0ff66bfa5c79
Create Date: 2026-03-31 15:00:00.000000

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "0ff66bfa5c79"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "movements",
        sa.Column("source_email_sender", sa.String(255), nullable=True),
    )
    op.add_column(
        "movements",
        sa.Column("source_email_subject", sa.String(500), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("movements", "source_email_subject")
    op.drop_column("movements", "source_email_sender")
