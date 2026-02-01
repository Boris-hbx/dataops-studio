# 07 - API 设计规范

## URL 命名

- `[MUST]` 使用 `/api/<resource>` 前缀，资源名用小写复数
- `[MUST]` 路径参数用 snake_case: `/api/pipelines/{pipeline_id}`
- `[SHOULD]` 嵌套资源不超过 2 层: `/api/pipelines/{id}/executions`
- `[MAY]` 使用查询参数做过滤和分页: `?limit=50&status=active`

## HTTP 方法

- `[MUST]` GET 用于读取（幂等），POST 用于创建/操作，PUT 用于全量更新，DELETE 用于删除
- `[MUST]` GET 请求不应有副作用
- `[SHOULD]` 批量操作使用 POST + body 而非多个 DELETE

## 响应格式

- `[MUST]` 成功响应直接返回数据（不包装 {code, data, message}），FastAPI 自动序列化
- `[MUST]` 错误响应使用 HTTPException，包含 detail 字段
- `[SHOULD]` 列表接口返回数组，不做额外包装（除非需要分页信息）
- `[SHOULD]` 分页接口返回 {items: [], total: int, page: int, page_size: int}

## 错误码

- `[MUST]` 400 — 请求参数错误
- `[MUST]` 404 — 资源不存在
- `[MUST]` 422 — 请求体校验失败（FastAPI 自动处理）
- `[MUST]` 500 — 服务端未处理异常
- `[SHOULD]` 错误 detail 使用中文描述，便于前端直接展示

## 配置热重载

- `[MUST]` YAML 配置修改后，通过 GET /api/config/reload 热重载
- `[MUST]` 重载接口返回加载的配置计数，便于验证
- `[SHOULD]` 重载不影响已运行的请求

## 命名约定

- `[MUST]` 请求/响应字段使用 snake_case
- `[SHOULD]` 布尔字段以 is_/has_/can_ 开头: is_active, has_dependency
- `[SHOULD]` 时间字段以 _at 结尾: created_at, updated_at
- `[MAY]` 枚举值用小写下划线: check_type: "null_check"
