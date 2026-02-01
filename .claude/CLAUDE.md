# DataOps Studio - 数据运维平台

## Project Overview

DataOps Studio 是公司内部数据平台 SaaS，提供数据管道管理、数据质量监控、成本分析和数据血缘追踪能力。前后端分离架构，面向数据团队和管理层提供统一的运维视图。

## Tech Stack

> **唯一真相源**: 以下技术栈定义为项目级常量，所有 team command 和 agent 必须引用此处，不得自行重新定义。

| 端 | 技术栈 | 版本要求 |
|----|--------|---------|
| 前端 | React + Vite + Ant Design + Recharts | React 18, Vite 6, Ant Design 5 |
| 后端 | Python + FastAPI + uvicorn | Python 3.12+ |
| 配置 | YAML-driven (pipelines, quality rules, permissions) | — |
| CI | GitHub Actions | — |

### 前端规范
- 组件: 函数组件 + Hooks, PascalCase, `export default function`
- 文件限制: 单文件 ≤300 行
- 状态管理: useState / useEffect / 自定义 Hook（按需升级到 Context）
- UI 库: Ant Design 内置组件优先（Table, Form, Card, Modal, message, Spin, Empty）

### 后端规范
- API 路由: `/api/<resource>` RESTful 风格
- 配置热重载: 修改 YAML 后通过 `/api/config/reload` 重载
- 文件限制: 单文件 ≤400 行

## Architecture

前后端分离 3 层架构:

```
frontend/           (L1 Presentation)   → React + Ant Design SPA
backend/            (L2 API + Logic)    → FastAPI REST API, YAML 配置驱动
backend/configs/    (L3 Data + Config)  → YAML 配置文件, 数据模型定义
```

四人开发分工:
```
Dev A (Baoxing Huai)  → frontend/       前端所有页面与组件
Dev B (Junjie Duan)   → backend/        后端 API、业务逻辑、调度引擎
Dev C (Sihao Li)      → 数据层 + CI/CD  数据模型、配置管理、基础设施
Dev D (Feng Wen)      → 测试 + 标注质量  E2E 测试、标注模块质量保障、数据校验
```

## Key Conventions

- Python: snake_case (函数/变量), PascalCase (类), UPPER_CASE (常量)
- React: PascalCase (组件), camelCase (函数/变量/props)
- API 路由: `/api/<resource>` RESTful 风格
- 配置文件: YAML 格式, 修改后通过 `/api/config/reload` 热重载
- Commit 格式: `type(scope): description` (Conventional Commits)

## Toolchain Commands

> **唯一真相源**: 以下命令为项目级标准，team command 中引用此处定义，不得自行重新定义。

| 操作 | 前端 | 后端 |
|------|------|------|
| 安装依赖 | `cd frontend && npm install` | `cd backend && pip install -r requirements.txt` |
| 启动开发 | `cd frontend && npx vite --port 6660` | `cd backend && python -m uvicorn main:app --reload --port 8000` |
| 格式化 | `cd frontend && npx prettier --write src/` | `cd backend && ruff format .` |
| Lint | `cd frontend && npx eslint --fix src/` | `cd backend && ruff check .` |
| 测试 | `cd frontend && npx vitest run` | `cd backend && pytest` |
| 完整验证 | `cd frontend && npx prettier --write src/ && npx eslint --fix src/ && npx vitest run` | `cd backend && ruff format . && ruff check . && pytest` |

## Important Files

- `docs/README.md` — 文档索引与阅读指南
- `docs/product/PRD.md` — 产品需求文档
- `docs/architecture/EXECUTION-PLAN.md` — 架构设计、角色分工、排期
- `docs/architecture/TECH-STANDARDS.md` — 技术栈与编码规范
- `docs/process/COLLABORATION-GUIDE.md` — 团队协作流程
- `docs/standard/spec-standard.md` — Spec 规范模板
- `.claude/standards/` — 工程规范 (MUST/SHOULD/MAY)
- `.claude/agents/` — 能力域 Agent 定义（PO、架构、UX、安全、风控、审查、测试、复盘）
- `.claude/commands/team-fullstack.md` — 全栈协作团队编排命令
- `.claude/commands/team-baoxing.md` — 前端团队编排命令
- `.claude/commands/team-template.md` — 团队编排模板
- `.claude/commands/quick-review.md` — 快速审查命令
