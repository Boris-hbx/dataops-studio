---
description: "快速审查：仅执行代码审查和格式化"
argument-hint: "<文件范围或最近的变更>"
---

## 流程

### 1. 确定审查范围
分析 $ARGUMENTS 确定审查目标：
- 指定文件/目录 → 审查指定范围
- "最近变更" → 通过 git diff 确定变更文件
- 无参数 → 审查所有未提交的变更

### 2. 格式化 + Lint
根据文件类型执行：
- Python: `cd backend && ruff format . && ruff check .`
- React: `cd frontend && npx prettier --write src/ && npx eslint --fix src/`

### 3. 代码审查
召集 @agents/agent-reviewer.md 对变更文件进行审查。
按强制检查清单逐项检查。

### 4. 安全审查（如涉及）
如变更涉及以下内容，额外召集 @agents/agent-security.md：
- API 端点、输入校验
- 认证/授权逻辑
- 配置文件、环境变量
- 用户输入渲染

### 5. 输出审查报告
结构化输出：
- 检查项通过/不通过状态
- 问题清单（按严重程度分类）
- 修复建议
