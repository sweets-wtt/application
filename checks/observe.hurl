# Hurl 验收 - https://hurl.dev/docs/
# OpenObserve API - https://openobserve.ai/docs/api/

# 存活探测
GET http://127.0.0.1:5080/healthz
HTTP 200

# 搜索路径冒烟 不涉应用与其它容器数据
POST http://127.0.0.1:5080/api/default/_search
Authorization: Basic {{OBSERVE_AUTH_BASIC}}
Content-Type: application/json
{
  "query": {
    "start_time": {{start}},
    "end_time": {{end}},
    "from": 0,
    "size": 10,
    "stream_type": "logs",
    "sql": "SELECT * FROM \"default\""
  }
}
HTTP 200
[Asserts]
jsonpath "$.hits" exists
