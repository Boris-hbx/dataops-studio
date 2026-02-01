# 08 - React 组件规范

## 文件结构

- `[MUST]` 一个文件一个组件，使用 `export default function ComponentName()`
- `[MUST]` 文件名与组件名一致，PascalCase: `DataLineage.jsx`
- `[MUST]` 单文件不超过 300 行，超出则拆分子组件
- `[SHOULD]` 页面组件放 `src/pages/`，公共组件放 `src/components/`

## Props 与状态

- `[MUST]` Props 使用 camelCase 命名
- `[MUST]` 事件回调 Props 以 on 开头: `onClick`, `onChange`, `onSubmit`
- `[SHOULD]` 优先使用 useState + useEffect，复杂状态考虑 useReducer
- `[SHOULD]` 数据获取封装在 useCallback 中，useEffect 中调用

## Hooks 使用

- `[MUST]` 自定义 Hook 以 use 开头: `useFetchData`, `useDebounce`
- `[MUST]` useEffect 必须声明依赖数组
- `[SHOULD]` 避免在循环/条件中调用 Hook
- `[SHOULD]` 数据获取模式: loading(Spin) → error(message.error) → empty(Empty) → data

## UI 组件选择

- `[MUST]` 优先使用 Ant Design 5 内置组件
- `[MUST]` 布局使用 Row/Col 或 Flex，不用自定义 Grid
- `[SHOULD]` 表单使用 Ant Design Form 组件
- `[SHOULD]` 消息反馈: 操作成功用 message.success，失败用 message.error
- `[MAY]` 图表使用 Recharts

## 样式

- `[MUST]` 使用 inline style 对象或 Ant Design token，不引入 CSS 文件
- `[SHOULD]` 颜色使用 Ant Design 色板常量或十六进制值
- `[MAY]` 响应式布局使用 Col 的 xs/sm/md/lg 属性
