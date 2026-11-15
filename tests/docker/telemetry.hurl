# Hurl - `https://hurl.dev/`

# 健康检查
GET {{OPENOBSERVE_URL}}/healthz
HTTP 200

# API 日志 - 容器文件日志经采集器入库
POST {{OPENOBSERVE_URL}}/api/default/_search
Authorization: {{OPENOBSERVE_AUTHORIZATION}}
{
  "query": {
    "sql": "SELECT * FROM default WHERE str_match(body, 'granian') LIMIT 1",
    "start_time": 1000000000000000,
    "end_time": 9990000000000000,
    "from": 0,
    "size": 1
  }
}
HTTP 200
[Asserts]
jsonpath "$.hits" count >= 1

# API 追踪 - 按服务名验收
POST {{OPENOBSERVE_URL}}/api/default/_search?type=traces
Authorization: {{OPENOBSERVE_AUTHORIZATION}}
{
  "query": {
    "sql": "SELECT * FROM default WHERE service_name = 'api' LIMIT 1",
    "start_time": 1000000000000000,
    "end_time": 9990000000000000,
    "from": 0,
    "size": 1
  }
}
HTTP 200
[Asserts]
jsonpath "$.hits" count >= 1

# API 指标 - HTTP 请求时长
POST {{OPENOBSERVE_URL}}/api/default/_search?type=metrics
Authorization: {{OPENOBSERVE_AUTHORIZATION}}
{
  "query": {
    "sql": "SELECT * FROM http_server_duration_sum WHERE service_name = 'api' LIMIT 1",
    "start_time": 1000000000000000,
    "end_time": 9990000000000000,
    "from": 0,
    "size": 1
  }
}
HTTP 200
[Asserts]
jsonpath "$.hits" count >= 1

# 前端日志 - 事件驱动空容忍
POST {{OPENOBSERVE_URL}}/api/default/_search
Authorization: {{OPENOBSERVE_AUTHORIZATION}}
{
  "query": {
    "sql": "SELECT * FROM default WHERE str_match(body, 'service=web') OR str_match(body, 'service=miniapp') LIMIT 1",
    "start_time": 1000000000000000,
    "end_time": 9990000000000000,
    "from": 0,
    "size": 1
  }
}
HTTP 200
