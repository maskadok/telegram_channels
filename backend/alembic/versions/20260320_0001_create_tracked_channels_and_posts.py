"""create tracked channels and posts

Revision ID: 20260320_0001
Revises: None
Create Date: 2026-03-20 20:30:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260320_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tracked_channels",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_tracked_channels_username", "tracked_channels", ["username"], unique=True)

    op.create_table(
        "channel_posts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tracked_channel_id", sa.Integer(), nullable=False),
        sa.Column("telegram_message_id", sa.Integer(), nullable=False),
        sa.Column("message_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column("views", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("forwards", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("replies_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reactions_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("popularity_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("raw_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["tracked_channel_id"], ["tracked_channels.id"], ondelete="CASCADE"),
        sa.UniqueConstraint(
            "tracked_channel_id",
            "telegram_message_id",
            name="uq_channel_posts_channel_message",
        ),
    )
    op.create_index("ix_channel_posts_tracked_channel_id", "channel_posts", ["tracked_channel_id"], unique=False)
    op.create_index("ix_channel_posts_message_date", "channel_posts", ["message_date"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_channel_posts_message_date", table_name="channel_posts")
    op.drop_index("ix_channel_posts_tracked_channel_id", table_name="channel_posts")
    op.drop_table("channel_posts")
    op.drop_index("ix_tracked_channels_username", table_name="tracked_channels")
    op.drop_table("tracked_channels")
