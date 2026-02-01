---
description: "团队编排模板 — 复制此文件到 ~/.claude/commands/team-<你的名字>.md 后自定义"
argument-hint: "<任务描述>"
---

# 团队编排模板

复制此文件并修改下方 [TODO] 标记的部分。

## 团队配置

- 负责人: [TODO: 你的名字]
- 我的画像: @agents/agent-[TODO].md
- 工作目录: [TODO: frontend/src/ 或 backend/ 或 ...]
- 技术栈: [TODO: React 18 + Ant Design 5 或 Python 3.12 + FastAPI 或 ...]
- lint 命令: [TODO: cd frontend && npx prettier --write src/ && npx eslint --fix src/]
- test 命令: [TODO: cd frontend && npx vitest run]

## 我的专家团（从 @agents/ 中选择你需要的）

| 幕 | 召集的专家 | 说明 |
|----|-----------|------|
| Act 1 需求分析 | @agents/agent-pm.md | 将任务转化为结构化 Spec |
| Act 2 架构设计 | @agents/agent-architect.md + [TODO: 按需加 agent-ux / agent-security / agent-fullstack] | 侦察代码，输出蓝图 |
| Act 3 审核拆解 | 领航官（你自己） | 审核 Spec ↔ 蓝图，拆解子任务 |
| Act 4 施工 | 构建师 (general-purpose agent) | 按子任务施工，可并行 |
| Act 5 质量门禁 | lint/test + @agents/agent-reviewer.md [+ agent-security.md] | 格式化 + 测试 + 审查 |
| Act 6 交付 | @agents/agent-retrospective.md | Git 提交 + 执行报告 |

## 六幕流程

### Act 1 — 需求分析
召集 @agents/agent-pm.md 分析 $ARGUMENTS。
输出结构化 Spec：功能描述 / 用户故事 / 验收标准 / API 需求。
如有待澄清项 → 用 AskUserQuestion 向用户提问。

### Act 2 — 架构设计
召集 @agents/agent-architect.md [+ 其他专家]。
侦察工作目录下的现有代码，输出实施蓝图。

### Act 3 — 领航官审核 + 拆解子任务
你自身执行：
1. 审核 Spec ↔ 蓝图一致性
2. 拆解为可并行的子任务清单
3. 用 TaskCreate 跟踪

### Act 4 — 施工
按子任务清单派遣构建师（general-purpose agent），无依赖的可并行。

### Act 5 — 质量门禁
1. 执行 lint: [TODO: 你的 lint 命令]
2. 执行 test: [TODO: 你的 test 命令]
3. 召集 @agents/agent-reviewer.md 审查变更文件
如不通过 → 返回 Act 4 修复（最多 2 次回退）

### Act 6 — 交付
1. Git add 变更文件（逐个添加），git commit（Conventional Commits）
2. 召集 @agents/agent-retrospective.md 生成执行报告
3. 不自动 push，除非用户要求

## 错误处理
| 场景 | 处理 |
|------|------|
| 构建师报错 | 补充指令重试（最多 2 次） |
| 质量门禁不通过 | 返回 Act 4 修复 → 重新 Act 5（最多 2 次） |
| 需要其他团队 API | Mock 先行 + 报告中标记跨团队依赖 |
| Spec 有待澄清项 | AskUserQuestion 向用户提问 |
