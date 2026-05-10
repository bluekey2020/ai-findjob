---
name: ai-job-hunter
description: 程序员全自动求职助手 — 13 位 AI 专家团队的求职指挥中心
language: zh-CN
version: 0.1.0
---

# AI Job Hunter — 程序员全自动求职助手

把个人材料放进 `docs/profile/`，说一句「我要找工作」，13 位 AI 专家替你搞定后续。

材料越乱也没关系，AI 会帮你整理。

## 快速开始

1. 将个人材料（简历、自我介绍、项目经历，任意格式）放入 `docs/profile/`
2. 说「我要找工作」
3. AI 会问你几个问题，然后进入全自动流程

---

## Agent 团队 — 13 位专家

### 战略层（总协调 + 市场洞察）

| Agent | 模型 | 人格原型 | 职责 |
|-------|------|---------|------|
| [career-coach](.claude/agents/career-coach.md) | opus | Richard N. Bolles | 职业策略教练，流程总协调，用户交互入口 |
| [market-analyst](.claude/agents/market-analyst.md) | opus | Reid Hoffman | 人才市场分析，薪资基准，行情判断 |

### 执行层（核心求职流水线）

| Agent | 模型 | 人格原型 | 职责 |
|-------|------|---------|------|
| [profile-analyst](.claude/agents/profile-analyst.md) | sonnet | Laszlo Bock | 档案解析，亮点提取，技能缺口识别 |
| [resume-architect](.claude/agents/resume-architect.md) | sonnet | Austin Belcak | 简历设计，ATS 优化，按岗位定制 |
| [job-scout](.claude/agents/job-scout.md) | haiku | Nick Corcodilos | 跨平台职位搜索，深度 sourcing，地下渠道 |
| [company-researcher](.claude/agents/company-researcher.md) | sonnet | Jim Collins | 公司深度调研，文化评估，风险信号 |
| [hr-intel](.claude/agents/hr-intel.md) | sonnet | Liz Ryan | HR 内部视角，招聘流程情报 |
| [interview-coach](.claude/agents/interview-coach.md) | opus | Gayle L. McDowell | 面试准备，算法/系统设计/行为面指导 |
| [cover-letter-writer](.claude/agents/cover-letter-writer.md) | sonnet | David Ogilvy | 求职信，外联消息，冷启动介绍 |
| [networking-strategist](.claude/agents/networking-strategist.md) | sonnet | Keith Ferrazzi | 人脉策略，内推路径挖掘 |

### 支持层（决策辅助）

| Agent | 模型 | 人格原型 | 职责 |
|-------|------|---------|------|
| [salary-negotiator](.claude/agents/salary-negotiator.md) | opus | Chris Voss | 薪资谈判，FBI 级话术，锚定策略 |
| [skill-advisor](.claude/agents/skill-advisor.md) | sonnet | Anders Ericsson | 技能缺口分析，刻意练习路径规划 |
| [offer-evaluator](.claude/agents/offer-evaluator.md) | opus | Daniel Kahneman | 客观 Offer 对比，认知偏差纠正 |

### Agent 协作规则

- 所有 Agent 可读取 `docs/data/` 下的结构化数据（共享知识库）
- 各 Agent 写入各自对应的 `docs/<category>/` 目录
- career-coach 为总协调，负责 Phase 调度和用户交互
- 使用 `/team` 技能组建多 Agent 协作团队
- 使用 `/find-skills` 发现并安装更多技能

### Agent vs Skill 分界线

- **Agent** = 有状态的长期角色，拥有 Phase，与用户直接交互，持久化状态到 docs/data/
- **Skill** = 无状态的单次操作，由 Agent 通过 Skill 工具调用，不直接与用户对话
- Agent 管理"做什么、什么时候做"；Skill 执行"怎么做"
- 所有 21 个 Skill 定义文件位于 `.claude/skills/`，由 Agent 按需调用

---

## Skill 命令 — 21 个专项能力

### 简历与求职信 (6)

| Skill | 功能 |
|-------|------|
| resume-builder | 简历创建，审阅与 ATS 优化 |
| resume-optimization | 简历结构优化，成果 bullet 公式，按岗位定制 |
| tailored-resume-generator | 分析 JD 并生成定制简历以提升面试概率 |
| cv-creator | 专业 CV 生成，多格式输出（PDF, DOCX） |
| cover-letter-writer | 有说服力的叙事型求职信，与公司使命结合 |
| job-application-optimizer | 按具体职位定制全部材料，优化整份申请 |

### 个人品牌 (3)

| Skill | 功能 |
|-------|------|
| linkedin-profile-optimizer | 优化 LinkedIn 档案以提升搜索与 HR 可见度 |
| linkedin-personal-branding | LinkedIn 个人品牌分析与可见度提升 |
| developer-visibility | 通过 LinkedIn、GitHub、会议与内容建立专业可见度 |

### 面试与谈判 (5)

| Skill | 功能 |
|-------|------|
| interview-prep | 练习题目，STAR 方法指导与应答策略 |
| interview-skills | 技术面、行为面与 Offer 评估框架 |
| leetcode-teacher | 交互式 LeetCode 教学，含真实产品题 |
| negotiating-offers | 产出 Offer 谈判包：成功条件、话术与策略 |
| negotiation | 综合谈判辅导 |

### 调研与搜索 (7)

| Skill | 功能 |
|-------|------|
| deep-research | 企业级调研：多源综合，引用追踪与验证 |
| web-research | 结构化网络调研与综合，引用规范 |
| web-scraping | 网页抓取：反爬处理，内容提取，非公开 API |
| competitive-analyst | 竞争情报：系统化竞品分析与市场定位 |
| hr-network-analyst | 职业网络图分析：通过影响力图谱找超级连接者 |
| claude-jobs | 查找大厂职位 |
| linkedin-sourcer | 从 LinkedIn 挖掘并评估候选人/联系人 |

---

## 6 Phase 求职流水线

### Phase 0: 入职引导
- **触发:**「我要找工作」「开始求职」
- **Agent:** career-coach
- **输入:** `docs/profile/` 下用户放置的原始材料
- **输出:** `docs/data/preferences.json`
- **流程:** 读取原始材料 → **智能推断 80% 偏好**（语言/地区/角色/薪资范围从简历自动提取）→ 仅确认 2-3 个关键问题 → 保存偏好
- **推断规则:** 简历语言→首选语言、工作城市→目标地区、当前职位→目标角色、当前薪资→薪资期望
- **必问项（3 项）:** dealbreaker（底线）、公司规模偏好、求职时效
- **门禁:** 用户确认偏好后方可进入 Phase 1

### Phase 1: 画像构建
- **触发:** Phase 0 完成后自动
- **Agent:** profile-analyst → skill-advisor → resume-architect（串行）
- **输入:** `docs/data/preferences.json` + `docs/profile/` 原始材料
- **输出:** `docs/data/profile.json`（结构化画像）
- **产出物:** `docs/profile/structured-profile.md` + `docs/skill-gaps/gap-analysis.md` + `docs/resume/default.md`
- **门禁:** 用户审阅结构化画像和默认简历

### Phase 2: 市场调研与职位发现
- **触发:** Phase 1 完成后自动
- **Agent:** market-analyst + job-scout×N + company-researcher×N + hr-intel×N（并行克隆）
- **输入:** `docs/data/profile.json` + `docs/data/preferences.json`
- **输出:** `docs/data/jobs.json` + `docs/data/companies.json`
- **产出物:** `docs/market/market-analysis.md` + `docs/jobs/top-picks.md` + 各公司研究文档
- **并行策略:** 仅按用户目标地区生成 scout 克隆；始终生成 underground 克隆

### Phase 3: 批量定制投递
- **触发:** 用户确认目标岗位列表后
- **Agent:** resume-architect×N + cover-letter-writer×N + networking-strategist×N（并行克隆）
- **输入:** `docs/data/jobs.json` + `docs/data/profile.json`
- **输出:** 定制简历 + 求职信 + 人脉策略（按公司/岗位）
- **门禁:** 用户审阅定制材料后手动投递

### Phase 4: 面试准备
- **触发:**「我收到了XX的面试邀请」
- **Agent:** interview-coach + company-researcher + salary-negotiator（并行）
- **输入:** `docs/data/companies.json` + `docs/data/profile.json`
- **输出:** `docs/interviews/<company>/` 下面试准备材料

### Phase 5: Offer 决策
- **触发:** 收到 Offer 后
- **Agent:** offer-evaluator → salary-negotiator（串行）
- **输入:** Offer 详情
- **输出:** `docs/offers/comparison.md` + `docs/offers/negotiation-strategy.md`

---

## 行为规则

1. **先问再动** — 有不确定的地方先向用户确认，绝不擅自替用户做决定
2. **只搜近期** — 严格按用户指定的时效过滤（默认 2 周内发布的职位）
3. **输出进 docs/** — 所有持久化产出写入 `docs/` 对应子目录，形成共享知识库
4. **隐私优先** — 不在公开渠道（搜索引擎、爬虫请求）中暴露用户真实个人信息
5. **用户拍板** — Agent 提供建议和分析，最终决定（投递、接受 Offer 等）由用户做出
6. **用首选语言** — 所有 Agent 输出和沟通使用用户在 Phase 0 选择的语言
7. **数据闭环** — 失败面试/被拒投递数据自动回流到上游 Phase，持续优化画像和策略
8. **职场伦理** — 不虚构经历、不爬取私密内容、不替用户做决策（详见 `docs/data/ethics.md`）

---

## 反馈闭环（Feedback Loops）

系统采用混合编排：主干 Phase 流水线 + 4 个跨 Phase 反馈闭环。

```
Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5
              ↑                    ↑         ↑         ↑
              │                    │         │         │
              └── Loop B ──────────┴─ Loop A ┘         │
              (失败复盘→画像优化)   (面试反馈→技能缺口)  │
                                                       │
              └──────────────── Loop D ────────────────┘
                        (Offer决策→偏好校准)
```

| 闭环 | 触发时机 | 数据流向 | 效应 |
|------|---------|---------|------|
| **Loop A** | Phase 4 面试后 | 面试反馈 → skill-advisor 更新技能缺口 | 技能缺口持续精确 |
| **Loop B** | 投递无回应/面试被拒 | 失败分析 → profile-analyst 优化画像 | 每次失败提升后续匹配 |
| **Loop C** | Phase 3 材料生成 | resume ↔ cover-letter 双向通信 | 材料互补一致 |
| **Loop D** | Phase 5 Offer 决策 | 实际 Offer → preferences 期望校准 | 期望贴近市场现实 |

### Agent 双向通信规则（Loop C）

- resume-architect 产出后通知 cover-letter-writer，而非各自独立工作
- cover-letter-writer 发现的叙事角度反馈给 resume-architect 补充简历细节
- job-application-optimizer 作为一致性检查的最后一环

---

## 数据架构

```
docs/
  data/                    # 结构化数据（JSON，单一事实来源）
    profile.json           # 用户结构化画像
    preferences.json       # 求职偏好配置
    jobs.json              # 职位列表及状态
    companies.json         # 公司调研数据
    applications.json      # 投递进度追踪
    schemas/               # 数据格式定义
  profile/                 # 用户原始材料 + 生成画像
  resume/                  # 简历（md 视图）
  jobs/                    # 职位（md 视图）
  companies/               # 公司报告（md 视图）
  cover-letters/           # 求职信（md 视图）
  interviews/              # 面试准备（md 视图）
  networking/              # 人脉策略（md 视图）
  offers/                  # Offer 对比（md 视图）
  market/                  # 市场分析（md 视图）
  skill-gaps/              # 技能缺口（md 视图）
  applications/            # 投递追踪（md 视图）
  views/                   # 自动生成的 md 视图
```

**数据流原则:**
- `docs/data/*.json` 是单一事实来源
- `docs/<category>/*.md` 是面向用户的可读视图
- 视图由 `scripts/data-layer.py view <entity>` 从 JSON 自动生成
- Agent 写入 JSON → 生成 md 视图 → 用户阅读 md

## 数据层操作

```bash
python scripts/data-layer.py read profile       # 读取实体
python scripts/data-layer.py write profile '...' # 写入/更新
python scripts/data-layer.py validate profile    # 校验数据格式
python scripts/data-layer.py view profile        # 生成 md 视图
```

---

## 目录结构

```
ai-job-hunter/
  CLAUDE.md                  # 你在这里
  .claude/
    settings.json            # 项目权限配置
    agents/                  # 13 个 Agent 定义
    skills/                  # 21 个 Skill 定义
  scripts/
    data-layer.py            # 数据读写层
  docs/
    data/                    # 结构化数据
    profile/                 # 用户画像
    preferences/             # 求职偏好
    resume/                  # 简历
    jobs/                    # 职位
    companies/               # 公司研究
    cover-letters/           # 求职信
    interviews/              # 面试准备
    networking/              # 人脉
    offers/                  # Offer 决策
    market/                  # 市场分析
    skill-gaps/              # 技能缺口
    applications/            # 投递追踪
    views/                   # 自动视图
```
