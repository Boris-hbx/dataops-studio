# 05 - 目录结构与文件归档规范

## 项目根目录结构

- `[MUST]` 项目根目录遵循以下布局:

```text
dataops-studio/
├── .claude/                  # AI 辅助开发配置与工程规范
│   ├── CLAUDE.md             # 项目概览 (AI 上下文入口)
│   └── standards/            # 分级工程规范 (00-xx 编号)
│
├── docs/                     # 项目文档 (分类归档)
│   ├── README.md             # 文档索引与阅读指南
│   ├── product/              # 产品文档
│   ├── architecture/         # 架构与技术文档
│   └── process/              # 流程与协作文档
│
├── backend/                  # Python 后端
│   ├── main.py               # FastAPI 应用入口
│   ├── core/                 # 核心业务逻辑
│   ├── configs/              # YAML 配置文件
│   ├── requirements.txt      # Python 依赖
│   └── tests/                # 后端测试
│
├── frontend/                 # React 前端
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── components/       # 公共组件
│       └── pages/            # 页面组件
│
├── .gitignore
└── start.bat                 # 启动脚本
```

## 文档目录规范

- `[MUST]` `docs/` 按以下子目录归档:
  | 子目录 | 归档内容 |
  |--------|---------|
  | `product/` | 产品需求 |
  | `architecture/` | 架构设计、技术选型 |
  | `process/` | 团队协作、工作流 |

- `[MUST]` `docs/README.md` 文档索引必须存在
- `[MUST]` 文档文件名: `UPPER-KEBAB-CASE.md`
- `[MUST]` 规范文件: `数字前缀-kebab-case.md`

## .gitignore 规范

- `[MUST]` 以下必须排除:
  ```gitignore
  node_modules/
  dist/
  __pycache__/
  *.pyc
  .env
  .env.*
  *.pem
  *.key
  ```
