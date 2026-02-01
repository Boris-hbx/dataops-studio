# DataOps Studio - 数据运维平台

## Project Overview

DataOps Studio 是公司内部数据平台 SaaS，提供数据管道管理、数据质量监控、成本分析和数据血缘追踪能力。前后端分离架构，面向数据团队和管理层提供统一的运维视图。

## Tech Stack

- **Backend**: Python 3.12+, FastAPI, uvicorn
- **Frontend**: React 18, Vite 6, Ant Design 5, Recharts
- **Config**: YAML-driven (pipelines, quality rules, permissions)
- **Package Manager**: pip (backend) + npm (frontend)
- **Linting**: ruff (Python), ESLint (JS/JSX)
- **Formatting**: ruff format (Python), Prettier (JS/JSX)
- **Testing**: pytest (backend), Vitest (frontend)
- **CI**: GitHub Actions

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

## Commands

```bash
# 后端
cd backend && pip install -r requirements.txt
cd backend && python -m uvicorn main:app --reload --port 8000

# 前端
cd frontend && npm install
cd frontend && npx vite --port 6660

# 格式化
cd backend && ruff format .
cd frontend && npx prettier --write src/

# Lint
cd backend && ruff check .
cd frontend && npx eslint src/

# 测试
cd backend && pytest
cd frontend && npx vitest run
```

## Important Files

- `docs/README.md` — 文档索引与阅读指南
- `docs/product/PRD.md` — 产品需求文档
- `docs/architecture/EXECUTION-PLAN.md` — 架构设计、角色分工、排期
- `docs/architecture/TECH-STANDARDS.md` — 技术栈与编码规范
- `docs/process/COLLABORATION-GUIDE.md` — 团队协作流程
- `.claude/standards/` — 工程规范 (MUST/SHOULD/MAY)
- `.claude/commands/agents/` — 能力域 Agent 定义（架构、UX、安全、风控、审查、全栈、复盘 + 个人画像）
- `.claude/commands/team-template.md` — 团队编排模板（六幕流程）
- `.claude/commands/quick-review.md` — 快速审查命令
- `.claude/agents/README.md` — Agent 系统架构总览
- `.claude/agents/INTER-TEAM-PROTOCOL.md` — 跨团队协作协议
