# Hurl - `https://hurl.dev/`

# HTTP 重定向
GET http://localhost/
HTTP 301
[Asserts]
header "Location" startsWith "https://"

# forward-auth 未认证跳转
GET https://localhost/
Host: {{TRAEFIK_DOMAIN}}
[Options]
insecure: true
HTTP 302

# 界面登录跳转
GET https://localhost/
Host: {{AUTHENTIK_DOMAIN}}
[Options]
insecure: true
HTTP 302

# Outpost 存活
GET https://localhost/outpost.goauthentik.io/ping
Host: {{AUTHENTIK_DOMAIN}}
[Options]
insecure: true
HTTP 204
