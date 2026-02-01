# 06 - 基础设施规范

> **作者**: Baoxing Huai
> **审核**: Jianmin Lu
> **状态**: Approved

## 端口注册表

- `[MUST]` 所有服务端口遵循以下注册表，严禁未经审批擅自修改:

| 服务 | 端口 | 配置位置 | 说明 |
|------|------|---------|------|
| Frontend Dev Server | `6660` | `vite.config.js`, `start.bat` | Vite 开发服务器 |
| Backend API Server | `8000` | `main.py`, `start.bat` | FastAPI / uvicorn |
| Frontend Proxy | `/api → localhost:8000` | `vite.config.js` | 前端代理后端 API |

## 端口变更流程

- `[MUST]` 端口变更属于 MUST 级规范变更，需要:
  1. **全员一致同意** (Dev A + Dev B + Dev C)
  2. **Sponsor (Jianmin Lu) 审批**
  3. 提交变更 PR 并在 PR 描述中注明变更原因

- `[MUST]` 端口变更时，以下 **6 个位置** 必须同步更新:

| # | 文件 | 需修改内容 |
|---|------|-----------|
| 1 | `frontend/vite.config.js` | `server.port` 值 |
| 2 | `frontend/vite.config.js` | `server.proxy['/api'].target` 端口 (如后端端口变更) |
| 3 | `start.bat` | 前端启动命令中的 `--port` 参数 |
| 4 | `start.bat` | 后端启动命令中的 `--port` 参数 |
| 5 | `.claude/CLAUDE.md` | Commands 段中的端口号 |
| 6 | `.claude/standards/99-quick-ref.md` | 速查表中的端口号 |

- `[MUST]` 端口变更 PR 必须包含 checklist，逐项确认以上 6 个位置已同步

## 端口冲突处理

- `[MUST]` 开发者启动服务前，如遇端口冲突:
  1. **禁止** 随意更换端口启动 — 必须先释放被占用端口
  2. 排查占用进程: `netstat -ano | findstr :<port>` (Windows) 或 `lsof -i :<port>` (macOS/Linux)
  3. 终止占用进程后重新启动
  4. 如确需临时使用其他端口进行本地调试，**不得** 提交端口变更到 Git

- `[SHOULD]` 如果频繁遇到端口冲突，应在站会中提出，由团队讨论是否需要走正式变更流程

## 环境变量规范

- `[MUST]` 密钥、凭据等敏感信息通过 `.env` 文件注入，严禁硬编码
- `[MUST]` `.env` 文件已在 `.gitignore` 中排除，禁止提交到仓库
- `[SHOULD]` 提供 `.env.example` 模板文件，列出所有需要的环境变量 (不含实际值)
