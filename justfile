# justfile - `https://github.com/casey/just`

# 不稳定特性
set unstable

# shell
set shell := ["bash", "-cu"]

# Windows shell
set windows-shell := ["powershell", "-NoProfile", "-Command"]

# 默认
default:
    # 列出任务
    @just --list

# 初始化
setup:
    # 安装工具
    mise install --locked

# 检查
lint:
    # 检查格式
    dprint check
    # 拼写检查
    typos

# 格式化
format:
    # 格式化代码
    dprint fmt

# 钩子
hooks:
    # 安装钩子
    lefthook install
