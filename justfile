# justfile - https://github.com/casey/just

# 不稳定特性
set unstable

# shell
set shell := ["bash", "-cu"]

# 默认任务
default:
    @just --list

# 环境初始化
setup:
    mise install --locked

# 代码检查
lint:
    typos
    gitleaks git --config .gitleaks.toml .

# 钩子安装
hooks:
    lefthook install

# 漏洞扫描
scan:
    trivy fs --scanners vuln --severity HIGH,CRITICAL --exit-code 1 .
