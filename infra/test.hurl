# OpenObserve

# 健康检查
GET http://127.0.0.1:5080/healthz
HTTP 200

# 日志摄入
POST http://127.0.0.1:5080/api/default/hurl-acceptance/_json
Authorization: {{OTEL_EXPORTER_OTLP_HEADERS}}
[
  {
    "message": "hurl acceptance probe",
    "level": "info"
  }
]
HTTP 200

# authentik

# 就绪检查
GET http://127.0.0.1:9000/-/health/ready/
HTTP 200

# 根路径重定向
GET http://127.0.0.1:9000/
HTTP 302

# OIDC discovery
# GET http://127.0.0.1:9000/application/o/<slug>/.well-known/openid-configuration
# HTTP 200

# Traefik

# HTTP 重定向 HTTPS
GET http://127.0.0.1/
HTTP 301

# HTTPS 入口
GET https://127.0.0.1/
[Options]
insecure: true
HTTP 404
