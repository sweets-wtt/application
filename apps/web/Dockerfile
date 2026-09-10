# Dockerfile - https://docs.docker.com/reference/dockerfile/

# 构建层
FROM oven/bun:latest AS builder

# 工作目录
WORKDIR /app

# 工作区配置
COPY package.json bun.lock tsconfig.base.json ./
# 工作区包
COPY packages/ packages/
# Web 应用
COPY apps/web/ apps/web/

# 安装依赖
RUN bun install --frozen-lockfile

# 应用目录
WORKDIR /app/apps/web

# 构建产物
RUN bun --bun vite build

# 运行层
FROM nginxinc/nginx-unprivileged:alpine

# 静态产物
COPY --from=builder /app/apps/web/dist /usr/share/nginx/html

# 用户
USER 101

# 监听端口
EXPOSE 8080
