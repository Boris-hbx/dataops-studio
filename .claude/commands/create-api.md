---
description: "快速创建 API 端点 — 根据描述生成 FastAPI 路由"
argument-hint: "<API 描述，例如：创建一个获取用户列表的 API>"
---

# create-api — 快速创建 API 端点

根据用户描述快速创建 FastAPI REST API 端点。

## 输入

用户通过 $ARGUMENTS 描述需要创建的 API，例如：
- "创建一个获取用户列表的 API"
- "新增 /api/reports/daily 返回日报数据"

## 执行步骤

1. **分析需求**: 从 $ARGUMENTS 中提取资源名、HTTP 方法、路径、参数
2. **读取现有代码**: 读取 `backend/main.py` 了解现有 API 模式和数据结构
3. **遵循规范**: 按 `.claude/standards/07-api-design.md` 设计 API
4. **实现代码**:
   - 在 `backend/main.py` 中添加路由函数
   - 使用 snake_case 命名
   - 添加 docstring 说明
   - 遵循现有的数据生成模式（确定性随机）
5. **格式化**: 运行 `cd backend && ruff format . && ruff check .`
6. **验证**: 说明如何测试新 API（curl 命令示例）

## 约束

- [MUST] 遵循 `/api/<resource>` URL 规范
- [MUST] GET 用于查询，POST 用于创建/操作
- [MUST] 使用 FastAPI 类型注解
- [SHOULD] 返回结构与现有 API 风格一致
- 参考 CLAUDE.md 中的后端规范
