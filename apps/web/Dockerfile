# 构建层
FROM oven/bun:1 AS builder

  # 构建参数（VITE_* 为构建时注入）
  ARG VITE_API_BASE_URL
  ARG VITE_HEARTBEAT_INTERVAL

  # 传递为环境变量供 vite 构建读取
  ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
  ENV VITE_HEARTBEAT_INTERVAL=$VITE_HEARTBEAT_INTERVAL

  # 工作目录
  WORKDIR /app

  # 工作区配置
  COPY package.json bun.lock ./
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

  # Nginx 站点配置 - 覆盖默认站点以实现 SPA 回退与 API 反代
  COPY apps/web/nginx.conf /etc/nginx/conf.d/default.conf

  # 授予非 root 用户绑定 80 端口的能力
  RUN apk add --no-cache libcap && setcap "cap_net_bind_service=+ep" /usr/sbin/nginx

  # 运行期目录交由 nginx 用户持有
  RUN chown -R nginx:nginx /var/cache/nginx /var/run /usr/share/nginx/html

  # 运行用户 - 禁止以 root 运行
  USER nginx

  # 端口
  EXPOSE 80

  # 启动
  CMD ["nginx", "-g", "daemon off;"]
