# Agent 市场/插件系统概念设计（#8）

## 概述

开放第三方 Agent 生态，允许社区开发者发布针对特定场景的 Agent 插件。

## 架构设计

### Agent 注册接口
```json
{
  "agent_id": "com.example.finance-resume-agent",
  "name": "金融行业简历专家",
  "version": "1.0.0",
  "author": "example-dev",
  "description": "专门优化金融/投行方向的简历",
  "category": "resume",
  "phase": "3",
  "dependencies": ["resume-architect>=2.0"],
  "permissions": ["Read", "Write"],
  "model_requirement": "sonnet",
  "input_schema": {},
  "output_schema": {},
  "pricing": {
    "model": "free | one_time | subscription | usage_based",
    "amount": 0
  }
}
```

### 能力声明 Schema
- `tools_required`: Agent 需要的工具列表
- `data_access`: 可访问的 docs/data/ 实体
- `side_effects`: 是否可写文件、发网络请求
- `max_tokens_per_run`: 单次调用 token 上限

### 版本管理
- 语义版本号（major.minor.patch）
- 兼容性声明（breaking changes 列表）
- 回滚支持（保留最近 3 个版本）

### 安全沙箱
- 第三方 Agent 默认仅读权限
- 写操作需用户显式授权
- 网络请求需审批
- 不能访问 `.claude/settings.json`
- 不能修改系统 Agent 文件

## 发现机制

### Agent Store
- 按 category/phase 分类
- 用户评分 + 评价
- 使用量排行
- 匹配度推荐（基于用户画像）

### 质量审核
- 代码安全扫描（自动）
- 功能可用性测试（自动）
- 用户反馈系统
- 恶意 Agent 举报和下架机制

## 商业模式

| 模式 | 说明 |
|------|------|
| 免费 | 社区贡献，基础功能 |
| 一次性购买 | 单一场景，买断制 |
| 订阅 | 持续更新和维护 |
| 使用量计费 | 按调用次数/token 计费 |
| 平台抽成 | 平台抽 15-30% |

## 实施路线图

- Phase 1: Agent SDK + 注册接口（内部 Agent 先跑通）
- Phase 2: 沙箱安全 + 权限系统
- Phase 3: Store 前端 + 支付系统
- Phase 4: 社区生态运营
