## Spec: Team Baoxing 前端团队编排命令

**编号**: SPEC-003
**状态**: Approved
**日期**: 2026-02-01
**作者**: Baoxing Huai

### 一、问题陈述（Why）

宝兴负责 frontend/ 下所有页面与组件开发，需要一个专属的团队编排命令。
team-fullstack 面向前后端协同场景，对纯前端任务过重（包含后端 lint/test、联调阶段等）。
需要一个聚焦前端的编排，强调组件设计、交互体验和前端特有风险。

### 二、目标与成功标准（DoD）

- [x] 创建 `.claude/commands/team-baoxing.md`，可通过 `/team-baoxing <任务>` 调用
- [x] 角色映射表包含 5 个指定 agent：architect、challenger、ux、reviewer、security
- [x] 工作流程图清晰展示阶段流转
- [x] 每个 Stage 标注触发条件、参与 agent、产出
- [x] Challenger 质疑维度针对前端场景定制
- [x] 后端依赖处理策略：Mock-First + 跨团队标记
- [x] Spec 规范引用 docs/standard/spec-standard.md

### 三、非目标（Out of Scope）

- 不实现后端 API（那是 Team B 的事）
- 不配置 CI/CD（那是 Team C 的事）
- 不编写 E2E 测试（那是 Team D 的事）

### 四、技术方案（How）

#### 与 team-fullstack 的差异

| 维度 | team-fullstack | team-baoxing |
|------|---------------|-------------|
| 工作目录 | frontend/ + backend/ | frontend/src/ only |
| lint/test | 双端 | 仅前端 |
| UX 角色权重 | 与架构师平等 | UX 主导设计，架构师辅助 |
| Challenger 维度 | API 契约、故障场景等 | 渲染性能、状态复杂度、XSS 等前端风险 |
| 后端依赖 | 直接实现 | Mock-First + 跨团队标记 |
| Security 角色 | 辅助（按需） | 常驻（前端安全是高频风险） |

#### 文件结构

```
.claude/commands/team-baoxing.md    # 命令文件（本次新增）
docs/spec/SPEC-003-team-baoxing.md  # 本 Spec
```

### 五、交互设计（UX）

N/A（本任务是命令配置，无 UI）

### 六、风险清单与应对

| 维度 | 风险描述 | 优先级 | 应对策略 | 决策 |
|------|---------|--------|---------|------|
| 角色重叠 | UX 与架构师在组件设计上职责模糊 | P1 | 明确：UX 定交互/状态，架构师定文件结构/数据流 | 接受 |
| 后端依赖 | 前端任务可能被后端 API 阻塞 | P1 | Mock-First 策略，前端不等后端 | 接受 |

### 七、决策记录

| 决策项 | 选项 | 结论 | 理由 |
|--------|------|------|------|
| UX vs 架构师主导 | A: 架构师主导 B: UX 主导 C: 平等 | B: UX 主导 | 前端团队的核心价值是用户体验，组件设计应由 UX 驱动 |
| Security 是否常驻 | A: 按需 B: 常驻 | B: 常驻 | 前端直面用户输入，XSS/注入是高频风险 |
| 是否复用 team-fullstack | A: 继承 B: 独立 | B: 独立 | 纯前端场景不需要后端相关阶段，独立更精简 |
