## Spec: Agent 工具调用标注模块

**编号**: SPEC-004
**状态**: Implemented
**日期**: 2026-02-01
**作者**: Team Fullstack

### 一、问题陈述（Why）

DataOps Studio 现有标注模块支持 5 种 RLHF 标注类型（ranking、dpo、kto、sft、reward），但不支持 Agent 工具调用场景的标注。团队需要对 AI Agent 的工具调用进行质量评估——判断 Agent 是否选对了工具、参数是否正确、调用时机是否恰当。参考工程 S-test 已有成熟方案，需要将此能力集成到 DataOps Studio 中。

### 二、目标与成功标准（DoD）

- [x] **后端 API**: 新增 Agent 工具调用标注相关端点（会话管理 + 标注 + 统计）
- [x] **数据存储**: 使用 SQLite 持久化（会话数据 + 标注记录），重启不丢失
- [x] **多格式导入**: 支持 OpenAI / Anthropic / 自定义格式自动检测与转换
- [x] **YAML 配置**: 新增 `backend/configs/agent-annotation.yaml`（标注维度定义 + 示例数据路径）
- [x] **前端页面 1**: `AgentAnnotation.jsx` — 会话列表页（统计卡片 + 会话卡片 + 文件上传）
- [x] **前端页面 2**: `AgentAnnotationWorkspace.jsx` — 标注工作台（左右分栏：会话上下文 + 标注表单）
- [x] **标注表单**: 正确性（correct/incorrect/uncertain）+ 错误类型 + 严重程度 + 备注
- [x] **路由集成**: `/agent-annotation` → 列表页，`/agent-annotation/workspace/:sessionId` → 工作台
- [x] **侧边栏**: Layout.jsx 新增"Agent标注"菜单项
- [x] **lint + test 通过**: 前后端代码通过格式化和静态检查

### 三、非目标（Out of Scope）

- 不修改现有 RLHF 标注模块（AnnotationTasks / AnnotationWorkspace）
- 不实现用户认证（auth 仍 disabled）
- 不实现标注结果导出 / 下载功能（后续迭代）
- 不实现多人协同标注 / 标注一致性检测（后续迭代）
- 不实现标注任务分配和工作流管理（后续迭代）

### 四、技术方案

#### API 契约

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/agent-annotation/stats` | 统计概览 |
| GET | `/api/agent-annotation/sessions` | 会话列表 |
| GET | `/api/agent-annotation/sessions/{session_id}` | 会话详情 |
| POST | `/api/agent-annotation/sessions/import` | 导入会话（multipart/form-data） |
| GET | `/api/agent-annotation/sessions/{session_id}/tool-calls` | 工具调用列表（含标注） |
| POST | `/api/agent-annotation/annotations` | 提交标注 |
| GET | `/api/agent-annotation/annotations?session_id=xxx` | 标注列表 |

#### 文件清单

| 操作 | 文件 | 职责 |
|------|------|------|
| 新增 | `backend/agent_annotation.py` | API 路由 + SQLite 操作（APIRouter，挂载到 main.py） |
| 新增 | `backend/agent_importers.py` | 多格式导入器（OpenAI/Anthropic/Custom 自动检测） |
| 新增 | `backend/configs/agent-annotation.yaml` | 标注维度定义 + 示例数据配置 |
| 新增 | `frontend/src/pages/AgentAnnotation.jsx` | 会话列表页 |
| 新增 | `frontend/src/pages/AgentAnnotationWorkspace.jsx` | 标注工作台页 |
| 修改 | `frontend/src/App.jsx` | 添加路由 |
| 修改 | `frontend/src/components/Layout.jsx` | 添加菜单项 |
| 修改 | `backend/main.py` | include_router 挂载新模块 |

#### SQLite 数据模型

**agent_sessions 表:**
- session_id TEXT PRIMARY KEY
- created_at TEXT
- model TEXT
- metadata TEXT (JSON 序列化)
- messages TEXT (JSON 序列化)

**agent_annotations 表:**
- id TEXT PRIMARY KEY
- session_id TEXT (外键)
- message_index INTEGER
- tool_call_index INTEGER
- annotator TEXT DEFAULT 'default_user'
- correctness TEXT (correct/incorrect/uncertain)
- error_type TEXT (wrong_tool/wrong_params/wrong_timing/redundant/missing, 可空)
- severity TEXT (critical/major/minor/trivial, 可空)
- comment TEXT (可空)
- created_at TEXT

数据库文件位置: `backend/data/agent_annotation.db`（自动创建）

#### 多格式导入器

采用 S-test 的 ImporterRegistry 模式：
- OpenAIImporter: 检测 messages + role + content → 置信度评分
- AnthropicImporter: 检测 created_at + model 以 claude 开头 → 置信度评分
- CustomImporter: 检测 trace_id + conversation_turns → 置信度评分
- 最高置信度 ≥ 0.5 时选用对应 importer，否则报错

### 五、交互设计（UX）

#### 页面 1: 会话列表页 `/agent-annotation`

**布局:** 统计卡片行 + 上传区 + 会话卡片列表

**统计卡片 (Row, 4列):**
- 会话数 | 工具调用数 | 已标注数 | 标注率(%)

**上传区:** Ant Design Upload.Dragger, 接受 .json 文件

**会话卡片:** Card 列表，每个卡片显示:
- Session ID + Model 名称
- 消息数 / 工具调用数 / 已标注数
- 创建时间
- "开始标注" 按钮 → 跳转到工作台

**页面状态:** 加载(Spin) / 空数据(Empty + 引导上传) / 错误(message.error)

#### 页面 2: 标注工作台 `/agent-annotation/workspace/:sessionId`

**布局:** Row > Col 左右分栏 (12:12)

**左栏 — 会话上下文:**
- 消息列表，按角色着色（user 蓝色 / assistant 绿色 / tool 橙色）
- 工具调用内联显示，可点击高亮选中
- 选中的工具调用有边框高亮

**右栏 — 标注面板:**
- 未选择时: 提示"请在左侧点击工具调用"
- 选中后:
  - 工具名称 + ID
  - 参数 JSON 格式化展示（pre 标签）
  - 标注表单: Radio(正确性) + Select(错误类型, 条件显示) + Select(严重程度, 条件显示) + TextArea(备注)
  - 提交按钮
  - 已有标注列表（Tag 形式展示）

### 六、风险清单

| 维度 | 风险描述 | 优先级 | 应对策略 | 决策 |
|------|---------|--------|---------|------|
| 故障场景 | 大文件上传（>10MB）导致内存溢出 | P1 | 后端限制 10MB，前端 beforeUpload 校验 | 接受 |
| 安全风险 | JSON content 渲染 XSS | P1 | 纯文本渲染，不用 dangerouslySetInnerHTML | 接受 |
| 边缘情况 | 会话无工具调用时工作台空白 | P1 | Empty 组件提示"此会话无工具调用" | 接受 |
| 边缘情况 | 重复导入同一会话 ID | P1 | SQLite INSERT OR REPLACE 覆盖 + 前端提示 | 接受 |
| API 契约 | 前后端枚举值不一致 | P1 | 硬编码对齐，初期不配置化 | 接受 |
| 规模假设 | SQLite 万级数据查询慢 | P2 | 当前可接受，后续加索引或迁移 | 接受 |

### 七、决策记录

| 决策项 | 选项 | 结论 | 理由 |
|--------|------|------|------|
| 数据存储 | A: 内存+YAML B: SQLite | B: SQLite | 标注数据需要持久化，重启不丢失；后续可平滑迁移到更大的数据库 |
| 导入格式 | A: 仅统一格式 B: 多格式自动检测 | B: 多格式自动检测 | 与 S-test 参考实现一致，提升数据源兼容性 |
