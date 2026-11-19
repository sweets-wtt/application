# .github

## 技术架构

```text
根: .github
├── 语法检查: actionlint
└── 安全审计: zizmor
```

## 项目结构

```text
.
├── actions/               # 复合动作
│   └── setup/             # 环境准备
│       └── action.yaml    # 工具链准备
├── workflows/             # 工作流
│   ├── ci.yaml            # 持续集成
│   └── release.yaml       # 版本发布
├── actionlint.yaml        # 语法检查
└── README.md              # 目录说明
```

## 发版流程

手动触发 `release` 工作流，仅限 `main` 分支：

* 校验：运行 `task check` 与提交规范检查，未通过则中止
* 计算版本：`cog bump --auto` 按提交推导版本，写 `CHANGELOG.md`，提交 `chore(version)`，打 `vX.Y.Z` 标签
* 推送：版本提交与标签推送到 `main`，无版本变更时跳过
