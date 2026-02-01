---
description: "全栈协作团队：前后端协同开发，强调契约对齐和结构化产出"
argument-hint: "<任务描述>"
---

# Team Fullstack — 全栈协作团队

全栈任务的专属编排。七个角色各司其职，确保每个任务都有：
- 结构化的 Spec（规范见 docs/standard/spec-standard.md）
- 前后端契约对齐
- 所有关键决策的 rationale

## 团队配置

### 角色与 Agent 映射

| # | 角色 | Agent 定义 | 职责一句话 |
|---|------|-----------|-----------|
| 1 | 产品负责人（PO） | .claude/agents/agent-product-owner.md | 意图分析 + 目标定义 + DoD 把关 |
| 2 | 架构师 | .claude/agents/agent-architect.md | 技术方案 + API 契约设计 |
| 3 | UX 专家 | .claude/agents/agent-ux.md | 交互设计 + 体验验收 |
| 4 | Challenger | .claude/agents/agent-challenger.md | 挑战假设，识别风险 |
| 5 | 开发者 | general-purpose agent（施工） | 按 Spec 实现代码 |
| 6 | 测试工程师 | .claude/agents/agent-test.md | lint/test 执行 + 覆盖分析 |
| 7 | 审查员 | .claude/agents/agent-reviewer.md | 代码质量 + DoD 验收 |

辅助 Agent（按需召集）：

| Agent 定义 | 何时召集 |
|-----------|---------|
| .claude/agents/agent-security.md | Stage 7 验收涉及 API/认证/输入时 |
| .claude/agents/agent-retrospective.md | Stage 9 生成执行报告 |

### 技术栈与工具链

> 技术栈、lint/test/format 命令、编码规范均定义在 **CLAUDE.md** 中（唯一真相源），本命令不重复定义。

| 项 | 配置 |
|----|------|
| 工作目录 | frontend/src/ + backend/ |
| 验证命令 | 参见 CLAUDE.md → Toolchain Commands |

---

## 工作流程

### 流程图

```
$ARGUMENTS
    │
    ▼
┌──────────────────────────┐
│ Stage 1: PO 初始化        │  产出: Why + DoD + 非目标
│ 👤 领航官(PO)             │
└───────────┬──────────────┘
            │
            ▼
┌──────────────────────────┐
│ Stage 2: 协作设计         │  产出: 技术方案 + 交互设计
│ 👤 架构师 + UX 专家       │
└───────────┬──────────────┘
            │
            ▼
┌──────────────────────────┐
│ Stage 3: 风险质疑         │  产出: 风险清单 (P0/P1/P2)
│ 👤 Challenger            │
└───────────┬──────────────┘
            │
            ▼
┌──────────────────────────┐
│ Stage 4: 方案精炼         │  产出: 更新 Spec + 决策记录
│ 👤 架构师 + UX 专家       │
└───────────┬──────────────┘
            │
            ▼
┌──────────────────────────┐
│ Stage 5: 任务拆解         │  产出: 子任务清单 (TaskCreate)
│ 👤 领航官(PO)             │
└───────────┬──────────────┘
            │
            ▼
┌──────────────────────────┐
│ Stage 6: 施工             │  前端/后端可并行
│ 👤 开发者                 │  联调在双端完成后执行
└───────────┬──────────────┘
            │
            ▼
┌──────────────────────────┐
│ Stage 7: 联合验收         │  测试 + 代码质量 + 交互体验
│ 👤 测试工程师 + 审查员     │  三方同时通过才算通过
│   + UX 专家 (+Security)  │
└───────────┬──────────────┘
            │
       通过? ──否──▶ Stage 8: 迭代修复 (最多 2 轮) ──▶ 回到 Stage 7
            │                👤 开发者 → 对应审查方复验
            ▼
┌──────────────────────────┐
│ Stage 9: PO 确认 + 交付   │  DoD 核实 + Git 提交 + 执行报告
│ 👤 领航官(PO)             │
│   + Retrospective        │
└──────────────────────────┘
```

### Stage 1 — PO 初始化
触发: 用户输入 $ARGUMENTS
参与: **PO（agent-product-owner.md）**
产出: Spec 初始化章节（按 docs/standard/spec-standard.md 模板）

输出：
- 问题陈述（Why）
- 目标与成功标准（DoD）— 必须可验证
- 非目标（Out of Scope）— 明确不做什么
如有待澄清项 → 用 AskUserQuestion 向用户提问。

### Stage 2 — 协作设计
触发: PO 初始化完成
参与: 架构师（agent-architect.md）+ UX 专家（agent-ux.md）
产出: Spec 技术方案 + 交互设计章节

- 架构师：API 契约、后端数据模型、模块划分、Mock 策略
- UX 专家：组件树、状态管理、页面状态方案（Spin / Empty / message.error）
双方需协调一致：UX 方案需架构师确认可实现，API 需考虑前端消费方式。

### Stage 3 — 风险质疑
触发: 设计完成
参与: Challenger（agent-challenger.md）
产出: 风险清单（按维度 + 优先级）

按 agent-challenger.md 中定义的质疑维度逐一检查，输出结构化风险清单。
风险格式参照 docs/standard/spec-standard.md 的风险清单格式。

### Stage 4 — 方案精炼
触发: 风险质疑完成
参与: 架构师（agent-architect.md）+ UX 专家（agent-ux.md）
产出: 更新后的 Spec + 决策记录

逐条回应风险（接受/拒绝/降级），更新 Spec，记录决策 rationale。
P0 风险必须解决后才能进入施工。

### Stage 5 — 任务拆解
触发: 方案精炼完成，P0 风险已解决
参与: **PO（agent-product-owner.md）**
产出: 子任务清单

1. 审核 Spec 完整性（docs/standard/spec-standard.md 的 7 个必要章节全部填写）
2. 拆解为可并行的子任务（前端任务 / 后端任务 / 联调任务）
3. 用 TaskCreate 跟踪，标注依赖关系

### Stage 6 — 施工
触发: 任务拆解完成
参与: 开发者（general-purpose agent）
产出: 代码实现

派遣构建师按子任务施工。
前端和后端任务可并行。联调任务在前后端完成后执行。
遇到 Spec 未覆盖的情况 → 必须回到架构师确认，不擅自决定。

### Stage 7 — 联合验收
触发: 施工完成
参与: 测试工程师（agent-test.md）+ 审查员（agent-reviewer.md）+ UX 专家（agent-ux.md）
辅助: 涉及 API/认证/输入时额外召集 agent-security.md
产出: 联合验收报告

**测试工程师（agent-test.md）：**
1. 按 CLAUDE.md → Toolchain Commands 的"完整验证"命令执行前后端 lint + test
2. 测试覆盖分析：变更代码是否有对应测试？缺失的测试场景？
3. 输出测试报告（执行结果 + 覆盖评估 + 风险评级）

**审查员（agent-reviewer.md）：**
5. 按 agent-reviewer.md 强制检查清单逐项检查代码质量

**UX 专家（agent-ux.md）：**
6. 检查交互实现、状态处理、操作路径

三方需同时通过才算验收完成。

### Stage 8 — 迭代修复（条件触发）
触发: 验收不通过
参与: 开发者（施工修复）→ 对应审查方复验
产出: 修复后的代码

测试问题 → 测试工程师复验。代码问题 → 审查员复验。交互问题 → UX 复验。
最多 2 轮迭代。

### Stage 9 — PO 确认 + 交付
触发: 验收通过
参与: **PO（agent-product-owner.md）** + **agent-retrospective.md**
产出: 任务完成确认 + 执行报告

1. PO 对照 DoD 逐条核实
2. Git add 变更文件（逐个添加），git commit（Conventional Commits）
3. 召集 agent-retrospective.md 生成执行报告
4. 不自动 push，除非用户要求

---

## 错误处理

| 场景 | 处理 |
|------|------|
| 施工遇到 Spec 未覆盖情况 | 回到架构师确认，不擅自决定 |
| Challenger 质疑未被回应 | 阻塞施工，必须先回应 |
| 验收不通过 | 返回施工修复 → 重新验收（最多 2 轮） |
| 前后端契约不一致 | 以 Spec 定义的契约为准，双端对齐 |
| Scope 变更请求 | 必须由 PO 批准或拒绝 |
| 需要其他团队配合 | Mock 先行 + 报告中标记跨团队依赖 |
| Spec 有待澄清项 | AskUserQuestion 向用户提问 |
