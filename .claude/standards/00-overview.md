# 00 - 工程规范总览

## 约束等级定义

| 等级 | 标记 | 含义 | 违反后果 |
|------|------|------|---------|
| **MUST** | `[MUST]` | 必须遵守，严禁违反 | CI 自动拒绝，PR 不可合并 |
| **SHOULD** | `[SHOULD]` | 应该遵守 | PR 中说明理由后可豁免，需 Reviewer 确认 |
| **MAY** | `[MAY]` | 建议遵守 | 团队共识后可调整 |

## 规范变更流程

1. MUST 级规范变更需要 **全员一致同意** + Sponsor 审批
2. SHOULD 级规范变更需要 **2/3 团队成员同意**
3. MAY 级规范变更需要 **任意 1 名成员提 PR + 1 人 Review**

## 规范文件索引

| 文件 | 覆盖范围 |
|------|---------|
| `01-code-style.md` | Python/React 命名、格式化、文件组织 |
| `02-error-handling.md` | 错误处理、日志、异常策略 |
| `03-testing.md` | 测试策略、覆盖率、Mock |
| `04-git-workflow.md` | 分支、提交、PR、Review |
| `05-directory-structure.md` | 目录结构与文件归档 |
| `06-infrastructure.md` | 端口注册表、基础设施常量、环境变量 |
| `99-quick-ref.md` | 日常开发速查表 |

## 适用范围

本规范适用于 DataOps Studio 项目全部 Python 后端代码、React 前端代码、YAML 配置文件、CI/CD 配置和文档。
