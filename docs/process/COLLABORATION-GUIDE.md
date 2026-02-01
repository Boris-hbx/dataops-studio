# DataOps Studio 团队协作指南

**版本**: v1.0
**日期**: 2026-01-31
**作者**: Jianmin Lu
**状态**: Active

## 1. 五条协作原则

| # | 原则 | 含义 |
|---|------|------|
| 1 | **接口即契约** | 三人通过 API 接口和 YAML Schema 连接, 不靠口头约定 |
| 2 | **Mock 即自由** | 前端用 Mock API 开发, 后端用 Mock 数据生成, 互不阻塞 |
| 3 | **Main 即真相** | 每日合入 main, 不在分支里藏代码 |
| 4 | **CI 即仲裁** | lint/format/test 必须通过, 没有例外 |
| 5 | **15 分钟规则** | 卡住 15 分钟就求助, 不要闷头死磕 |

## 2. 代码依赖拓扑 (三人解耦)

```text
              backend/configs/ (共享配置层 — YAML Schema)
             /          |           \
            /           |            \
  frontend/       backend/main.py     backend/core/
    Dev A             Dev B              Dev C
 (前端展示)        (API + 逻辑)       (数据 + 基建)
```

**关键**: 三人代码仅在 YAML 配置 Schema 和 API 接口契约上交汇。Dev A 不导入 backend Python 代码; Dev C 的配置变更通过 API reload 反映到 Dev B。

## 3. 谁给谁提供什么 (Mock-First 开发)

```text
Dev C ───提供 YAML 配置 Schema + 示例数据──→ Dev B
       (D1 交付)

Dev B ───提供 Mock API 响应示例──→ Dev A
       (D1 交付)
       各接口的 JSON 响应格式, 供前端先行开发

Dev A ───提供 UI 反馈──→ Dev B
       (API 响应数据是否充足? 缺什么字段?)

Dev B ───提供配置变更需求──→ Dev C
       (YAML 配置需要新增什么字段?)
```

## 4. 接口变更协议

API 接口和 YAML Schema 锁定后, 任何字段变更需三人同意。

**变更流程**:
1. 发起人在 IM 群发: "[接口变更] /api/dashboard/stats 需要增加 avg_duration 字段, 原因: Dashboard 需展示平均耗时. 影响: A 的卡片渲染 + B 的聚合逻辑"
2. 三人 15 分钟内回复 ✅ 或提出替代方案
3. 全部 ✅ 后发起人修改并提交 PR
4. 各自适配
5. 当天合入 main

## 5. 每日协作节奏

```text
09:00  ┌─ 站会 (15 min, 全员 + Sponsor) ──────┐
       │ 每人 3 句话:                          │
       │ 1. 昨天完成了什么                     │
       │ 2. 今天计划做什么                     │
       │ 3. 有没有阻塞                         │
       └────────────────────────────────────────┘

09:15  ┌─ 独立开发 (用 Mock) ──────────────────┐
~12:00 │ 各自在自己负责的目录开发               │
       │ 遇到问题 → IM 群立刻说, 别攒到站会     │
       └────────────────────────────────────────┘

13:00  ┌─ 独立开发 (续) ──────────────────────┐
~16:00 │ 完成的功能提交 PR                     │
       └────────────────────────────────────────┘

16:00  ┌─ 集成窗口 (30 min) ──────────────────┐
       │ 1. 所有人 push 最新代码                │
       │ 2. 提交 PR 到 main                     │
       │ 3. Reviewer 审查                       │
       │ 4. CI 通过 → Merge                     │
       │ 5. 所有人 git pull main, 验证构建通过  │
       └────────────────────────────────────────┘

16:30  ┌─ Review 时段 (30 min) ────────────────┐
       │ Review 他人 PR, 评论/批准              │
       └────────────────────────────────────────┘
```

## 6. 分支策略

```text
main (保护分支)
  │
  ├── feat/a-dashboard-cards       Dev A: Dashboard 指标卡片
  ├── feat/a-pipeline-table        Dev A: 管道列表表格
  ├── feat/a-quality-page          Dev A: 质量管理页面
  │
  ├── feat/b-dashboard-api         Dev B: Dashboard API
  ├── feat/b-pipeline-api          Dev B: Pipelines API
  ├── feat/b-cost-api              Dev B: Cost API
  │
  ├── feat/c-yaml-schema           Dev C: YAML 配置 Schema
  ├── feat/c-ci-pipeline           Dev C: CI/CD 流水线
  ├── feat/c-test-framework        Dev C: 测试框架搭建
  │
  └── fix/42-api-cors              Bug 修复分支
```

**规则**:
- 一个功能 = 一个分支, 不堆叠
- 分支存活 ≤ 2 天
- 合并后立即删除

## 7. PR Review 流程

```text
开发者提交 PR
    ↓
CI 自动运行 → Fail → 开发者修复 → 重新提交
    ↓ Pass
Reviewer 审查 → 评论 → 开发者修改 → 再审
    ↓ Approved
合入 main (Squash Merge)
    ↓
其他人: git pull main, 验证构建通过
```

**Review 轮转**:

| 提交者 | Reviewer | 备选 |
|--------|----------|------|
| Dev A (Baoxing) | Dev B (Junjie) | Dev C |
| Dev B (Junjie) | Dev C (Sihao) | Dev A |
| Dev C (Sihao) | Dev A (Baoxing) | Dev B |

**响应 SLA**: 2 小时内. 忙碌时备选接手.

**Review 重点 (按优先级)**:

| P0 | 接口契约正确性; 安全问题 (SQL 注入、XSS、密钥泄露) |
| P1 | 错误处理完整性; 关键路径测试覆盖 |
| P2 | 代码可读性 (命名、函数长度) |
| P3 | 性能 (MVP 阶段除非明显问题) |

## 8. Code Ownership

```text
# 共享层 — 任何变更需三人同意
backend/configs/          @baoxing @junjie @sihao

# 各自负责
frontend/                 @baoxing
backend/main.py           @junjie
backend/core/             @junjie

# 基础设施
.github/                  @sihao
start.bat                 @sihao

# 文档
docs/                     @jianmin
.claude/                  @junjie @jianmin
```

## 9. 沟通渠道

| 渠道 | 用途 | SLA |
|------|------|-----|
| **IM 群** | 日常问题、快速确认、接口讨论 | 15 分钟 |
| **IM 私聊** | 一对一技术讨论 | 30 分钟 |
| **GitHub PR 评论** | 代码级讨论 | 2 小时 |
| **GitHub Issue** | Bug 跟踪、功能需求 | 下次站会 |
| **站会** | 进度同步、障碍移除 | 每日 09:00 |
| **紧急会议** | 复杂问题、冲突解决 | 即时 |

## 10. 求助协议 (15 分钟规则)

```text
遇到问题
    ↓
自行排查 (15 分钟)
    ↓
    ├── 解决了 → 继续开发
    │
    └── 没解决 → 发 IM 群
          │
          │ 格式:
          │ "[Help] 问题描述"
          │ "试过: xxx"
          │ "报错: xxx"
          │ "相关代码: 文件:行号"
          │
          ↓
        有人知道 → IM 回复或共享屏幕
        无人知道 → 记 Issue, 临时绕过, 站会讨论
```

**禁止**:
- 闷头卡一上午不说话
- 发模糊消息如 "不行了"
- 不通知 Owner 就改别人负责的代码
