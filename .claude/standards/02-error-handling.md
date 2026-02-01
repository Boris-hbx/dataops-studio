# 02 - 错误处理规范

## Python 后端

- `[MUST]` API 路由函数使用 FastAPI 的 `HTTPException` 返回错误
- `[MUST]` 不在 API 层 bare `except:`, 必须指定异常类型
- `[MUST]` 配置文件加载失败时抛出明确异常并记录日志, 不静默忽略
- `[SHOULD]` 业务逻辑层使用自定义异常类, 在 API 层统一转换为 HTTP 错误
- `[SHOULD]` 使用 `logging` 或 `print` 记录关键操作 (MVP 阶段允许 print)
- `[MAY]` 引入 `structlog` 结构化日志

## React 前端

- `[MUST]` API 调用使用 `.catch()` 或 `try/catch` 处理错误
- `[MUST]` 数据未加载时显示 loading 状态, 不渲染空数据
- `[SHOULD]` API 错误向用户展示友好提示 (Ant Design `message` 组件)
- `[SHOULD]` 可选链操作符 `?.` 访问可能为空的嵌套属性
- `[MAY]` 引入全局 Error Boundary

## 通用

- `[MUST]` 不在代码中硬编码密钥、密码、Token
- `[MUST]` 不 `catch` 异常后什么都不做 (吞异常)
