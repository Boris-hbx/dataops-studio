# Agent 系统架构

> **状态**: Active (v3 — 能力域 Agent + 团队编排分层)
> **Spec**: docs/spec/SPEC-002-agent-system-redesign.md

## 概述

DataOps Studio 采用 **能力域 Agent + 个人编排** 模式组织 AI 辅助开发。

核心理念：Agent 是拥有特定专业能力的专家，由团队编排命令按需召集。

## 三层架构

```
.claude/commands/agents/        → 能力域 Agent（团队共享，进 git）
.claude/commands/team-template.md → 编排模板（团队共享，进 git）
~/.claude/commands/team-*.md    → 个人编排（不进 git，各自维护）
```

| 层级 | 位置 | 共享性 | 作用 |
|------|------|--------|------|
| 能力域 Agent | `commands/agents/` | 团队共享 | 统一的专业能力定义，可 @引用 |
| 编排模板 | `commands/team-template.md` | 团队共享 | 六幕流程标准模板 |
| 个人编排 | `~/.claude/commands/` | 个人 | 各开发者的编排偏好 |
| 快速命令 | `commands/quick-*.md` | 团队共享 | 轻量级通用命令 |

## 能力域 Agent（7 个）

| Agent | 职责 |
|-------|------|
| agent-architect | 系统设计、技术选型、模块划分、API 契约 |
| agent-ux | 组件设计、布局、交互流、状态管理 |
| agent-security | 输入校验、注入防护、错误边界、凭据扫描 |
| agent-pm | 需求分析、范围界定、复杂度评估、MVP 取舍 |
| agent-reviewer | 代码规范、逻辑正确性、性能、可维护性 |
| agent-fullstack | 前后端接口对齐、数据契约、Mock 策略 |
| agent-retrospective | 执行回顾、成果盘点、改进建议 |

## 快速命令

| 命令 | 说明 |
|------|------|
| `/quick-review <范围>` | 格式化 + 代码审查 + 安全审查 |

## 使用方式

```bash
# 首次使用：基于模板创建个人编排
# 1. 查看模板: cat .claude/commands/team-template.md
# 2. 复制到 ~/.claude/commands/team-<你的名字>.md
# 3. 填入你的团队配置和专家选择

# 日常使用
/team-baoxing 实现数据管道列表页面
/quick-build 给 Dashboard 加一个刷新按钮
/quick-review 检查最近修改的代码
```

## 跨团队协作

详见 [INTER-TEAM-PROTOCOL.md](INTER-TEAM-PROTOCOL.md)
