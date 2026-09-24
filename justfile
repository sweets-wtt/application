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
