# 白标/API 授权概念设计（#33）

## 概述

将 AI Job Hunter 的核心能力封装为 API，允许第三方平台（招聘网站、HR SaaS、培训机构）集成求职助手功能。

## API 接口定义

### REST API Endpoints

```
POST   /api/v1/profile/analyze       — 解析简历，返回结构化画像
POST   /api/v1/jobs/search            — 搜索职位
POST   /api/v1/jobs/match             — 计算职位匹配度
POST   /api/v1/resume/tailor          — 按 JD 定制简历
POST   /api/v1/cover-letter/generate  — 生成求职信
GET    /api/v1/dashboard              — 获取进度数据
POST   /api/v1/offer/evaluate         — Offer 多维度评估
POST   /api/v1/interview/prep         — 生成面试准备方案
```

### 请求/响应格式
```json
// POST /api/v1/resume/tailor
{
  "profile": { /* 结构化画像 */ },
  "job_description": "JD 文本或 URL",
  "options": {
    "language": "zh-CN",
    "max_length": 2,
    "anti_ai_detection": true
  }
}

// Response
{
  "success": true,
  "data": {
    "resume_md": "# ...",
    "match_score": 87,
    "keyword_coverage": 0.92
  },
  "usage": {
    "tokens_used": 3500,
    "cost": 0.035
  }
}
```

## 认证授权

### API Key 模型
- 每个租户一个 API Key
- Key 绑定到具体权限范围（scopes）
- Rate limiting: 每个 Key 每分钟 N 次

### OAuth 2.0（企业版）
- Client Credentials flow（服务器到服务器）
- Authorization Code flow（用户授权场景）
- PKCE 扩展

### 多租户数据隔离
- 每个租户独立的数据命名空间
- 加密存储（AES-256-GCM）
- 数据保留策略可配置
- 支持 GDPR / PIPL 删除请求

## 计费模型

| Tier | 价格 | 包含 |
|------|------|------|
| Free | ¥0/月 | 100 次 API 调用/月 |
| Starter | ¥999/月 | 5000 次 + 基础 Agent |
| Pro | ¥4,999/月 | 20000 次 + 全部 Agent + 定制 |
| Enterprise | 议价 | 无限制 + SLA + 私有部署 |

## Webhook 回调

```json
{
  "event": "application.status_changed",
  "application_id": "app_xxx",
  "old_status": "applied",
  "new_status": "phone_screen",
  "timestamp": "2026-05-07T10:00:00Z"
}
```

支持事件：`job.discovered`, `application.created`, `interview.scheduled`, `offer.received`

## 白标方案

### 嵌入模式
- iframe / Web Component 嵌入
- 自定义品牌色和 Logo
- 自定义域名（CNAME）

### Headless 模式
- 纯 API 集成
- 第三方自行构建 UI
- SDK（JS/Python/Java）

### 私有部署
- Docker 镜像 / K8s Helm Chart
- 客户自有云部署
- 数据不出客户 VPC

## 技术约束

- API 响应时间 < 3s（P95）
- 可用性 99.9%（Enterprise SLA）
- 支持中文/英文/日文
- PII 数据加密传输（TLS 1.3）
