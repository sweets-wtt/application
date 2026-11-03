"""数据库模型"""

from datetime import datetime

from sqlalchemy import DateTime, Index, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """模型基类 - 承载全部表元数据, 供 alembic autogenerate 使用"""


class Idempotency(Base):
    """幂等记录 - HTTP Idempotency-Key 与工作流 run 的映射"""

    __tablename__ = "idempotency"

    # 幂等键
    key: Mapped[str] = mapped_column(Text, primary_key=True)
    # 工作流名
    workflow_name: Mapped[str] = mapped_column(Text, nullable=False)
    # 工作流 run 标识
    run_id: Mapped[str] = mapped_column(Text, nullable=False)
    # 创建时间
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        # run_id 查询索引
        Index("ix_idempotency_run_id", "run_id"),
    )
