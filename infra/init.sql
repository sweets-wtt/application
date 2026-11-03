-- 应用口令
\getenv app_password POSTGRES_APP_PASSWORD

-- 应用角色
CREATE ROLE app LOGIN PASSWORD :'app_password';

-- 应用库
CREATE DATABASE app OWNER app;

-- Authelia 口令
\getenv authelia_password POSTGRES_AUTHELIA_PASSWORD

-- Authelia 角色
CREATE ROLE authelia LOGIN PASSWORD :'authelia_password';

-- Authelia 库
CREATE DATABASE authelia OWNER authelia;
