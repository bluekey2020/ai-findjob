# 张三

**目标岗位**：前端架构师 -- 飞书 | **地点**：深圳 | **期望薪资**：45K-65K/月

---

**联系方式**
- 电话：138-0000-0001
- 邮箱：zhangsan@example.com

---

## 专业摘要

5 年经验前端工程师，专攻**复杂协同编辑器架构与大型前端系统重构**。具备 Vue + React 双栈精通能力，亲身经历并主导了两次大型技术栈迁移：Shopee 的 jQuery -> React（10+ 页面现代化改造）和腾讯云控制台的 Vue 2 -> React 18（6 个子应用微前端解耦）。当前在腾讯云主导 Module Federation + qiankun 微前端架构重构，实现子应用独立部署和故障隔离，构建时间缩短 40%，部署频率从周 2 次提升到日 3-4 次。开源项目 OpenBook（2.3k Stars）中正在研发基于 CRDT 的注释实时同步方案，对多人协作场景下的冲突解决和一致性保障有深入理解。前字节跳动员工，熟悉飞书技术栈和内部研发流程。

---

## 专业技能

**前端框架**：React（5 年，专家）、Vue 3（3 年，高级）、Next.js（2 年，中级）
**语言**：TypeScript（5 年，专家）、JavaScript（5 年，专家）
**架构与重构**：微前端架构（Module Federation + qiankun，2 年）、大型系统技术栈迁移（jQuery -> React、Vue 2 -> React 18）
**实时协作**：CRDT（开发中）、WebSocket（2 年）、OT 算法原理
**跨端方案**：Electron（2 年）、Chrome Extension（2 年）、响应式设计
**状态管理**：Redux Toolkit（4 年，专家）、Zustand（2 年，高级）、Pinia（2 年，高级）
**构建工具**：Webpack（5 年，专家）、Vite（2 年，高级）、Turbopack（1 年）
**样式方案**：CSS Modules（4 年，高级）、Tailwind CSS（3 年，高级）、Styled Components（3 年，高级）
**测试**：Playwright（2 年，高级）、Vitest（2 年，高级）、Cypress（2 年，中级）
**后端与数据库**：Node.js（3 年，高级）、Express（3 年，中级）、Prisma（2 年，中级）、PostgreSQL（2 年，中级）
**DevOps**：GitHub Actions（2 年，高级）、Docker（2 年，中级）

---

## 工作经历

### 腾讯 | 高级前端工程师 | 前端架构师 / Tech Lead
2023.03 - 至今 | 深圳

- 主导腾讯云控制台大型前端系统重构：从 Vue 2 全量迁移至 React 18 + TypeScript，采用 Module Federation + qiankun 微前端架构将 6 个子应用解耦，实现独立部署和故障隔离
- 构建时间从 8 分钟降至 4.5 分钟（缩短 40%），部署频率从周 2 次提升到日 3-4 次，大幅提升工程迭代效率
- 从零搭建 Radix UI 组件库体系，封装 50+ 业务组件覆盖 3 个产品线，建立前端编码规范和技术评审流程，保障跨端和多产品线的一致性
- 推动 Playwright E2E 测试体系建设，核心业务流程覆盖率从 0 提升至 85%，线上故障率降低约 60%，保障复杂系统重构质量
- 指导 3 名初级工程师，制定 onboarding 计划和代码审查流程，团队交付效率提升约 30%
- 技术栈：React 18、TypeScript、Module Federation、qiankun、Playwright、Radix UI

### 字节跳动 | 前端工程师 | 核心开发者
2021.06 - 2023.02 | 北京/深圳

- 使用 Vue 3 + Pinia 重构抖音电商商品管理模块，首屏加载性能提升 60%，页面交互响应时间从 2.5 秒降至 1 秒以内
- 设计基于 JSON Schema 的动态表单引擎，支持 30+ 种表单布局和 20+ 字段类型，运营配置效率提升 3 倍，方案被 3 个业务线复用
- 搭建前端监控体系（Sentry + 自研埋点），覆盖全链路性能指标采集，日均处理百万级事件
- 技术栈：Vue 3、Pinia、JSON Schema、Element Plus、Sentry

### Shopee | 前端开发工程师
2019.07 - 2021.05 | 深圳

- 主导团队从 jQuery 到 React 的全量技术栈迁移，制定分阶段迁移策略和兼容层方案，完成 10+ 核心页面的现代化改造，业务零中断
- 负责卖家中心核心页面开发，开发多语言支持方案覆盖东南亚 7 个国家和地区
- 优化 Webpack 构建配置和 CI/CD 流水线，构建时间减少 35%，发布效率提升约 50%
- 技术栈：React、jQuery、Webpack、Node.js

---

## 项目经验

### 腾讯云控制台 -- 大型系统微前端架构重构
2023.03 - 至今 | 前端架构师 / Tech Lead

- 主导 Vue 2 -> React 18 全量技术栈迁移，6 个子应用微前端解耦（Module Federation + qiankun）
- 子应用独立部署和故障隔离，构建时间缩短 40%（8min -> 4.5min），部署频率周 2 次 -> 日 3-4 次
- 建立跨应用通信协议和共享组件层，保障迁移过程中的兼容性和一致性
- 技术栈：React 18、TypeScript、Module Federation、qiankun、Webpack、Playwright

### OpenBook -- 开源电子书阅读器（CRDT 实时协作）
2022.06 - 至今 | 独立开发者

- 基于 Electron + React + TypeScript 的跨平台电子书阅读器，GitHub 获得 2.3k Stars
- 自研注释系统支持高亮和笔记导出到 Notion/Flomo
- 正在研发基于 CRDT（Conflict-free Replicated Data Type）的注释实时同步方案，实现多人协作场景下的无冲突注释共享和离线编辑后自动合并
- 大文件 PDF 分片渲染策略，100MB+ 文件流畅无卡顿；Web Worker 文档解析，主线程零阻塞
- 社区贡献 30+ 阅读主题，累计下载量约 12000 次
- 技术栈：Electron、React、TypeScript、CRDT、Web Workers、IndexedDB

### 抖音电商后台 -- 动态表单引擎
2022.03 - 2023.02 | 核心开发者

- 基于 JSON Schema 的配置驱动动态表单引擎，运营配置效率提升 3 倍
- 新建活动上线周期从 3 天缩短至半天，被 3 个业务线复用
- 技术栈：Vue 3、Pinia、JSON Schema、Element Plus

---

## 教育背景

### 深圳大学 | 计算机科学与技术 | 本科
2015.09 - 2019.06 | GPA 3.7/4.0 | 校级优秀毕业生

---

## 语言能力

- 中文：母语
- 英语：CET-6，能流畅阅读英文技术文档和技术交流

---

## 开源贡献

- **OpenBook**：GitHub 2.3k Stars，跨平台电子书阅读器（含 CRDT 实时协作方案研发）
- **DevTools-Kit**：Chrome 扩展，周活 5000+ 用户
