# Hurl - `https://hurl.dev/`

# 健康检查
GET {{OPENOBSERVE_URL}}/healthz
HTTP 200

# 检查日志摄入
POST {{OPENOBSERVE_URL}}/api/default/default/_json
Authorization: {{OPENOBSERVE_AUTHORIZATION}}
[
  {
    "level": "info",
    "message": "observe check"
  }
]
HTTP 200

# 认证搜索
POST {{OPENOBSERVE_URL}}/api/default/_search
Authorization: {{OPENOBSERVE_AUTHORIZATION}}
{
  "query": {
    "sql": "SELECT * FROM default LIMIT 1",
    "start_time": 1000000000000000,
    "end_time": 9900000000000000,
    "from": 0,
    "size": 10
  }
}
HTTP 200
