"""模型汇总"""

from server.core.db import Base


# 模型在此汇总 - 供 Alembic autogenerate 发现
# 新增模型后须在本模块导入, 否则不会被迁移检测

__all__ = ["Base"]
