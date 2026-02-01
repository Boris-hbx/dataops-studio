## Spec: 演示增强 — 工程健壮性 + MCP + DataLineage + Skills/Standards

**编号**: SPEC-005
**状态**: In Progress
**日期**: 2026-02-01
**作者**: Team Fullstack

### 一、问题陈述（Why）

DataOps Studio 即将面向三类领导演示。当前工程功能框架完整，但存在以下缺口影响演示效果和工程健壮性：

1. MCP Server 已编译但从未实际运行验证
2. DataLineage 后端 API 已有但前端无可视化页面
3. 工程规范体系（standards）缺少 API 设计规范、React 组件规范
4. Skills 仅 4 个，缺少面向日常开发的高频命令
5. MCP Server 缺少 agent-annotation 模块的 Tools

### 二、目标与成功标准（DoD）

| # | 目标 | 验证方式 |
|---|------|---------|
| 1 | 新建 DataLineage 前端页面，展示数据血缘图 | 浏览器访问 /lineage 可见节点和连线 |
| 2 | MCP Server 补充 agent-annotation tools | 源码新增 tool 定义，npm run build 通过 |
| 3 | 新增 API 设计规范 (07-api-design.md) | 文件存在且覆盖 URL/响应/版本等规则 |
| 4 | 新增 React 组件规范 (08-react-components.md) | 文件存在且覆盖组件结构/Hook/Props 等规则 |
| 5 | 新增 3 个实用 Skills | .claude/commands/ 下新增文件 |
| 6 | 更新 standards 索引 (00-overview.md) | 新增文件已加入索引 |
| 7 | 前后端 lint 通过 | prettier + eslint + ruff format + ruff check 无报错 |

### 三、非目标（Out of Scope）

- 不修改现有页面的 UI 设计
- 不增加后端 API 端点（使用现有 /api/lineage）
- 不实现用户认证
- 不实现 MCP SSE transport

### 四、技术方案

#### DataLineage 页面

- 使用 Ant Design Card + 自定义 CSS 实现简洁的血缘图
- 按层级（ODS → DW → DM）从左到右布局
- 节点按类型着色：ODS 蓝色、DW 绿色、DM 橙色
- 连线显示 pipeline 名称和状态

#### MCP Agent-Annotation Tools

在 `mcp-server-dataops/src/tools/` 新增 `agent-annotation.ts`：
- `get_agent_annotation_stats` — 统计概览
- `list_agent_sessions` — 会话列表
- `get_agent_session_tool_calls` — 获取工具调用列表

#### 新增 Standards

- `07-api-design.md` — API URL 命名、HTTP 方法、响应格式、错误码、分页
- `08-react-components.md` — 组件文件结构、Props 定义、Hook 使用、样式规范

#### 新增 Skills

- `create-api.md` — 快速创建 RESTful API 端点
- `create-page.md` — 快速创建前端页面
- `debug.md` — 调试辅助（查日志、检查端口、验证 API）

### 五、文件清单

| 操作 | 文件 | 职责 |
|------|------|------|
| 新增 | `frontend/src/pages/DataLineage.jsx` | 数据血缘可视化页面 |
| 修改 | `frontend/src/App.jsx` | 添加 /lineage 路由 |
| 修改 | `frontend/src/components/Layout.jsx` | 添加"数据血缘"菜单项 |
| 新增 | `mcp-server-dataops/src/tools/agent-annotation.ts` | MCP agent-annotation tools |
| 修改 | `mcp-server-dataops/src/index.ts` | 注册新 tools |
| 新增 | `.claude/standards/07-api-design.md` | API 设计规范 |
| 新增 | `.claude/standards/08-react-components.md` | React 组件规范 |
| 修改 | `.claude/standards/00-overview.md` | 更新索引 |
| 新增 | `.claude/commands/create-api.md` | 创建 API skill |
| 新增 | `.claude/commands/create-page.md` | 创建页面 skill |
| 新增 | `.claude/commands/debug.md` | 调试 skill |

### 六、风险清单

| 维度 | 风险描述 | 优先级 | 应对策略 |
|------|---------|--------|---------|
| 血缘图复杂度 | 纯 CSS/Canvas 实现复杂图形有限 | P1 | 采用简洁层级布局，不用第三方图库 |
| MCP 编译 | TypeScript 编译可能因依赖版本报错 | P1 | 编译后验证，必要时调整 |

### 七、决策记录

| 决策项 | 结论 | 理由 |
|--------|------|------|
| 血缘图实现方式 | 纯 CSS 层级布局 | 避免引入额外依赖（d3/react-flow），演示够用 |
| MCP tools 范围 | 仅新增 agent-annotation | 其他 14 个 tool 已完备 |
