# Dockerfile - https://docs.docker.com/reference/dockerfile/

# 构建层
FROM oven/bun:1 AS builder

# 构建参数（VITE_* 为构建时注入）
ARG VITE_TELEMETRY_URL
ARG VITE_OIDC_ISSUER
ARG VITE_OIDC_CLIENT_ID
ARG VITE_API_BASE_URL

# 传递为环境变量供 vite 构建读取
ENV VITE_TELEMETRY_URL=$VITE_TELEMETRY_URL
ENV VITE_OIDC_ISSUER=$VITE_OIDC_ISSUER
ENV VITE_OIDC_CLIENT_ID=$VITE_OIDC_CLIENT_ID
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# 工作目录
WORKDIR /app

# 工作区配置
COPY package.json bun.lock ./
# 共享包
COPY packages/typescript/ packages/typescript/
# Web 应用
COPY apps/web/ apps/web/

# 安装依赖
RUN bun install --frozen-lockfile

# 构建（产物不含 Source Map）
WORKDIR /app/apps/web
RUN bun run build

# 运行层
FROM nginx:alpine

# 静态产物
COPY --from=builder /app/apps/web/dist /usr/share/nginx/html

# 端口
EXPOSE 80

# 启动
CMD ["nginx", "-g", "daemon off;"]
