-- 应用口令
\getenv app_password POSTGRES_APP_PASSWORD

-- 应用角色
CREATE ROLE app LOGIN PASSWORD :'app_password';

-- 应用库
CREATE DATABASE app OWNER app;

-- Casdoor 库 - 复用应用角色
CREATE DATABASE casdoor OWNER app;
