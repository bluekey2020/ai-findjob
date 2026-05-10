# Phase 0-3 审计报告

> 审计人：Richard N. Bolles（career-coach）
> 审计日期：2026-05-06
> 审计范围：Phase 0（入职引导）至 Phase 3（批量定制投递）

---

## 一、数据完整性检查

### 1.1 结构化数据文件

| 实体 | 文件 | 状态 | Schema | 校验结果 |
|------|------|------|--------|---------|
| preferences | `docs/data/preferences.json` | 存在 | 有 | 通过 |
| profile | `docs/data/profile.json` | 存在 | 有 | 通过 |
| jobs | `docs/data/jobs.json` | 存在 | 有 | 通过 |
| companies | `docs/data/companies.json` | 存在 | 有 | 通过 |
| applications | `docs/data/applications.json` | 已补全 | 有 | 通过 |

### 1.2 校验详情

**preferences.json** — 14 维度全覆盖。包括：语言、目标岗位、目标地区、薪资期望、城市偏好、搬迁意愿、签证状态、公司规模偏好、加班容忍度、通知期、底线限制、时效过滤、偏好平台、梦想公司。所有字段类型与 schema 一致。

**profile.json** — 结构化画像完整。包含：基本信息、个人摘要、9个亮点、7个待改进项、25项技能（含等级/年限/分类）、3段工作经历、1份教育经历、4个项目、2门语言。缺少：GitHub 主页链接、社交链接（已在 gaps 中标注）。

**jobs.json** — 20个职位。来源覆盖：Boss直聘（5）、拉勾（3）、猎聘（4）、51job（2）、脉脉（1）、智联招聘（1）、GitHub Issues（2）、V2EX（2）。地区分布：深圳17、远程3。时效：全部14天内发布。7个 Top Picks 均有详细匹配理由。

**companies.json** — 10家公司。覆盖所有面试机会集中的雇主。每家包含：技术栈、文化摘要、财务健康评级、风险信号、机会信号、用户匹配建议。

**applications.json** — 已从空白状态修复。新增 `pipeline_progress` 字段记录 Phase 进展和下一行动项。

---

## 二、Phase 产出清单

### Phase 0: 入职引导

| 产出 | 路径 | 状态 | 质量 |
|------|------|------|------|
| 用户偏好 | `docs/data/preferences.json` | 完成 | 合格 — 14维偏好完整 |
| 偏好视图 | `docs/views/preferences.md` | 完成 | 合格 |

**合规评估：** 偏好数据完整。用户确认环节在前期对话中完成。

### Phase 1: 画像构建

| 产出 | 路径 | 状态 | 质量 |
|------|------|------|------|
| 结构化画像 | `docs/data/profile.json` | 完成 | 优秀 — 25项技能、3段经历、4个项目 |
| 画像视图 | `docs/views/profile.md` | 完成 | 合格 |
| 结构化画像（可读版） | `docs/profile/structured-profile.md` | 完成 | 合格 |
| 技能缺口分析 | `docs/skill-gaps/gap-analysis.md` | 完成 | 优秀 — 含四象限分析和学习路径 |
| 默认简历 | `docs/resume/default.md` | 完成 | 合格 |

**亮点：** 技能缺口报告将技能分为四象限（专家/高级/中级/缺失），每个有可操作的改进路径。profile.json 的 `highlights` 和 `gaps` 字段设计合理，既展示亮点又诚实暴露短板。

**偏差：** profile.json 中缺少 GitHub/个人站点链接（已在 gaps 中标注为待补充）。

### Phase 2: 市场调研与职位发现

| 产出 | 路径 | 状态 | 质量 |
|------|------|------|------|
| 职位数据 | `docs/data/jobs.json` | 完成 | 优秀 — 20个职位，8个平台 |
| 职位视图 | `docs/views/jobs.md` | 完成 | 合格 — 含匹配度和风险警告 |
| Top Picks | `docs/jobs/top-picks.md` | 完成 | 优秀 — 详细的推荐理由 |
| 公司数据 | `docs/data/companies.json` | 完成 | 优秀 — 10家深度调研 |
| 公司视图 | `docs/views/companies.md` | 完成 | 合格 — 含综合评价排名 |
| 公司研究×10 | `docs/companies/*.md` | 完成 | 合格 |
| HR 情报 | `docs/companies/hr-intel-report.md` | 完成 | 合格 |
| 市场分析 | `docs/market/market-analysis.md` | 完成 | 优秀 — 含薪资P25-P90基准 |

**亮点：** 
- 市场分析报告的薪资基准有数据来源，对用户有直接参考价值
- 用户市场定位 P75-P90 分位，建议上调薪资预期至 38K-52K
- jobs.json 在每个职位的 `match_score` 和 `match_reasons` 字段设计好，实现了"为什么匹配"的可解释性
- jobs.json 内嵌了完整的 `market_analysis` 数据，避免了数据碎片化

**偏差：**
- CLAUDE.md Phase 2 要求 "company-researcher×N + hr-intel×N（并行克隆）"，实际执行了中国公司调研（12篇）和外企调研，但缺少小型/创业公司研究
- `docs/jobs/top-picks.md` 作为唯一 jobs 视图，缺少对全部 20 个职位的浏览视图（jobs.md 视图已覆盖）

### Phase 3: 批量定制投递

| 产出 | 路径 | 状态 | 质量 |
|------|------|------|------|
| 定制简历×5 | `docs/resume/tailored-*.md` | 完成 | 优秀 — ATS 友好，量化成果，按岗位调整关键词 |
| 求职信×5 | `docs/cover-letters/*.md` | 完成 | 优秀 — 叙事型，每个都有"为什么是我"+"岗位理解"两段结构 |
| 人脉策略总览 | `docs/networking/overview.md` | 完成 | 优秀 — 含优先级矩阵和一二级人脉盘点 |
| 人脉策略×4 | `docs/networking/strategy-*.md` | 完成 | 合格 |
| 投递追踪 | `docs/data/applications.json` | 已修复 | 合格 |

**定制简历覆盖范围：**
1. 阿里云低代码平台（job-sz-liepin-002，90分）
2. 字节飞书架构师（job-sz-boss-002，88分）
3. 腾讯云控制台（job-sz-boss-001，92分）
4. 腾讯技术中台（job-sz-lagou-003，91分）
5. 微众银行可视化搭建（job-sz-toutiao-001，89分）

**未覆盖的 Top Picks：** 字节国际远程（job-remote-001）和 PingCAP（job-remote-002）缺少定制简历和求职信。建议用户确认是否对这些远程岗位感兴趣后再补充。

**偏差：**
- CLAUDE.md Phase 3 要求 "resume-architect×N + cover-letter-writer×N + networking-strategist×N（并行克隆）"
- 实际只针对 5/7 个 Top Picks 生成了定制材料。缺少字节远程和 PingCAP 的材料
- 缺少 networking strategy 对应字节前端架构师岗位（有 strategy-bytedance.md，覆盖飞书方向）

---

## 三、与 CLAUDE.md 规范的偏差及修复状态

| # | 偏差描述 | 严重度 | 状态 |
|---|---------|--------|------|
| 1 | **流程绕过 career-coach** — Phase 0-3 由主线程直接执行，未通过 career-coach 协调调度 | 中 | 不可逆，已记录。后续 Phase 4/5 由 career-coach 接管 |
| 2 | **applications.json 空白** — 投递追踪数据文件初始化为空，未记录 Phase 进度 | 高 | 已修复 — 补充了 pipeline_progress 字段和 Phase 3 产出清单 |
| 3 | **applications.md 视图缺失** — 5个视图缺1个 | 中 | 已修复 — 生成了 applications.md |
| 4 | **Phase 3 材料未全量覆盖** — 7个 Top Picks 只生成了 5 份定制材料 | 低 | 待确认 — 等待用户决定是否补充远程岗位材料 |
| 5 | **缺少小型/创业公司研究** — companies.json 10家公司全为大中型 | 低 | 可接受 — 用户偏好中型公司（mid） |
| 6 | **networking 策略与 cover letter 不对齐** — networking 含阿里/字节/腾讯/微众，但与 cover letter 不是 1:1 映射 | 低 | 可接受 — 实际内容覆盖合理 |
| 7 | **缺少 Phase 0 的 14 维度询问记录** — preferences 已设置但询问过程未存档 | 低 | 可接受 — 数据完整即可 |

---

## 四、Phase 4/5 就绪状态

### Phase 4 入口条件

| 条件 | 状态 |
|------|------|
| 用户画像完整 | 就绪 |
| 目标公司研究完成 | 就绪（10家） |
| 定制简历可用 | 就绪（5份，可扩展） |
| 求职信可用 | 就绪（5份，可扩展） |
| 人脉策略可用 | 就绪（4份 + 总览） |
| 用户收到面试邀请 | **等待中** |

### Phase 5 入口条件

Phase 5 需 Phase 4 完成后触发，届时将需要：
- Offer 详情（薪资结构、股权、福利、入职日期等）
- 竞品 Offer 信息（如有多个）
- 用户对各项要素的权重偏好

### 当前状态

**当前位置：Phase 3 产出完成，Phase 4 等待用户触发。**

Phase 4 触发方式：用户说「我收到了XX的面试邀请」或类似表述。此时 career-coach 将调度：
- interview-coach（Gayle L. McDowell）—— 面试准备
- company-researcher（Jim Collins）—— 目标公司深度调研
- salary-negotiator（Chris Voss）—— 薪资谈判策略

三个 Agent 并行执行，输出至 `docs/interviews/<company>/`。

---

## 五、总结评估

### 整体评分：B+（良好偏优秀）

**优势：**
- 数据架构设计合理，JSON + md 双轨制运行良好
- 市场分析深度超出预期，薪资基准可直接用于谈判
- 技能缺口分析有可操作的学习路径
- 定制简历和求职信质量高，叙事性强，有量化成果
- 20 个职位覆盖 8 个平台，搜索广度充分

**待改进：**
- 流程未按 CLAUDE.md 规范通过 career-coach 调度（已接管后续）
- applications.json 初始化未包含 Phase 进度（已修复）
- 2/7 Top Pick 缺少定制材料（等待用户确认）
- company-researcher 应更严格按 Phase 2 要求与 job-scout 并行执行

### 下一步建议

1. **立即：** 用户审阅 5 份定制简历和求职信，确认投递意愿
2. **可选：** 如对远程岗位感兴趣，补充字节国际远程和 PingCAP 的定制材料
3. **等待：** 投递后等待面试邀请，触发 Phase 4
4. **长期：** 补充 GitHub 个人主页，完善 `docs/data/profile.json` 中的社交链接

---

*审计完成。career-coach 已接管 Phase 4/5 调度权。*
