## Spec: Boris 角色创建卡死修复

**编号**: SPEC-007
**状态**: Stage 6 - 已完成
**日期**: 2026-02-02

### 一、问题陈述（Why）

罗马广场页面使用 Boris 设计助手创建角色时，前 2 次正常，第 3 次创建时弹窗内一直转圈无法继续。

**根因**：`sendToBoris` 调用 `readAgentStream` 发起 SSE 流式请求，当 ARK API（火山引擎 Doubao）响应挂起（如速率限制、网络抖动）时：
1. 前端 `reader.read()` 无限阻塞在 while(true) 循环中
2. `borisSending` 状态锁为 true，输入框禁用、按钮 loading
3. 前端无超时机制（后端 read timeout 600s）
4. 用户关闭弹窗不会终止请求（无 AbortController）
5. 用户只能刷新页面才能恢复

**涉及文件**：
- `frontend/src/pages/RomanForum.jsx:24-54` — readAgentStream 函数
- `frontend/src/pages/RomanForum.jsx:219-247` — sendToBoris 函数

### 二、目标与成功标准（DoD）

- [x] Boris SSE 请求增加 30 秒前端超时，超时后自动终止并提示用户
- [x] 用户关闭 Boris 弹窗时自动终止正在进行的请求
- [x] Boris 请求失败或超时后，弹窗恢复可操作状态（可重试发送）
- [x] 不影响已有的手动创建角色流程
- [x] 不影响讨论区的 readAgentStream 调用（讨论可能需要更长时间）
- [x] lint 通过

### 三、非目标（Out of Scope）

- 不修改后端 roman_forum.py 的超时配置
- 不修改讨论区（startDiscuss）的流式读取逻辑
- 不新增组件或文件，在现有文件内修复
- 不修改 Boris prompt 或 AI 对话逻辑

### 四、技术方案（How）

**方案**：给 `readAgentStream` 增加 `AbortSignal` 参数，Boris 调用时传入带超时的 signal。

1. `readAgentStream(agent, topic, history, onChunk, signal)` — 新增可选 `signal` 参数，传递给 `fetch`
2. `sendToBoris` 中创建 `AbortController`，30 秒后自动 abort
3. 将 AbortController 存到 `borisAbortRef`（useRef），关闭弹窗时调用 `abort()`
4. `sendToBoris` 的 catch 分支区分 AbortError 和其他错误，给出不同提示

**数据流**：
```
用户点击发送 → sendToBoris()
  ├─ 创建 AbortController (30s timeout)
  ├─ 存入 borisAbortRef
  ├─ readAgentStream(..., signal) → fetch(/api/forum/discuss, {signal})
  │   ├─ 正常完成 → 解析 suggestion → setBorisSending(false)
  │   ├─ 30s 超时 → AbortError → message.warning("响应超时") → setBorisSending(false)
  │   └─ 其他错误 → message.error("响应失败") → setBorisSending(false)
  └─ 用户关闭弹窗 → borisAbortRef.current.abort() → 同上 AbortError 分支
```

### 五、交互设计（UX）

**状态方案**：
- 正常发送中：Input 禁用 + Button loading（现有行为不变）
- 超时(30s)：自动终止，显示 `message.warning("Boris 响应超时，请重试")`，Input 恢复可用
- 请求失败：显示 `message.error("Boris 响应失败")`（现有行为不变），Input 恢复可用
- 关闭弹窗：静默终止请求，不显示提示

### 六、风险清单与应对

| 维度 | 风险描述 | 优先级 | 应对策略 | 决策 |
|------|---------|--------|---------|------|
| 功能回归 | readAgentStream 签名变更影响讨论区调用 | P0 | signal 参数可选，不传则与现有行为一致 | 接受 |
| 超时体验 | 30s 对复杂角色描述是否太短 | P2 | Boris 单轮回复通常 5-15s，30s 足够宽裕 | 接受 |
| 状态泄漏 | 弹窗关闭后 setState 到已卸载组件 | P1 | abort 后 catch 分支检查弹窗状态再 setState | 接受 |

### 七、决策记录

| 决策项 | 选项 | 结论 | 理由 |
|--------|------|------|------|
| 超时机制 | A: AbortController+setTimeout B: Promise.race | A | AbortController 可同时用于弹窗关闭取消，更统一 |
| 超时时长 | A: 15s B: 30s C: 60s | B: 30s | Boris 回复通常 5-15s，30s 留有余量又不会让用户等太久 |
| 讨论区是否也加超时 | A: 加 B: 不加 | B: 不加 | 讨论区本身有停止按钮，且多轮发言可能更长，属于不同场景 |
