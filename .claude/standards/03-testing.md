# 03 - 测试规范

## 后端 (pytest)

- `[MUST]` API 路由必须有对应的测试 (使用 FastAPI TestClient)
- `[MUST]` 测试文件命名: `test_<module>.py`
- `[MUST]` 测试函数命名: `test_<功能描述>()`
- `[SHOULD]` 关键业务逻辑 (聚合计算、评分计算) 有单元测试
- `[SHOULD]` YAML 配置加载 + 热重载有测试
- `[MAY]` 测试覆盖率目标 80%+

## 前端 (Vitest)

- `[SHOULD]` 公共组件有渲染测试
- `[SHOULD]` 工具函数有单元测试
- `[MAY]` 页面级组件有 snapshot 测试

## 集成测试

- `[SHOULD]` 前后端联调场景有 E2E 测试覆盖
- `[MAY]` 使用 Playwright 进行浏览器 E2E 测试

## CI 集成

- `[MUST]` PR 合并前所有测试必须通过
- `[MUST]` CI 中同时执行 lint + format check + test
