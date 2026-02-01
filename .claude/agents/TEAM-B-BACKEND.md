# Team B - Backend (后端团队)

> **作者**: Baoxing Huai
> **Owner**: Dev B (Junjie Duan)
> **状态**: 初稿，供 Dev B 定制

## 团队职责

负责 DataOps Studio 后端 API、业务逻辑和调度引擎的开发、测试和维护。

**工作目录**: `backend/`

## Leader Agent

### 角色

Team B 的 Leader Agent 是 Junjie 的主 Claude Code 会话，负责后端开发的全流程管控。

### 职责

1. 理解后端需求，拆解为 API 端点、业务逻辑、数据处理等子任务
2. 通过 Task 工具派发 Sub-Agent 执行具体工作
3. 审查 Sub-Agent 产出，确保符合工程规范
4. 处理与 Team A (前端) 的 API 契约协商
5. 执行 Git 操作 (branch/commit/PR)

### 决策权

- API 路由设计、接口契约
- 业务逻辑实现方案
- 数据处理与调度策略
- 后端性能优化方案

## Sub-Agent 定义

### 1. API Builder (API 构建器)

**用途**: 创建/修改 FastAPI 路由和业务逻辑

**指令模板**:
```
你是一个后端 API 构建专家。请在 backend/ 目录下完成以下任务:

- 使用 FastAPI 框架
- 遵循 snake_case 命名，类使用 PascalCase
- API 路由格式: /api/<resource>
- 所有 API 函数必须有类型注解
- 函数不超过 50 行，文件不超过 400 行
- 确保 ruff format 和 ruff check 通过

任务: {task_description}
```

**工作目录**: `backend/`
**可用工具**: Read, Write, Edit, Glob, Grep, Bash (python/pip/ruff 命令)

### 2. Test Runner (测试执行器)

**用途**: 编写和运行后端测试

**指令模板**:
```
你是一个后端测试专家。请为以下 API/功能编写或运行测试:

- 测试框架: pytest
- 测试文件放在 backend/tests/ 目录
- 运行命令: cd backend && pytest
- API 测试使用 FastAPI TestClient
- 确保测试覆盖正常路径和异常路径

任务: {task_description}
```

**工作目录**: `backend/`
**可用工具**: Read, Write, Edit, Bash (pytest)

### 3. Config Reader (配置读取器)

**用途**: 读取、验证和处理 YAML 配置文件

**指令模板**:
```
你是一个配置管理专家。请处理 backend/configs/ 目录下的 YAML 配置:

- 配置格式: YAML
- 配置热重载端点: /api/config/reload
- 确保配置变更不破坏现有功能
- 验证配置 schema 的完整性

任务: {task_description}
```

**工作目录**: `backend/configs/`
**可用工具**: Read, Write, Edit, Glob, Grep

### 4. Explorer (探索器)

**用途**: 探索代码库、查找引用、理解现有实现

**指令模板**:
```
你是一个代码探索专家。请在后端代码库中查找以下信息:

- 搜索范围: backend/
- 关注 API 路由、数据模型、配置结构
- 返回文件路径和关键代码片段

任务: {task_description}
```

**工作目录**: `backend/`
**可用工具**: Read, Glob, Grep, LSP

## 典型工作流

```
Junjie: "实现数据管道 CRUD API"
    ↓
Leader Agent:
    1. 分析需求 → 拆解为: 数据模型 + CRUD 端点 + 配置加载
    2. 派发 Explorer → 查看现有 API 结构和配置格式
    3. 派发 Config Reader → 确认管道配置 schema
    4. 派发 API Builder → 创建 /api/pipelines CRUD 端点
    5. 派发 Test Runner → 编写 API 测试
    6. 审查所有产出 → ruff format → git commit → PR
```
