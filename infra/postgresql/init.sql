-- PostgreSQL 初始化脚本 - https://www.postgresql.org/docs/current/app-psql.html

-- 官方镜像机制：数据目录为空时经 /docker-entrypoint-initdb.d 执行

-- 应用角色口令（psql \getenv 读取环境变量）
\getenv app_password POSTGRES_APP_PASSWORD

-- 应用角色
CREATE ROLE app LOGIN PASSWORD :'app_password';

-- 应用库
CREATE DATABASE app OWNER app;
