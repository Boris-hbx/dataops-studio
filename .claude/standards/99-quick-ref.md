# 99 - 速查表

## 日常开发命令

```bash
# === 后端 ===
# 安装依赖
cd backend && pip install -r requirements.txt

# 启动 (开发模式, 热重载)
cd backend && python -m uvicorn main:app --reload --port 8000

# 格式化
cd backend && ruff format .

# Lint
cd backend && ruff check .

# 测试
cd backend && pytest

# === 前端 ===
# 安装依赖
cd frontend && npm install

# 启动 (开发模式, 端口 6666)
cd frontend && npx vite --port 6666

# 格式化
cd frontend && npx prettier --write src/

# Lint
cd frontend && npx eslint src/

# 测试
cd frontend && npx vitest run

# 构建
cd frontend && npx vite build

# === 配置热重载 ===
curl http://localhost:8000/api/config/reload
```

## MUST 速查 (严禁违反)

| 规则 | 检查方式 |
|------|---------|
| `ruff format` 通过 | CI 自动 |
| `ruff check` 零警告 | CI 自动 |
| Prettier 格式一致 | CI 自动 |
| 禁止直接 push `main` | GitHub Branch Protection |
| PR 至少 1 人 Review | GitHub 设置 |
| CI 全绿才合并 | GitHub 设置 |
| Conventional Commits | Review |
| API 函数有类型注解 | Review |
| 不硬编码密钥 | Review |

## SHOULD 速查

| 规则 | 备注 |
|------|------|
| Python 函数 ≤ 50 行 | 超出需拆分 |
| Python 文件 ≤ 400 行 | 超出需拆模块 |
| React 组件 ≤ 300 行 | 超出需拆子组件 |
| PR ≤ 400 行 | 大功能拆分 |
| 分支存活 ≤ 2 天 | 及时合并 |

## 职责速查

| 目录 | 职责 | Owner |
|------|------|-------|
| `backend/configs/` | YAML 配置 (共享契约层) | 共有 |
| `frontend/` | 前端展示、用户交互 | Dev A (Baoxing Huai) |
| `backend/main.py` | API 路由、业务逻辑 | Dev B (Junjie Duan) |
| `backend/core/` | 核心引擎、调度 | Dev B (Junjie Duan) |
| `.github/` | CI/CD | Dev C (Sihao Li) |
| `docs/` | 项目文档 | Sponsor (Jianmin Lu) |
