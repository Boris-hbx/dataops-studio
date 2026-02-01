# Team C - Infrastructure (基建团队)

> **作者**: Baoxing Huai
> **Owner**: Dev C (Sihao Li)
> **状态**: 初稿，供 Dev C 定制

## 团队职责

负责 DataOps Studio 的数据层、配置管理、CI/CD 和基础设施的开发和维护。

**工作目录**: `backend/configs/`, `.github/`, 项目根目录配置文件

## Leader Agent

### 角色

Team C 的 Leader Agent 是 Sihao 的主 Claude Code 会话，负责基建和 DevOps 的全流程管控。

### 职责

1. 理解基建需求，拆解为配置管理、CI/CD、测试框架等子任务
2. 通过 Task 工具派发 Sub-Agent 执行具体工作
3. 审查 Sub-Agent 产出，确保符合工程规范
4. 维护跨 Team 共享的配置契约层 (`backend/configs/`)
5. 执行 Git 操作 (branch/commit/PR)

### 决策权

- CI/CD 流水线设计
- 配置文件 schema 定义
- 测试框架和工具选型
- 部署和环境管理策略

## Sub-Agent 定义

### 1. Config Builder (配置构建器)

**用途**: 创建/修改 YAML 配置文件和 schema

**指令模板**:
```
你是一个配置管理专家。请处理项目配置相关任务:

- 配置格式: YAML
- 配置目录: backend/configs/
- 配置是前后端共享的契约层，变更需通知 Team A 和 Team B
- 确保 schema 完整且向后兼容

任务: {task_description}
```

**工作目录**: `backend/configs/`
**可用工具**: Read, Write, Edit, Glob, Grep

### 2. CI Builder (CI 构建器)

**用途**: 创建/修改 GitHub Actions 工作流

**指令模板**:
```
你是一个 CI/CD 专家。请处理 GitHub Actions 相关任务:

- 工作流目录: .github/workflows/
- 需覆盖: lint, test, build 三个阶段
- Python: ruff format + ruff check + pytest
- Frontend: prettier + eslint + vitest
- 确保 CI 与本地开发命令一致

任务: {task_description}
```

**工作目录**: `.github/`
**可用工具**: Read, Write, Edit, Glob, Grep, Bash

### 3. Test Framework (测试框架)

**用途**: 维护和配置测试基础设施

**指令模板**:
```
你是一个测试基础设施专家。请处理测试配置相关任务:

- 后端测试: pytest (backend/tests/)
- 前端测试: Vitest (frontend/)
- 确保测试配置与 CI 一致
- 管理测试依赖和 fixtures

任务: {task_description}
```

**工作目录**: 项目根目录
**可用工具**: Read, Write, Edit, Bash (pytest, vitest)

### 4. Explorer (探索器)

**用途**: 探索配置、CI 和基础设施相关代码

**指令模板**:
```
你是一个基础设施探索专家。请查找以下信息:

- 搜索范围: 项目根目录、.github/、backend/configs/
- 关注配置结构、CI 流程、依赖关系
- 返回文件路径和关键内容

任务: {task_description}
```

**工作目录**: 项目根目录
**可用工具**: Read, Glob, Grep, LSP

## 典型工作流

```
Sihao: "配置 GitHub Actions CI 流水线"
    ↓
Leader Agent:
    1. 分析需求 → 拆解为: lint workflow + test workflow + build workflow
    2. 派发 Explorer → 查看现有项目结构和依赖
    3. 派发 CI Builder → 创建 .github/workflows/ci.yml
    4. 派发 Test Framework → 确认测试配置与 CI 一致
    5. 审查所有产出 → git commit → PR
```
