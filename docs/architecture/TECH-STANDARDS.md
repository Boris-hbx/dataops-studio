# DataOps Studio 技术规范

**版本**: v1.0
**日期**: 2026-01-31
**作者**: Sihao Li
**状态**: Active

## 1. 后端技术规范 (Python)

### 1.1 代码风格

- 格式化工具: `ruff format`
- Lint 工具: `ruff check`
- 行宽: 100 字符
- 缩进: 4 空格
- 字符串: 双引号优先
- 类型注解: 所有公开函数必须有参数和返回值类型注解

### 1.2 命名约定

| 类型 | 风格 | 示例 |
|------|------|------|
| 函数/方法 | snake_case | `get_pipeline()` |
| 变量 | snake_case | `total_cost` |
| 类 | PascalCase | `PipelineConfig` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| 模块 | snake_case | `quality_rules.py` |
| 私有函数 | _snake_case | `_generate_executions()` |

### 1.3 项目结构

```text
backend/
├── main.py              # FastAPI 应用入口, API 路由
├── core/                # 核心业务逻辑
│   ├── __init__.py
│   ├── scheduler/       # 调度引擎 (预留)
│   └── engine/          # 数据处理引擎 (预留)
├── configs/             # YAML 配置文件
│   ├── pipelines.yaml
│   ├── quality.yaml
│   └── permission.yaml
├── requirements.txt     # Python 依赖
└── tests/               # 测试目录
    └── test_api.py
```

### 1.4 API 设计约定

- 路由前缀: `/api/`
- RESTful 风格: GET 获取, POST 创建, PUT 更新, DELETE 删除
- 响应格式: JSON
- 错误响应: `{"detail": "error message"}`
- 列表接口支持 `limit` 参数分页

## 2. 前端技术规范 (React)

### 2.1 代码风格

- 格式化工具: `prettier`
- Lint 工具: `eslint`
- 缩进: 2 空格
- 分号: 不使用
- 引号: 单引号
- JSX 引号: 双引号

### 2.2 命名约定

| 类型 | 风格 | 示例 |
|------|------|------|
| 组件 | PascalCase | `Dashboard.jsx` |
| 函数 | camelCase | `fetchPipelines()` |
| 变量 | camelCase | `totalCost` |
| 常量 | UPPER_SNAKE_CASE | `API_BASE_URL` |
| CSS 类 | kebab-case | `stat-card` |
| 事件处理 | handleXxx | `handleClick` |

### 2.3 项目结构

```text
frontend/
├── index.html
├── package.json
├── vite.config.js
└── src/
    ├── main.jsx           # 应用入口
    ├── App.jsx            # 路由配置
    ├── components/        # 公共组件
    │   └── Layout.jsx
    ├── pages/             # 页面组件 (一页一文件)
    │   ├── Dashboard.jsx
    │   ├── Pipelines.jsx
    │   ├── QualityRules.jsx
    │   └── CostAnalysis.jsx
    ├── services/          # API 调用封装 (预留)
    ├── hooks/             # 自定义 Hooks (预留)
    └── utils/             # 工具函数 (预留)
```

### 2.4 组件规范

- 使用函数组件 + Hooks, 不使用 Class 组件
- 每个页面组件对应一个文件
- 公共组件放 `components/`
- 状态管理: 优先 `useState` + `useEffect`, 复杂场景再引入 Context
- API 调用: 在 `useEffect` 中 fetch, 未来迁移到 `services/` 封装层

## 3. 配置文件规范 (YAML)

### 3.1 文件组织

- 每类配置独立文件: pipelines.yaml, quality.yaml, permission.yaml
- 文件头部注释说明配置项含义和取值范围
- 修改配置后调用 `/api/config/reload` 热重载

### 3.2 字段约定

**Pipeline**:
- `id`: 全局唯一, snake_case
- `status`: `active | paused | failed | degraded`
- `schedule`: 标准 cron 表达式
- `owner`: 团队标识符

**Quality Rule**:
- `id`: QR-NNN 格式
- `severity`: `critical | warning | info`
- `check_type`: `null_check | range_check | uniqueness | freshness | custom_sql`
- `enabled`: boolean

## 4. Git 约定

- Commit 格式: `type(scope): description`
- type: `feat | fix | refactor | test | docs | ci | chore`
- scope: `frontend | backend | config | ci`
- 分支命名: `<type>/<short-description>`
- PR 使用 Squash Merge
