---
description: "快速创建前端页面 — 根据描述生成 React 页面组件"
argument-hint: "<页面描述，例如：创建一个系统设置页面>"
---

# create-page — 快速创建前端页面

根据用户描述快速创建 React 前端页面。

## 输入

用户通过 $ARGUMENTS 描述需要创建的页面，例如：
- "创建一个系统设置页面"
- "新增报表展示页面，包含图表和表格"

## 执行步骤

1. **分析需求**: 从 $ARGUMENTS 中提取页面功能、数据来源、交互方式
2. **读取现有代码**:
   - 读取 `frontend/src/App.jsx` 了解路由结构
   - 读取 `frontend/src/components/Layout.jsx` 了解菜单结构
   - 读取一个现有页面（如 `Dashboard.jsx`）了解代码风格
3. **遵循规范**: 按 `.claude/standards/08-react-components.md` 设计组件
4. **实现代码**:
   - 在 `frontend/src/pages/` 创建页面组件
   - 使用 `export default function PageName()`
   - 实现三态：loading(Spin) → empty(Empty) → data
   - 使用 Ant Design 5 组件
5. **注册路由**: 在 `App.jsx` 添加 Route
6. **添加菜单**: 在 `Layout.jsx` 添加菜单项（选择合适的 icon）
7. **格式化**: 运行 `cd frontend && npx prettier --write src/`

## 约束

- [MUST] 单文件不超过 300 行
- [MUST] 使用函数组件 + Hooks
- [MUST] 优先使用 Ant Design 内置组件
- [SHOULD] 数据获取使用 useCallback + useEffect 模式
- 参考 CLAUDE.md 中的前端规范
