# 跨 Team 协作协议

> **作者**: Baoxing Huai
> **状态**: Active

## 核心原则

### 1. 文件即通信

- 团队之间 **没有** 直接通信通道 (无共享内存、无消息队列)
- 所有协作通过 **Git 仓库文件** 完成
- 变更通过 **PR** 传递，Review 是唯一的正式沟通机制
- Leader Agent 每次开始工作前，先 `git pull` 获取最新代码

### 2. 契约即边界

- **API 契约**: 前后端通过 RESTful API 契约解耦
  - 契约定义在 `docs/architecture/` 中的接口文档
  - 变更 API 契约需要 Team A 和 Team B 双方 Leader 确认
- **YAML Schema**: 配置文件的 schema 是 Team B 和 Team C 的唯一耦合点
  - Schema 定义在 `backend/configs/` 目录
  - 变更 Schema 需要 Team B 和 Team C 双方 Leader 确认

### 3. Mock-First 开发

- 当等待其他 Team 的依赖时，使用 Mock 先行开发
- **前端 Mock**: 在 API 未就绪时，使用本地 Mock 数据开发 UI
- **后端 Mock**: 在配置 schema 未定义时，使用示例 YAML 开发 API
- Mock 数据应尽量贴近真实数据结构，减少后续对接成本

## 每日工作节奏

```
09:00  站会 (人工, 全员)
       ├── 同步进展、阻塞点、当日计划
       └── 确认跨 Team 依赖和优先级
         ↓
09:30  Leader Agent 拉取最新代码
       └── git pull → 检查是否有影响本 Team 的变更
         ↓
10:00  Leader Agent 分配 Sub-Agent 任务
       ├── 根据站会确定的优先级分配
       └── 有依赖时先用 Mock 开工
         ↓
持续    Sub-Agent 执行 → Leader 审查 → 迭代
         ↓
16:00  Leader Agent 集成产出
       ├── 合并 Sub-Agent 的变更
       ├── 运行完整测试
       └── 提交 PR
         ↓
17:00  跨 Team PR Review
       └── 涉及契约变更的 PR 需要对方 Team Leader Review
```

## 协作场景

### 场景 1: 前端需要新 API

```
Team A Leader: 在 PR 描述中说明需要的 API 契约
    ↓
Team B Leader: Review PR → 确认契约可行性
    ↓
Team B: 实现 API (Team A 同时用 Mock 开发前端)
    ↓
Team A: API 就绪后替换 Mock → 集成测试
```

### 场景 2: 配置 Schema 变更

```
Team C Leader: 提交 Schema 变更 PR
    ↓
Team B Leader: Review → 确认后端兼容性
    ↓
Team B: 适配新 Schema
Team C: 更新 CI 测试
```

### 场景 3: 端口或基础设施变更

```
任一 Team Leader: 提出变更需求
    ↓
全员站会讨论 → 一致同意
    ↓
Sponsor 审批
    ↓
Team C: 执行变更，同步 06-infrastructure.md 中列出的所有文件
    ↓
全员验证
```

## 冲突解决

1. **代码冲突**: 由 Leader Agent 在 PR 中解决 merge conflict
2. **契约冲突**: 在站会中由相关 Team Leader 协商，Sponsor 仲裁
3. **优先级冲突**: Sponsor (Jianmin Lu) 有最终决定权

## 共享资源

| 资源 | Owner | 变更流程 |
|------|-------|---------|
| `backend/configs/` | Team C (Sihao) | PR + Team B Review |
| `backend/configs/annotation.yaml` (samples) | Team D (Feng Wen) + Team C | PR + Team B Review |
| `tests/` | Team D (Feng Wen) | PR + Team B Review |
| `docs/` | Sponsor (Jianmin Lu) | PR + 任一 Review |
| `.claude/standards/` | 全员共有 | 按规范等级走变更流程 |
| `.claude/agents/` | 各 Team Owner | PR + Sponsor Review |
