# 04 - Git 工作流规范

## 分支策略

- `[MUST]` `main` 分支永远可运行, 禁止直接 push
- `[MUST]` 所有改动通过 PR 合并到 `main`
- `[MUST]` 分支命名: `<type>/<short-description>`
  - `feat/dashboard-cards`
  - `fix/api-cors-error`
  - `refactor/cost-calculation`
- `[SHOULD]` 分支存活不超过 2 天

## Commit 规范

- `[MUST]` 遵循 Conventional Commits:
  ```text
  <type>(<scope>): <description>
  ```
- `[MUST]` type 取值:
  | type | 用途 |
  |------|------|
  | `feat` | 新功能 |
  | `fix` | Bug 修复 |
  | `refactor` | 重构 |
  | `test` | 测试 |
  | `docs` | 文档 |
  | `ci` | CI/CD |
  | `chore` | 构建、依赖 |
- `[MUST]` scope 取值: `frontend`, `backend`, `config`, `ci`
- `[SHOULD]` 单个 commit 只做一件事

## PR 规范

- `[MUST]` PR 标题遵循 Commit 格式
- `[MUST]` PR 至少 1 人 Review 后合并
- `[MUST]` CI 全绿才合并
- `[SHOULD]` PR 描述包含 What / Why / Test
- `[SHOULD]` PR 不超过 400 行, 大功能拆分

## 合并策略

- `[MUST]` 使用 Squash Merge, 保持 main 历史干净
- `[MUST]` 禁止 `git push --force` 到 `main`
