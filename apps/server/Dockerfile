# Dockerfile - https://docs.docker.com/reference/dockerfile/

# 基础镜像
FROM python:3.12-slim AS builder

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 工作目录
WORKDIR /app

# 工作区配置
COPY pyproject.toml uv.lock ./
# 工作区包
COPY packages/python/ packages/python/
# Server 应用
COPY apps/server/ apps/server/

# 安装依赖
RUN uv sync --frozen --all-packages --no-editable

# 运行层
FROM python:3.12-slim

# 虚拟环境
COPY --from=builder /app/.venv /app/.venv

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

# 启动命令
CMD ["granian", "--interface", "asgi", "--host", "0.0.0.0", "server.main:app"]
