# 基础镜像
FROM python:3.12-slim AS builder

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 工作目录
WORKDIR /app

# 项目配置与锁文件
COPY apps/server/pyproject.toml apps/server/uv.lock ./apps/server/
# Server 源码
COPY apps/server/src/ ./apps/server/src/

# 安装依赖（非可编辑模式安装 server 包）
RUN uv sync --frozen --no-editable --project apps/server

# 运行层
FROM python:3.12-slim

# 虚拟环境
COPY --from=builder /app/apps/server/.venv /app/.venv

# 环境变量
ENV PATH="/app/.venv/bin:$PATH"

# 工作目录
WORKDIR /app

# 运行用户
RUN groupadd --system --gid 1000 app && useradd --system --uid 1000 --gid app app

# 用户
USER app

# 端口
EXPOSE 8000

# 工作进程数 - 默认 2 兼顾单进程阻塞隔离
# 可通过同名环境变量覆盖
ENV GRANIAN_WORKERS=2

# 启动命令
CMD ["granian", "--interface", "asgi", "--host", "0.0.0.0", "server.main:app"]
