-- 读取环境变量
\getenv app_password POSTGRES_PASSWORD

-- 创建角色
CREATE ROLE app LOGIN PASSWORD :'app_password';

-- 创建数据库
CREATE DATABASE app OWNER app;
CREATE DATABASE hatchet OWNER app;
CREATE DATABASE authentik OWNER app;
