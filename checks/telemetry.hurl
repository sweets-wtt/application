# Hurl 验收 - https://hurl.dev/docs/
# OpenObserve API - https://openobserve.ai/docs/api/

# api 日志按服务非空
POST http://127.0.0.1:5080/api/default/_search
Authorization: Basic {{OBSERVE_AUTH_BASIC}}
Content-Type: application/json
{
  "query": {
    "start_time": {{start}},
    "end_time": {{end}},
    "from": 0,
    "size": 10,
    "sql": "SELECT * FROM \"default\" WHERE service_name = 'api'"
  }
}
HTTP 200
[Asserts]
jsonpath "$.hits[0]" exists

# 指标管道非空 主机与 PostgreSQL 指标
POST http://127.0.0.1:5080/api/default/_search
Authorization: Basic {{OBSERVE_AUTH_BASIC}}
Content-Type: application/json
{
  "query": {
    "start_time": {{start}},
    "end_time": {{end}},
    "from": 0,
    "size": 10,
    "sql": "SELECT * FROM \"default\""
  }
}
HTTP 200
[Asserts]
jsonpath "$.hits[0]" exists

# traces 流存在
GET http://127.0.0.1:5080/api/default/streams
Authorization: Basic {{OBSERVE_AUTH_BASIC}}
HTTP 200
[Asserts]
jsonpath "$.list[?(@.stream_type=='traces')].name" contains "default"

# web 日志按服务查询 空容忍 事件驱动
POST http://127.0.0.1:5080/api/default/_search
Authorization: Basic {{OBSERVE_AUTH_BASIC}}
Content-Type: application/json
{
  "query": {
    "start_time": {{start}},
    "end_time": {{end}},
    "from": 0,
    "size": 10,
    "sql": "SELECT * FROM \"default\" WHERE service_name = 'web'"
  }
}
HTTP 200
[Asserts]
jsonpath "$.hits" exists

# miniapp 日志按服务查询 空容忍 事件驱动
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
    "sql": "SELECT * FROM \"default\" WHERE service_name = 'miniapp'"
  }
}
HTTP 200
[Asserts]
jsonpath "$.hits" exists
