"""create post models

Revision ID: 4c0b50da81fc
Revises: d76993198d1f
Create Date: 2023-01-11 22:42:08.229353

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4c0b50da81fc"
down_revision = "d76993198d1f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sn_post",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.SmallInteger, nullable=False, autoincrement=True),
        sa.Column("header", sa.String(50), nullable=False),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column(
            "owner",
            sa.Integer,
            sa.ForeignKey("sn_user.id"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "sn_like",
        sa.Column(
            "post_id",
            sa.SmallInteger,
            sa.ForeignKey("sn_post.id"),
            primary_key=True,
        ),
        sa.Column(
            "user_id",
            sa.SmallInteger,
            sa.ForeignKey("sn_user.id"),
            primary_key=True,
        ),
    )


def downgrade() -> None:
    op.drop_table("sn_like")
    op.drop_table("sn_post")
