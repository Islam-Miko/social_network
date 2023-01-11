"""create refresh token

Revision ID: d76993198d1f
Revises: 5fc6ee199ee2
Create Date: 2023-01-10 23:10:41.364719

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d76993198d1f"
down_revision = "5fc6ee199ee2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "webtronics_refresh_token",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.SmallInteger, nullable=False, autoincrement=True),
        sa.Column("key", sa.String(255), nullable=False),
        sa.Column("valid_until", sa.Float, nullable=False),
        sa.Column("owner", sa.INTEGER, nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["owner"],
            ["webtronics_user.id"],
            ondelete="CASCADE",
        ),
    )


def downgrade() -> None:
    op.drop_table("webtronics_refresh_token")
