# 01 - 代码风格规范

## Python 后端

- `[MUST]` 使用 `ruff format` 格式化, 行宽 100
- `[MUST]` 使用 `ruff check` lint, 零警告
- `[MUST]` 公开函数必须有类型注解 (参数 + 返回值)
- `[MUST]` 函数命名 `snake_case`, 类命名 `PascalCase`, 常量 `UPPER_SNAKE_CASE`
- `[SHOULD]` 单个函数不超过 50 行
- `[SHOULD]` 单个文件不超过 400 行, 超出需拆分模块
- `[SHOULD]` 使用 f-string 而非 `.format()` 或 `%`
- `[MAY]` 内部函数使用 `_` 前缀表示私有

## React 前端

- `[MUST]` 使用 Prettier 格式化, 2 空格缩进, 无分号, 单引号
- `[MUST]` 组件文件名 `PascalCase.jsx`, 工具文件 `camelCase.js`
- `[MUST]` 使用函数组件 + Hooks, 禁止 Class 组件
- `[MUST]` 组件 `export default function ComponentName()`
- `[SHOULD]` 单个组件文件不超过 300 行
- `[SHOULD]` props 解构赋值, 不使用 `props.xxx`
- `[SHOULD]` 副作用逻辑放在 `useEffect` 中, 依赖数组准确声明
- `[MAY]` 复杂组件拆分为子组件, 放同级目录

## YAML 配置

- `[MUST]` 2 空格缩进
- `[MUST]` 字符串值使用双引号
- `[MUST]` 文件头部注释说明配置项含义和取值范围
- `[SHOULD]` 字段按逻辑分组, 组间空行分隔
