"""add sender whitelist and dedup fields

Revision ID: 0ff66bfa5c79
Revises: fea701f53aa0
Create Date: 2026-03-31 13:08:26.852112

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0ff66bfa5c79"
down_revision: Union[str, None] = "fea701f53aa0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create sender_whitelist table
    op.create_table(
        "sender_whitelist",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email_pattern", sa.String(255), nullable=False, unique=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # Add dedup columns to movements
    op.add_column(
        "movements",
        sa.Column("duplicate_group_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "movements",
        sa.Column("is_duplicate", sa.Boolean(), default=False, server_default="false"),
    )
    op.add_column(
        "movements",
        sa.Column(
            "superseded_by_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("movements.id"),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_movements_duplicate_group_id",
        "movements",
        ["duplicate_group_id"],
    )

    # Seed initial whitelist  # noqa: E501
    seed_sql = """
    INSERT INTO sender_whitelist
        (id, email_pattern, name, is_active, created_at, updated_at)
    VALUES
        (gen_random_uuid(), '@envio.santander.com.mx', 'Santander',
         true, now(), now()),
        (gen_random_uuid(), 'notificaciones@banamex.com', 'Banamex',
         true, now(), now()),
        (gen_random_uuid(), '@banamex.com', 'Banamex',
         true, now(), now()),
        (gen_random_uuid(), '@americanexpress.com.mx', 'American Express',
         true, now(), now()),
        (gen_random_uuid(), 'noreply@uber.com', 'Uber',
         true, now(), now()),
        (gen_random_uuid(), 'uber@uber.com', 'Uber Eats',
         true, now(), now()),
        (gen_random_uuid(), '@paypal.com.mx', 'PayPal',
         true, now(), now()),
        (gen_random_uuid(), 'service@paypal.com', 'PayPal',
         true, now(), now())
    """
    op.execute(sa.text(seed_sql))


def downgrade() -> None:
    op.drop_index("ix_movements_duplicate_group_id", "movements")
    op.drop_column("movements", "superseded_by_id")
    op.drop_column("movements", "is_duplicate")
    op.drop_column("movements", "duplicate_group_id")
    op.drop_table("sender_whitelist")
