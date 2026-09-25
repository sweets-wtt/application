-- PostgreSQL 初始化脚本 - `https://www.postgresql.org/docs/current/app-psql.html`

-- 应用口令
\getenv app_password POSTGRES_APP_PASSWORD

-- 应用角色
CREATE ROLE app LOGIN PASSWORD :'app_password';

-- 应用库
CREATE DATABASE app OWNER app;

-- Hatchet 库
CREATE DATABASE hatchet;
