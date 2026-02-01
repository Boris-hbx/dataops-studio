# Team D - QA & Annotation Quality (测试与标注质量团队)

> **作者**: Feng Wen
> **Owner**: Dev D (Feng Wen)
> **状态**: Active

## 团队职责

负责 DataOps Studio 的端到端测试、标注模块质量保障、数据校验与导出验证。

**工作目录**: `tests/`, `backend/configs/annotation.yaml` (annotation_samples 部分)

## Leader Agent

### 角色

Team D 的 Leader Agent 是 Feng Wen 的主 Claude Code 会话，负责测试与标注质量的全流程管控。

### 职责

1. 理解测试需求，拆解为 E2E 测试、API 测试、数据校验等子任务
2. 通过 Task 工具派发 Sub-Agent 执行具体工作
3. 审查 Sub-Agent 产出，确保测试覆盖率和数据质量
4. 处理与 Team A (前端) 和 Team B (后端) 的集成测试协调
5. 维护标注样本数据的完整性和多样性
6. 执行 Git 操作 (branch/commit/PR)

### 决策权

- 测试策略与用例设计
- 标注样本数据的内容与结构
- 质量指标基线与回归标准
- 测试工具链选型 (已确定: pytest + Vitest)

## Sub-Agent 定义

### 1. E2E Test Runner (端到端测试执行器)

**用途**: 编写和运行跨前后端的端到端测试用例

**指令模板**:
```
你是一个 E2E 测试专家。请为以下功能编写端到端测试:

- 后端测试框架: pytest + httpx (TestClient)
- 前端测试框架: Vitest
- 测试应覆盖完整的用户操作流程
- API 测试关注请求/响应的完整性和边界情况
- 确保测试可重复执行 (无外部依赖)

任务: {task_description}
```

**工作目录**: `tests/`, `backend/`, `frontend/`
**可用工具**: Read, Write, Edit, Bash (pytest, npx vitest)

### 2. Annotation Auditor (标注审核器)

**用途**: 验证标注提交/审核流程的正确性，校验数据一致性

**指令模板**:
```
你是一个标注质量审核专家。请验证以下标注相关功能:

- 标注提交 API: POST /api/annotation/tasks/{task_id}/submit
- 标注审核 API: POST /api/annotation/tasks/{task_id}/review
- 提交列表 API: GET /api/annotation/tasks/{task_id}/submissions
- 验证不同 task_type 的数据结构完整性
- 确保重复提交、非法状态等边界情况的正确处理

任务: {task_description}
```

**工作目录**: `backend/`, `tests/`
**可用工具**: Read, Write, Edit, Bash (curl, pytest)

### 3. Data Validator (数据校验器)

**用途**: 校验 YAML 样本数据的完整性，验证导出数据格式

**指令模板**:
```
你是一个数据校验专家。请对以下数据进行校验:

- YAML 样本数据: backend/configs/annotation.yaml 中 annotation_samples
- 每个样本需有: id, prompt, domain, difficulty, responses
- 每个 response 需有: model, text
- 导出数据需包含所有必要字段
- 验证样本 ID 唯一性、字段值合法性

任务: {task_description}
```

**工作目录**: `backend/configs/`, `tests/`
**可用工具**: Read, Write, Edit, Bash (python), Grep

### 4. Explorer (探索器)

**用途**: 探索代码库、查找测试覆盖盲区、理解现有实现

**指令模板**:
```
你是一个代码探索专家。请在代码库中查找以下信息:

- 搜索范围: 全项目
- 关注 API 端点、数据流、配置加载逻辑
- 识别缺少测试覆盖的关键路径
- 返回文件路径和关键代码片段

任务: {task_description}
```

**工作目录**: 全项目
**可用工具**: Read, Glob, Grep, LSP

## 典型工作流

```
Feng Wen: "验证标注提交到审核的完整流程"
    ↓
Leader Agent:
    1. 分析需求 → 拆解为: API 测试 + 数据校验 + 流程验证
    2. 派发 Explorer → 查看标注 API 端点和数据结构
    3. 派发 Data Validator → 校验 YAML 样本数据完整性
    4. 派发 Annotation Auditor → 测试提交/审核 API 流程
    5. 派发 E2E Test Runner → 编写端到端测试用例
    6. 审查所有产出 → git commit → PR
```

## 与其他 Team 的协作

| 协作方向 | 内容 |
|---------|------|
| Team D → Team A | 前端标注页面的交互测试反馈 |
| Team D → Team B | 标注 API 的边界场景 Bug 报告 |
| Team D → Team C | 标注样本数据的 schema 变更需求 |
| Team B → Team D | 新增 API 端点的测试需求 |
| Team C → Team D | YAML 配置变更后的回归验证需求 |
