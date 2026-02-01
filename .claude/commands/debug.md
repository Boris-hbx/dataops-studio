---
description: "调试辅助 — 快速诊断和排查常见问题"
argument-hint: "<问题描述，例如：前端页面打不开>"
---

# debug — 调试辅助

快速诊断和排查 DataOps Studio 常见问题。

## 输入

用户通过 $ARGUMENTS 描述遇到的问题，例如：
- "前端页面打不开"
- "API 返回 404"
- "后端启动报错"

## 诊断流程

### 1. 环境检查
- 检查端口占用: `netstat -ano | findstr :8000` (后端) 和 `:6660` (前端)
- 检查进程状态: 确认 uvicorn 和 vite 是否运行

### 2. 后端诊断
- 检查后端日志: 读取终端输出
- 验证 API 可达: `curl http://localhost:8000/docs`
- 检查 YAML 配置加载: `curl http://localhost:8000/api/config/reload`
- 检查 Python 导入: `cd backend && python -c "from main import app; print('OK')"`

### 3. 前端诊断
- 检查 Vite 开发服务器状态
- 检查代理配置: 读取 `frontend/vite.config.js` 确认 proxy target
- 验证前端构建: `cd frontend && npx vite build --mode development 2>&1 | head -20`

### 4. MCP 诊断
- 检查 MCP 配置: 读取 `.claude/mcp.json`
- 检查 MCP 编译: `ls mcp-server-dataops/dist/index.js`
- 验证 MCP 依赖: `cd mcp-server-dataops && node -e "require('./dist/index.js')"`

### 5. 常见问题速查

| 症状 | 可能原因 | 解决方案 |
|------|---------|---------|
| 前端白屏 | Vite 未启动 | `cd frontend && npx vite --port 6660` |
| API 404 | 后端未启动或路由未注册 | 检查 main.py 中 include_router |
| CORS 错误 | 后端 CORS 配置 | 检查 main.py 中 CORSMiddleware |
| 端口被占 | 旧进程未退出 | 找到并结束占用端口的进程 |
| YAML 加载失败 | 配置文件语法错误 | `python -c "import yaml; yaml.safe_load(open('configs/xxx.yaml'))"` |
| MCP 连接失败 | MCP server 未编译 | `cd mcp-server-dataops && npm run build` |

## 输出

诊断完成后输出:
1. 问题定位结论
2. 修复建议或自动修复
3. 验证步骤
