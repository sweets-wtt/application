# 基础镜像
FROM python:3.12-slim AS builder

  # 安装 uv
  COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

  # 工作目录
  WORKDIR /app

  # 工作区配置与锁文件
  COPY pyproject.toml uv.lock ./
  # Server 项目配置
  COPY apps/server/pyproject.toml ./apps/server/
  # Server 源码
  COPY apps/server/src/ ./apps/server/src/

  # 安装依赖
  RUN uv sync --frozen --no-editable --no-dev --package server

# 运行层
FROM python:3.12-slim

  # 虚拟环境
  COPY --from=builder /app/.venv /app/.venv

  # 环境变量
  ENV PATH="/app/.venv/bin:$PATH"

  # 工作目录
  WORKDIR /app

  # 运行用户与组
  RUN groupadd --system --gid 1000 app && useradd --system --uid 1000 --gid app app

  # 运行用户
  USER app

  # 端口
  EXPOSE 8000

  # 工作进程数
  ENV GRANIAN_WORKERS=2

  # 启动命令
  CMD ["granian", "--interface", "asgi", "--host", "0.0.0.0", "server.main:app"]
