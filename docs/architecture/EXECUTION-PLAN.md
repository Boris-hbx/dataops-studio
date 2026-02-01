# DataOps Studio 架构设计与执行计划

**版本**: v1.0
**日期**: 2026-01-31
**作者**: Junjie Duan
**状态**: Active

## 1. 系统架构

```text
┌──────────────────────────────────────────────────────────┐
│                    L1 Presentation                       │
│              frontend/ (React + Ant Design)              │
│  Dashboard │ Pipelines │ Quality │ Cost │ (future pages) │
├──────────────────────────────────────────────────────────┤
│                     L2 API Layer                         │
│               backend/main.py (FastAPI)                  │
│  /api/dashboard │ /api/pipelines │ /api/quality │ /api/cost │
├──────────────────────────────────────────────────────────┤
│                 L3 Data & Config Layer                   │
│              backend/configs/ (YAML files)               │
│   pipelines.yaml │ quality.yaml │ permission.yaml        │
└──────────────────────────────────────────────────────────┘
```

## 2. 技术选型

| 层次 | 技术 | 选型理由 |
|------|------|---------|
| 前端框架 | React 18 | 生态成熟, 热更新体验好 |
| UI 组件库 | Ant Design 5 | 企业级 UI, 中文友好 |
| 图表库 | Recharts | 声明式 API, 与 React 集成自然 |
| 构建工具 | Vite 6 | 极快的 HMR, 开发体验佳 |
| 后端框架 | FastAPI | 自动文档, 异步支持, 类型提示 |
| 配置管理 | PyYAML | 标准 YAML 解析 |
| 进程管理 | uvicorn | ASGI 服务器, 支持热重载 |

## 3. 三人分工

### 代码依赖拓扑 (四人解耦)

```text
                backend/configs/ (共享配置层)
               /         |          \          \
              /          |           \          \
    frontend/      backend/main.py   backend/core/   tests/ + 标注质量
     Dev A            Dev B            Dev C            Dev D
  (Presentation)   (API + Logic)   (Data + Infra)  (QA + Annotation)
```

**关键原则**: 四人代码仅在 `backend/configs/` (YAML 配置) 和 API 接口契约上交汇。前端只通过 HTTP API 调用后端, 不直接依赖后端 Python 代码。Dev D 横向覆盖端到端测试与标注模块质量。

### Dev A: Baoxing Huai — 前端展示层

**目录**: `frontend/`

**职责**:
- 全局布局 (Layout, 侧边栏, 顶栏)
- Dashboard 页面: 指标卡片、图表、告警列表
- Pipelines 页面: 管道列表、详情弹窗、执行记录
- Quality 页面: 规则列表、评分趋势、检查结果
- Cost 页面: 成本趋势、饼图、团队效能表
- API 调用封装、加载状态、错误处理
- 响应式布局适配

### Dev B: Junjie Duan — 后端 API 与业务逻辑

**目录**: `backend/main.py`, `backend/core/`

**职责**:
- FastAPI 应用搭建、中间件配置
- Dashboard API: 统计聚合、趋势计算、告警生成
- Pipelines API: CRUD、执行历史、成功率计算
- Quality API: 规则管理、检查结果、评分趋势
- Cost API: 成本汇总、管道明细、团队统计
- Lineage API: 血缘关系提取
- 数据模拟引擎: 执行历史、质量检查、告警生成
- 配置热重载接口

### Dev C: Sihao Li — 数据层与基础设施

**目录**: `backend/configs/`, `.github/`, 基础设施脚本

**职责**:
- YAML 配置文件设计与维护 (pipelines, quality, permissions)
- 数据模型定义 (pipeline, execution, quality rule, alert)
- 配置校验逻辑
- CI/CD 流水线 (GitHub Actions)
- 启动脚本 (start.bat)
- 开发环境搭建文档
- 测试框架搭建 (pytest + vitest)
- 代码质量工具链 (ruff, ESLint, Prettier)

### Dev D: Feng Wen — 测试与标注质量

**目录**: `tests/`, `backend/configs/annotation.yaml`, 标注模块相关代码

**职责**:
- E2E 测试: 端到端测试用例编写与维护 (pytest + 前端 Vitest)
- 标注模块质量保障: 标注提交/审核流程验证, 数据一致性校验
- 标注样本数据维护: `annotation.yaml` 中 `annotation_samples` 的扩展与校验
- 标注数据导出验证: 确保导出数据格式与字段完整性
- API 集成测试: 跨模块 API 调用场景的自动化测试
- 质量指标监控: 标注通过率、Kappa 一致性指标的回归验证
- Bug 回归测试: 修复后的回归用例编写

### Sponsor: Jianmin Lu

**职责**:
- 产品需求把控, 优先级调整
- 每日进度检查, 障碍移除
- UX 审查

## 4. 接口契约

前后端通过以下 API 接口通信, 接口一旦锁定, 变更需三人同意:

```text
GET /api/dashboard/stats          → DashboardStats
GET /api/dashboard/execution-trend → ExecutionTrend[]
GET /api/dashboard/alerts          → Alert[]
GET /api/pipelines                 → Pipeline[]
GET /api/pipelines/{id}            → PipelineDetail
GET /api/pipelines/{id}/executions → Execution[]
GET /api/quality/rules             → QualityRule[]
GET /api/quality/checks            → QualityCheck[]
GET /api/quality/score-trend       → ScoreTrend[]
GET /api/cost/summary              → CostSummary
GET /api/cost/trend                → CostTrend[]
GET /api/teams/stats               → TeamStats[]
GET /api/lineage                   → LineageGraph
GET /api/config/reload             → ReloadResult
```

## 5. 开发排期

| 阶段 | 内容 | Dev A | Dev B | Dev C | Dev D |
|------|------|-------|-------|-------|-------|
| D1 | 架构搭建 | Vite + React + 路由 + Layout | FastAPI 骨架 + YAML 加载 | 配置文件设计 + CI 搭建 | 测试框架搭建, 标注样本 schema 设计 |
| D2 | 核心页面 | Dashboard + Pipelines 页面 | Dashboard API + Pipelines API | 数据模拟引擎 | API 冒烟测试, 标注样本数据填充 |
| D3 | 完善功能 | Quality + Cost 页面 | Quality API + Cost API | 测试框架 + 配置校验 | 标注提交/审核 E2E 测试 |
| D4 | 集成联调 | 前后端联调, 样式打磨 | Lineage API + 热重载 | 集成测试 + 启动脚本 | 端到端标注流程验证, 数据导出校验 |
| D5 | 收尾 | 响应式适配, 细节优化 | 性能优化, 错误处理 | E2E 验证, 文档完善 | 回归测试套件, 质量指标基线建立 |
