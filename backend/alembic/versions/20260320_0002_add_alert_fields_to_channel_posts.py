"""add alert analytics fields to channel posts

Revision ID: 20260320_0002
Revises: 20260320_0001
Create Date: 2026-03-20 23:10:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260320_0002"
down_revision = "20260320_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "channel_posts",
        sa.Column("channel_median_views", sa.Float(), nullable=False, server_default="0"),
    )
    op.add_column(
        "channel_posts",
        sa.Column("alert_threshold_views", sa.Float(), nullable=False, server_default="0"),
    )
    op.add_column(
        "channel_posts",
        sa.Column("is_alert_candidate", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "channel_posts",
        sa.Column("alerted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_channel_posts_is_alert_candidate", "channel_posts", ["is_alert_candidate"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_channel_posts_is_alert_candidate", table_name="channel_posts")
    op.drop_column("channel_posts", "alerted_at")
    op.drop_column("channel_posts", "is_alert_candidate")
    op.drop_column("channel_posts", "alert_threshold_views")
    op.drop_column("channel_posts", "channel_median_views")
