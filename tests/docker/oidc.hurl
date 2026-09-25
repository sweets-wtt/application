# Hurl - `https://hurl.dev/`

# 发现文档
GET {{AUTHENTIK_URL}}/application/o/check/.well-known/openid-configuration
HTTP 200
[Asserts]
jsonpath "$.issuer" == "{{AUTHENTIK_URL}}/application/o/check/"

# JWKS
GET {{AUTHENTIK_URL}}/application/o/check/jwks/
HTTP 200
[Asserts]
jsonpath "$.keys" count >= 1
