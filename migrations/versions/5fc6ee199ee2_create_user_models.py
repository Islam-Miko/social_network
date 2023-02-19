"""create user models

Revision ID: 5fc6ee199ee2
Revises: 
Create Date: 2023-01-10 22:20:15.546404

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "5fc6ee199ee2"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sn_user",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.SmallInteger, nullable=False, autoincrement=True),
        sa.Column("first_name", sa.String(50), nullable=False),
        sa.Column("last_name", sa.String(50), nullable=False),
        sa.Column("birth_date", sa.DATE, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "sn_credential",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "id",
            sa.SmallInteger,
            primary_key=True,
        ),
        sa.Column("login", sa.String(50), nullable=False),
        sa.Column("password", sa.String(255), nullable=False),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["sn_user.id"],
            ondelete="CASCADE",
        ),
    )


def downgrade() -> None:
    op.drop_table("sn_user")
    op.drop_table("sn_credential")
