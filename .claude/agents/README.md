# Agent Team 架构

> **作者**: Baoxing Huai
> **状态**: Active

## 概述

DataOps Studio 采用 **Agent Team** 模式组织 AI 辅助开发。每位开发者拥有一个 **Leader Agent** (主 Claude Code 会话)，Leader 通过 Task 工具派生 **Sub-Agent** 完成专项任务。

## 团队结构

```
┌──────────────────────────────────────────────────────────────────────────┐
│                            DataOps Studio                                │
├───────────────┬───────────────┬──────────────────┬──────────────────────┤
│   Team A      │   Team B      │   Team C         │   Team D             │
│   Frontend    │   Backend     │   Infrastructure │   QA & Annotation    │
│   (Baoxing)   │   (Junjie)    │   (Sihao)        │   (Feng Wen)         │
├───────────────┼───────────────┼──────────────────┼──────────────────────┤
│ Leader Agent  │ Leader Agent  │ Leader Agent     │ Leader Agent          │
│ ├─ UI Builder │ ├─ API Builder│ ├─ Config Builder│ ├─ E2E Test Runner    │
│ ├─ Test Runner│ ├─ Test Runner│ ├─ CI Builder    │ ├─ Annotation Auditor │
│ ├─ Style Check│ ├─ Config Read│ ├─ Test Framework│ ├─ Data Validator     │
│ └─ Explorer   │ └─ Explorer   │ └─ Explorer      │ └─ Explorer           │
└───────────────┴───────────────┴──────────────────┴──────────────────────┘
```

## 核心概念

### Leader Agent

Leader Agent = 开发者的主 Claude Code 会话，负责:

- **需求理解**: 解析用户意图，拆解为可执行的子任务
- **任务派发**: 通过 Task 工具创建 Sub-Agent，并传递清晰指令
- **质量审查**: 审查 Sub-Agent 产出，确保符合工程规范
- **跨 Team 协调**: 处理跨团队依赖、解决冲突
- **Git 操作**: 负责 branch/commit/PR 等版本控制操作

### Sub-Agent

Sub-Agent = Task 工具派生的专项代理，每类 Sub-Agent 具备:

- **明确的指令模板**: 预定义的 prompt 模板，包含角色、目标、约束
- **限定的工作目录**: 只在指定目录范围内操作
- **可用工具列表**: 根据任务类型限定可用工具

### 工作流程

```
开发者输入需求
    ↓
Leader Agent 理解 & 拆解
    ↓
派发 Sub-Agent (Task 工具)
    ├── Sub-Agent 1: 执行子任务 A
    ├── Sub-Agent 2: 执行子任务 B (可并行)
    └── Sub-Agent 3: 执行子任务 C
    ↓
Leader Agent 审查 & 集成
    ↓
Git commit / PR
```

## 跨 Team 协作原则

1. **文件即通信**: 通过 Git 仓库文件协作，无直接通信通道
2. **契约即边界**: API 契约 + YAML Schema 是唯一耦合点
3. **Mock-First**: 等待依赖时用 Mock 先行开发
4. **每日节奏**: 站会(人工) → Leader 拉取最新 → 分配 Sub-Agent → 集成 → PR

详见 [INTER-TEAM-PROTOCOL.md](INTER-TEAM-PROTOCOL.md)

## 快速上手

1. 阅读你所在 Team 的定义文件 (TEAM-A/B/C)
2. 了解 Leader Agent 的职责和 Sub-Agent 的类型
3. 在日常开发中，由 Leader Agent 根据任务自动选择合适的 Sub-Agent
4. 跨 Team 协作时，参考 [INTER-TEAM-PROTOCOL.md](INTER-TEAM-PROTOCOL.md)

## 文件索引

| 文件 | 内容 |
|------|------|
| [TEAM-A-FRONTEND.md](TEAM-A-FRONTEND.md) | 前端 Team 定义 (Baoxing) |
| [TEAM-B-BACKEND.md](TEAM-B-BACKEND.md) | 后端 Team 定义 (Junjie) |
| [TEAM-C-INFRA.md](TEAM-C-INFRA.md) | 基建 Team 定义 (Sihao) |
| [TEAM-D-QA.md](TEAM-D-QA.md) | 测试与标注质量 Team 定义 (Feng Wen) |
| [INTER-TEAM-PROTOCOL.md](INTER-TEAM-PROTOCOL.md) | 跨 Team 协作协议 |
