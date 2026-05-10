---
name: privacy-config
description: 隐私数据分层授权的配置和执行规则。
type: config
---

# 隐私数据隔离（#35）

## 分层授权模型

求职系统涉及三种隐私层级的数据，必须分层处理：

### Layer 1 — 公开层（可出现在简历/求职信中）
| 字段 | 脱敏规则 |
|------|---------|
| name | 可用英文名/Pinyin |
| email | 专用求职邮箱（非个人主力） |
| phone | 可放（大陆求职必须） |
| skills, work_experience, projects | 完整展示 |
| education | 学校+专业，不含 GPA |
| GitHub / 个人主页 | 完整 URL |

### Layer 2 — 投递层（仅发送给目标公司，不出现在公开渠道）
| 字段 | 脱敏规则 |
|------|---------|
| current_company | 出现但脱敏为"某大厂"（面试阶段再透露） |
| current_salary | 不出现在简历中 |
| detailed_contact | 微信号仅面试阶段提供 |
| references | 仅在 offer 阶段提供 |

### Layer 3 — 内部层（仅本地 docs/data/ 存储，绝不出库）
| 字段 | 保护规则 |
|------|---------|
| phone | 本地存储，简历生成时可选脱敏 |
| salary_expectation | 仅 preferences.json，不对外 |
| dealbreakers | 仅本地，不对外透露 |
| interview_feedback | 仅本地 feedback.json |
| application_history | 仅本地，不上传 |

## 数据写入规则（Agent 手册）

所有 Agent 在写入任何可能对外输出的文档时，必须遵守：

1. **简历生成（resume-architect）：** 
   - 默认生成 Layer 1 版本
   - 用户可选导出含 Layer 2 信息的「投递版」
   - Layer 3 信息永不出现在简历中

2. **求职信生成（cover-letter-writer）：**
   - 不提及当前薪资、具体期望薪资
   - 可用「基于市场水平的薪资期望」代替

3. **职位搜索（job-scout）：**
   - 不在搜索请求中暴露用户真实姓名、邮箱
   - 不在第三方平台以用户身份注册

4. **网络调研（company-researcher, hr-intel）：**
   - 不向第三方透露用户的求职意向
   - 匿名浏览公司页面

5. **面试准备（interview-coach）：**
   - 面试材料仅本地存储
   - 不通过云端共享面试准备内容

## Agent 实现

各 Agent 的隐私合规通过以下方式实现：
- career-coach 在调度时检查输出目标（本地文件 vs 对外发送）
- data-layer.py 的 `view` 命令生成对外视图时自动应用脱敏
- profile.json 中的 `metadata.privacy_level` 字段标记数据敏感度
