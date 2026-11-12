# 构建层
FROM oven/bun:1 AS builder

  # 构建参数
  ARG VITE_API_BASE_URL
  ARG VITE_HEARTBEAT_INTERVAL

  # 构建参数转环境变量
  ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
  ENV VITE_HEARTBEAT_INTERVAL=$VITE_HEARTBEAT_INTERVAL

  # 工作目录
  WORKDIR /app

  # 工作区配置
  COPY package.json bun.lock ./
  # Web 应用配置
  COPY apps/web/package.json apps/web/
  # Web 源码
  COPY apps/web/src/ apps/web/src/
  # 构建配置
  COPY apps/web/index.html apps/web/vite.config.ts apps/web/tsconfig.json apps/web/uno.config.ts apps/web/
  # 类型声明
  COPY apps/web/components.d.ts apps/web/

  # 安装依赖
  RUN bun install --frozen-lockfile

  # 构建
  WORKDIR /app/apps/web
  RUN bun run build

# 运行层
FROM nginx:alpine

  # 静态产物
  COPY --from=builder /app/apps/web/dist /usr/share/nginx/html

  # Nginx 站点配置
  COPY apps/web/nginx.conf /etc/nginx/conf.d/default.conf

  # 绑定低端口能力
  RUN apk add --no-cache libcap && setcap "cap_net_bind_service=+ep" /usr/sbin/nginx

  # 运行期目录属主
  RUN chown -R nginx:nginx /var/cache/nginx /var/run /usr/share/nginx/html

  # 运行用户
  USER nginx

  # 端口
  EXPOSE 80

  # 启动命令
  CMD ["nginx", "-g", "daemon off;"]
