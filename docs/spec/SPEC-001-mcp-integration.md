## Spec: MCP 集成 — 让 Claude 直接操作 DataOps Studio

**编号**: SPEC-001
**状态**: Draft
**日期**: 2026-02-01
**作者**: Team A (Baoxing Huai)

---

### 功能描述

为 DataOps Studio 构建一个 MCP (Model Context Protocol) Server，使 Claude Desktop / Claude Code 能够直接查询管道状态、质量规则、成本趋势、数据血缘等运维数据，并执行配置热重载、标注提交等操作。MCP Server 作为独立进程运行，通过 HTTP 调用现有 FastAPI 后端 API，不侵入现有代码。

### 用户故事

- 作为 **数据工程师**，我希望在 Claude 对话中直接问"哪些管道今天失败了？"，以便不切换到 Dashboard 就能快速定位问题
- 作为 **数据团队 Leader**，我希望让 Claude 分析各团队的成本和质量指标，以便在周会前快速生成运营摘要
- 作为 **标注管理员**，我希望通过 Claude 查看标注任务进度和质量指标，以便及时发现低质量标注
- 作为 **开发者 (Baoxing)**，我希望在 Claude Code 中直接查询数据血缘，以便开发前端页面时理解数据流向

### 验收标准

- [ ] MCP Server 可通过 `npx` 或 `node` 启动，支持 stdio 传输协议
- [ ] 在 Claude Desktop 的 `claude_desktop_config.json` 中配置后可正常连接
- [ ] 实现至少 5 个 MCP Tools（见下方工具清单）
- [ ] 实现至少 3 个 MCP Resources（见下方资源清单）
- [ ] 所有 Tool 调用后端 API 失败时返回结构化错误信息，不崩溃
- [ ] 提供 `.claude/mcp.json` 配置文件，支持 Claude Code 直接使用
- [ ] README 中包含安装和配置说明

### UI 行为要点

本特性无前端 UI 变更。交互完全发生在 Claude 对话界面中：

- 用户在 Claude 中发出自然语言指令（如"查看失败的管道"）
- Claude 调用对应的 MCP Tool
- MCP Server 请求后端 API，返回结构化数据
- Claude 将数据整理为可读的回答呈现给用户

**典型交互示例**：

```
用户: 今天有哪些管道执行失败了？
Claude: [调用 list_pipeline_executions tool, status=failed, limit=10]
Claude: 今天有 2 条管道执行失败：
  1. risk_score_calc — 02:15 超时（耗时 45 分钟，阈值 30 分钟）
  2. payments_hourly — 08:15 数据源连接失败
  建议检查 risk_score_calc 的 timeout_minutes 配置，以及 payments_hourly 的数据源连通性。
```

### MCP Tools（可执行操作）

| # | Tool 名称 | 对应后端 API | 说明 |
|---|----------|-------------|------|
| 1 | `list_pipelines` | `GET /api/pipelines` | 列出所有管道，支持按 status/owner 筛选 |
| 2 | `get_pipeline_detail` | `GET /api/pipelines/{id}` | 获取管道详情和最近执行记录 |
| 3 | `list_pipeline_executions` | `GET /api/pipelines/{id}/executions` | 获取执行历史，支持 limit 参数 |
| 4 | `get_quality_rules` | `GET /api/quality/rules` | 获取质量规则及 30 天通过率 |
| 5 | `get_quality_checks` | `GET /api/quality/checks` | 获取质量检查结果 |
| 6 | `get_cost_summary` | `GET /api/cost/summary` | 获取成本总览和管道维度分解 |
| 7 | `get_cost_trend` | `GET /api/cost/trend` | 获取 30 天成本趋势 |
| 8 | `get_data_lineage` | `GET /api/lineage` | 获取数据血缘图（节点+边） |
| 9 | `get_dashboard_stats` | `GET /api/dashboard/stats` | 获取仪表盘关键指标 |
| 10 | `get_dashboard_alerts` | `GET /api/dashboard/alerts` | 获取最近告警列表 |
| 11 | `get_team_stats` | `GET /api/teams/stats` | 获取各团队绩效指标 |
| 12 | `list_annotation_tasks` | `GET /api/annotation/tasks` | 列出标注任务及进度 |
| 13 | `get_annotation_quality` | `GET /api/annotation/quality` | 获取标注质量指标 |
| 14 | `reload_config` | `GET /api/config/reload` | 热重载 YAML 配置 |

### MCP Resources（只读数据源）

| # | Resource URI | 对应数据 | 说明 |
|---|-------------|---------|------|
| 1 | `dataops://pipelines` | 管道目录 | 所有管道的基本信息列表 |
| 2 | `dataops://quality/rules` | 质量规则目录 | 所有质量规则定义 |
| 3 | `dataops://lineage` | 数据血缘图 | 完整的节点和边关系 |
| 4 | `dataops://dashboard` | 仪表盘快照 | 关键指标 + 最新告警 |
| 5 | `dataops://teams` | 团队目录 | 各团队及其管道归属 |

### 技术方案

**架构**:

```
Claude Desktop / Claude Code
    ↕ (MCP stdio 协议)
mcp-server-dataops (Node.js / TypeScript)
    ↕ (HTTP fetch)
FastAPI Backend (localhost:8000)
    ↕
YAML configs + 计算逻辑
```

**目录结构**:

```
mcp-server-dataops/
  package.json
  tsconfig.json
  src/
    index.ts           # MCP Server 入口，注册 tools & resources
    client.ts          # 封装后端 API HTTP 调用
    tools/
      pipelines.ts     # list_pipelines, get_pipeline_detail, list_pipeline_executions
      quality.ts       # get_quality_rules, get_quality_checks
      cost.ts          # get_cost_summary, get_cost_trend
      lineage.ts       # get_data_lineage
      dashboard.ts     # get_dashboard_stats, get_dashboard_alerts
      teams.ts         # get_team_stats
      annotation.ts    # list_annotation_tasks, get_annotation_quality
      config.ts        # reload_config
    resources/
      index.ts         # 注册所有 MCP Resources
  README.md
```

**关键技术选型**:

- 语言: TypeScript（与前端技术栈一致，团队熟悉）
- MCP SDK: `@modelcontextprotocol/sdk`
- 传输协议: stdio（Claude Desktop / Claude Code 标准方式）
- HTTP 客户端: 内置 `fetch`（Node 18+）
- 后端地址: 可配置，默认 `http://localhost:8000`

**配置文件**:

`.claude/mcp.json`（供 Claude Code 使用）:
```json
{
  "mcpServers": {
    "dataops-studio": {
      "command": "node",
      "args": ["mcp-server-dataops/dist/index.js"],
      "env": {
        "DATAOPS_API_BASE": "http://localhost:8000"
      }
    }
  }
}
```

`claude_desktop_config.json`（供 Claude Desktop 使用）:
```json
{
  "mcpServers": {
    "dataops-studio": {
      "command": "node",
      "args": ["/absolute/path/to/mcp-server-dataops/dist/index.js"],
      "env": {
        "DATAOPS_API_BASE": "http://localhost:8000"
      }
    }
  }
}
```

### API 需求

**无需新增后端 API**。MCP Server 完全复用现有 FastAPI 端点：

| 已有端点 | MCP Tool 对应 |
|---------|--------------|
| `GET /api/pipelines` | `list_pipelines` |
| `GET /api/pipelines/{id}` | `get_pipeline_detail` |
| `GET /api/pipelines/{id}/executions` | `list_pipeline_executions` |
| `GET /api/quality/rules` | `get_quality_rules` |
| `GET /api/quality/checks` | `get_quality_checks` |
| `GET /api/cost/summary` | `get_cost_summary` |
| `GET /api/cost/trend` | `get_cost_trend` |
| `GET /api/lineage` | `get_data_lineage` |
| `GET /api/dashboard/stats` | `get_dashboard_stats` |
| `GET /api/dashboard/alerts` | `get_dashboard_alerts` |
| `GET /api/teams/stats` | `get_team_stats` |
| `GET /api/annotation/tasks` | `list_annotation_tasks` |
| `GET /api/annotation/quality` | `get_annotation_quality` |
| `GET /api/config/reload` | `reload_config` |

### 跨团队依赖

- **Team B (段俊杰)**: 后端 API 必须在 `localhost:8000` 正常运行。MCP Server 是纯客户端，不影响后端代码
- **Team C (李思浩)**: 如后续需要将 MCP Server 加入 CI/start 脚本，需协调

### 待澄清项

- [ ] 是否需要认证机制？当前后端 API 无认证，MCP Server 也不加。如后续 permission.yaml 启用，需同步
- [ ] 是否需要支持 SSE 传输协议（用于远程部署场景）？MVP 仅支持 stdio
- [ ] `reload_config` 是否需要确认步骤（当前直接执行，无二次确认）？

### 实施建议

**Phase 1 (MVP)**: 实现 5 个核心 Tool + 3 个 Resource
- `list_pipelines`, `get_pipeline_detail`, `get_dashboard_stats`, `get_dashboard_alerts`, `get_data_lineage`
- `dataops://pipelines`, `dataops://lineage`, `dataops://dashboard`

**Phase 2**: 补齐剩余 Tool
- 质量、成本、团队、标注相关 Tool + Resource

**Phase 3**: 增强
- Prompt 模板（如"运营日报生成"、"故障根因分析"）
- SSE 传输支持
- 认证集成
