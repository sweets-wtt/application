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
FROM caddy:2.11.9@sha256:e40b94d0a43b5ff69cb20568d73f10c70703df7b0ffc2298eb3d723cdc9d0bd1

  # 静态产物
  COPY --from=builder /app/apps/web/dist /srv

  # 站点配置
  COPY infra/Caddyfile /etc/caddy/Caddyfile

  # 运行用户
  RUN addgroup -g 1000 -S caddy && adduser -u 1000 -S -G caddy -s /sbin/nologin caddy

  # 绑定低端口能力
  RUN setcap "cap_net_bind_service=+ep" /usr/bin/caddy

  # 运行期目录属主
  RUN chown -R caddy:caddy /srv /data /config

  # 运行用户
  USER caddy

  # 端口
  EXPOSE 80 443 443/udp

  # 启动命令
  CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile", "--adapter", "caddyfile"]
