"""idempotency 幂等表

Revision ID: 0001_idempotency
Revises:
Create Date: 2026-09-26
"""

from alembic import op

# 修订标识
revision = "0001_idempotency"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """建幂等表 - HTTP Idempotency-Key 与工作流 run 同事务记录"""
    op.execute(
        """
        CREATE TABLE idempotency (
            key            TEXT PRIMARY KEY,
            workflow_name  TEXT NOT NULL,
            run_id         TEXT NOT NULL,
            created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )

    # run_id 查询索引
    op.execute(
        "CREATE INDEX ix_idempotency_run_id ON idempotency (run_id)"
    )


def downgrade() -> None:
    """删幂等表"""
    op.execute("DROP TABLE IF EXISTS idempotency")
