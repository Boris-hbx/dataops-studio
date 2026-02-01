---
description: "宝兴的前端团队：组件设计驱动，强调交互体验和前端质量"
argument-hint: "<任务描述>"
---

# Team Baoxing — 前端开发团队

宝兴的前端专属编排。PO 统筹 + UX 驱动设计，确保每个任务都有：
- 结构化的 Spec（规范见 docs/standard/spec-standard.md）
- 清晰的组件树和交互方案
- 前端特有风险的识别与处理
- 所有关键决策的 rationale
- **Spec 文件实时落盘**（每个 Stage 完成后立即写入磁盘，防止断网/崩溃丢失进度）

## 团队配置

### 角色与 Agent 映射

| # | 角色 | Agent 定义 | 职责一句话 |
|---|------|-----------|-----------|
| 1 | 产品负责人（PO） | .claude/agents/agent-product-owner.md | 意图分析 + 目标定义 + DoD 把关 |
| 2 | UX 专家 | .claude/agents/agent-ux.md | 主导交互设计 + 体验验收 |
| 3 | 架构师 | .claude/agents/agent-architect.md | 组件结构 + 数据流设计 |
| 4 | Challenger | .claude/agents/agent-challenger.md | 挑战假设，识别前端风险 |
| 5 | 开发者 | general-purpose agent（施工） | 按 Spec 实现代码 |
| 6 | 测试工程师 | .claude/agents/agent-test.md | lint/test 执行 + 覆盖分析 |
| 7 | 审查员 | .claude/agents/agent-reviewer.md | 代码质量 + DoD 验收 |

辅助 Agent（每次验收必须召集）：

| Agent 定义 | 说明 |
|-----------|------|
| .claude/agents/agent-security.md | 前端安全常驻：XSS、用户输入、敏感数据渲染 |
| .claude/agents/agent-retrospective.md | 交付阶段生成执行报告 |

### 技术栈与工具链

> 技术栈、lint/test/format 命令、编码规范均定义在 **CLAUDE.md** 中（唯一真相源），本命令不重复定义。

| 项 | 配置 |
|----|------|
| 工作目录 | frontend/src/ only |
| 验证命令 | 参见 CLAUDE.md → Toolchain Commands → 前端列 |

### 后端依赖策略

本团队不实现后端代码。遇到后端 API 依赖时：
1. **Mock-First** — 在 frontend/src/mock/ 下创建 Mock 数据，结构与预期 API 响应一致
2. **契约先行** — 在 Spec 中定义预期的 API 契约（方法、路径、参数、响应结构）
3. **跨团队标记** — 在执行报告中标注需 Team B 实现的 API 端点
4. **Vite 代理** — /api/* → localhost:8000（后端就绪后直接切换）

### Spec 落盘策略

**每个 Stage 完成后，必须立即将该阶段产出写入 Spec 文件。**

文件路径: `docs/spec/SPEC-{序号}-{功能名}.md`
格式: 按 docs/standard/spec-standard.md 模板

目的：
- 应对断网/崩溃/上下文溢出等意外中断
- 任何时刻读取 Spec 文件即可知道当前进度
- 新会话可从 Spec 文件中恢复，继续未完成的阶段

落盘时机：
| Stage | 写入内容 |
|-------|---------|
| Stage 0 完成 | 创建 Spec 文件，写入任务定义 + 侦察发现 + Why + DoD + 非目标 |
| Stage 1 完成 | 追加技术方案 + 交互设计 |
| Stage 2 完成 | 追加风险清单 |
| Stage 3 完成 | 更新方案 + 追加决策记录 |
| Stage 8 完成 | 更新状态为 Implemented，标记所有 DoD |

---

## 工作流程

### 流程图

```
$ARGUMENTS（可能模糊）
    │
    ▼
┌──────────────────────────────┐
│ Stage 0: 意图分析 + PO 初始化 │  侦察代码 + 澄清需求 + Why/DoD/非目标
│ 👤 PO (agent-product-owner)  │  → 创建 Spec 文件（落盘）
└───────────┬──────────────────┘
            │
            ▼
┌──────────────────────────────┐
│ Stage 1: UX 驱动设计          │  UX: 交互方案 + 组件树
│ 👤 UX 专家(主导)              │  架构师: 文件结构 + 数据流
│   + 架构师(辅助)              │  → 更新 Spec 文件（落盘）
└───────────┬──────────────────┘
            │
            ▼
┌──────────────────────────────┐
│ Stage 2: 风险质疑             │  产出: 前端风险清单 (P0/P1/P2)
│ 👤 Challenger                │  → 更新 Spec 文件（落盘）
└───────────┬──────────────────┘
            │
            ▼
┌──────────────────────────────┐
│ Stage 3: 方案精炼             │  产出: 更新方案 + 决策记录
│ 👤 UX 专家 + 架构师           │  → 更新 Spec 文件（落盘）
└───────────┬──────────────────┘
            │
            ▼
┌──────────────────────────────┐
│ Stage 4: 任务拆解             │  产出: 子任务清单 (TaskCreate)
│ 👤 PO (agent-product-owner)  │
└───────────┬──────────────────┘
            │
            ▼
┌──────────────────────────────┐
│ Stage 5: 施工                 │  组件开发，无依赖任务可并行
│ 👤 开发者                     │
└───────────┬──────────────────┘
            │
            ▼
┌──────────────────────────────┐
│ Stage 6: 联合验收             │  测试 + 代码 + 交互 + 安全 四重检查
│ 👤 测试工程师 + 审查员         │  四方同时通过才算通过
│   + UX 专家 + Security       │
└───────────┬──────────────────┘
            │
       通过? ──否──▶ Stage 7: 迭代修复 (最多 2 轮) ──▶ 回到 Stage 6
            │                👤 开发者 → 对应审查方复验
            ▼
┌──────────────────────────────┐
│ Stage 8: PO 确认 + 交付       │  DoD 核实 + Git 提交 + 执行报告
│ 👤 PO (agent-product-owner)  │  → 更新 Spec 状态为 Implemented（落盘）
│   + Retrospective            │
└──────────────────────────────┘
```

### Stage 0 — 意图分析 + PO 初始化
触发: 用户输入 $ARGUMENTS
参与: **PO（agent-product-owner.md）**
产出: 清晰的任务定义 + Spec 文件创建 + Why/DoD/非目标
**落盘**: 创建 Spec 文件，写入任务定义 + 侦察发现 + Why/DoD/非目标，状态为 `Stage 0 - PO 初始化完成`

用户的 prompt 可能模糊（如"优化一下页面"、"加个功能"）。本阶段将模糊输入转化为明确任务并完成目标定义。

**步骤：**
1. **解析用户意图**：从 $ARGUMENTS 中提取关键词，推断用户想要什么
2. **侦察代码**：用 Explore agent 搜索相关的现有代码、组件、页面，理解现状
3. **澄清歧义**：如果意图不明确，用 AskUserQuestion 向用户提问：
   - 具体要改哪个页面/组件？
   - 期望的交互行为是什么？
   - 有没有参考的样式/功能？
4. **确定 Spec 编号**：查看 docs/spec/ 下已有的 SPEC 编号，分配下一个编号
5. **创建 Spec 文件并落盘**：`docs/spec/SPEC-{编号}-{功能名}.md`
6. **定义目标**：
   - 问题陈述（Why）
   - 目标与成功标准（DoD）— 必须可验证
   - 非目标（Out of Scope）— 明确不做什么
   - 如需后端 API → 标注为跨团队依赖，规划 Mock 方案

如有待澄清项 → 用 AskUserQuestion 向用户提问。

### Stage 1 — UX 驱动设计
触发: PO 初始化完成
参与: **UX 专家（agent-ux.md）** 主导 + **架构师（agent-architect.md）** 辅助
产出: Spec 交互设计 + 技术方案章节
**落盘**: 更新 Spec 文件，追加技术方案 + 交互设计章节，状态改为 `Stage 1 - 设计完成`

**UX 专家主导：**
- 组件树和层级关系
- 用户操作路径和交互流程
- 每个页面状态方案：加载中(Spin) / 空数据(Empty) / 出错(message.error)
- Props 流向和状态管理方案

**架构师辅助：**
- 文件结构和目录布局（frontend/src/pages/, components/）
- 数据流设计（API 调用 → state → 渲染）
- 如需后端 API → 定义预期契约 + Mock 数据结构
- 可复用资产识别（已有组件/Hook 是否可复用）

UX 方案需架构师确认可实现。架构师不改变交互设计。

### Stage 2 — 风险质疑
触发: 设计完成
参与: **Challenger（agent-challenger.md）**
产出: 前端风险清单（按维度 + 优先级）
**落盘**: 更新 Spec 文件，追加风险清单章节，状态改为 `Stage 2 - 风险质疑完成`

前端专属质疑维度（每次必须覆盖）：
- **渲染性能**: 大数据量列表会卡吗？需要虚拟滚动/分页吗？重渲染控制了吗？
- **状态复杂度**: 状态层级是否过深？是否需要提升到 Context？竞态条件？
- **组件粒度**: 单文件是否超 300 行？职责是否单一？是否需要拆分？
- **安全风险**: 有 dangerouslySetInnerHTML 吗？用户输入直接渲染了吗？
- **边缘情况**: 空数组/null/undefined/超长文本/特殊字符处理了吗？
- **后端依赖**: 依赖的 API 存在吗？不存在的 Mock 准备好了吗？

风险格式参照 docs/standard/spec-standard.md 的风险清单格式。

### Stage 3 — 方案精炼
触发: 风险质疑完成
参与: **UX 专家（agent-ux.md）** + **架构师（agent-architect.md）**
产出: 更新后的 Spec + 决策记录
**落盘**: 更新 Spec 文件，更新方案 + 追加决策记录章节，状态改为 `Stage 3 - 方案定稿`

逐条回应风险（接受/拒绝/降级），更新 Spec，记录决策 rationale。
P0 风险必须解决后才能进入施工。

### Stage 4 — 任务拆解
触发: 方案精炼完成，P0 风险已解决
参与: **PO（agent-product-owner.md）**
产出: 子任务清单

1. 审核 Spec 完整性（docs/standard/spec-standard.md 的 7 个必要章节全部填写）
2. 拆解为可并行的子任务（按组件/页面拆分）
3. 如有 Mock 需求 → 单独拆为一个子任务
4. 用 TaskCreate 跟踪，标注依赖关系

### Stage 5 — 施工
触发: 任务拆解完成
参与: **开发者**（general-purpose agent）
产出: 代码实现

派遣开发者按子任务施工。无依赖的组件可并行开发。
遇到 Spec 未覆盖的情况 → 必须回到 UX 专家/架构师确认，不擅自决定。

### Stage 6 — 联合验收
触发: 施工完成
参与: **测试工程师（agent-test.md）** + **审查员（agent-reviewer.md）** + **UX 专家（agent-ux.md）** + **安全（agent-security.md）**
产出: 联合验收报告

**测试工程师（agent-test.md）：**
1. 按 CLAUDE.md → Toolchain Commands 的"完整验证"前端命令执行 lint + test
2. 测试覆盖分析：变更代码是否有对应测试？缺失的测试场景？
3. 输出测试报告（执行结果 + 覆盖评估 + 风险评级）

**审查员（agent-reviewer.md）：**
5. 按 agent-reviewer.md 强制检查清单逐项检查代码质量

**UX 专家（agent-ux.md）：**
6. 检查交互实现、状态处理、操作路径

**安全（agent-security.md）：**
7. 检查 XSS 风险、用户输入处理、dangerouslySetInnerHTML

四方同时通过才算验收完成。

### Stage 7 — 迭代修复（条件触发）
触发: 验收不通过
参与: **开发者**（施工修复）→ 对应审查方复验
产出: 修复后的代码

测试问题 → 测试工程师复验。代码问题 → 审查员复验。交互问题 → UX 复验。安全问题 → Security 复验。
最多 2 轮迭代。

### Stage 8 — PO 确认 + 交付
触发: 验收通过
参与: **PO（agent-product-owner.md）** + **agent-retrospective.md**
产出: 任务完成确认 + 执行报告
**落盘**: 更新 Spec 文件，状态改为 `Implemented`，DoD 全部打勾

1. PO 对照 DoD 逐条核实
2. Git add 变更文件（逐个添加），git commit（Conventional Commits）
3. 召集 agent-retrospective.md 生成执行报告，包含：
   - 跨团队依赖清单（需 Team B 实现的 API）
   - Mock 文件清单（后端就绪后需替换）
4. 不自动 push，除非用户要求

---

## 错误处理

| 场景 | 处理 |
|------|------|
| 用户 prompt 模糊 | Stage 0 PO 用 AskUserQuestion 澄清，不猜测 |
| 会话中断/崩溃 | 读取 Spec 文件的状态字段，从对应 Stage 恢复 |
| 施工遇到 Spec 未覆盖情况 | 回到 UX 专家/架构师确认，不擅自决定 |
| Challenger 质疑未被回应 | 阻塞施工，必须先回应 |
| 验收不通过 | 返回施工修复 → 重新验收（最多 2 轮） |
| 需要后端 API 但不存在 | Mock-First + Spec 中定义预期契约 + 报告标记跨团队依赖 |
| Scope 变更请求 | 必须由 PO 批准或拒绝 |
