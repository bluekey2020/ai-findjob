# 张三

**目标岗位**：前端架构师 -- 技术中台 | **地点**：深圳 | **期望薪资**：45K-60K/月

---

**联系方式**
- 电话：138-0000-0001
- 邮箱：zhangsan@example.com

---

## 专业摘要

5 年经验前端工程师，深耕**前端技术中台与工程化基础设施建设**。当前在腾讯云主导微前端架构重构的同时，从零搭建了覆盖 3 个产品线的 Radix UI 组件库体系（50+ 业务组件），制定前端编码规范和技术评审流程。具备企业内部研发框架设计和 CLI 工具链开发经验（Webpack/Vite/Turbopack 全链路构建优化，自研动态表单引擎被 3 个业务线复用）。曾在字节跳动设计 JSON Schema 驱动的配置化表单引擎，支撑 30+ 种表单布局，将运营配置效率提升 3 倍。具备从 jQuery 到 React、Vue 2 到 React 18 两次大型技术栈迁移的一线经验，擅长抽象可复用的技术方案降低团队重复开发成本。拥有 2.3k Stars 开源项目，具备框架设计视野和社区影响力。

---

## 专业技能

**构建体系**：Webpack（5 年，专家）、Vite（2 年，高级）、Turbopack（1 年，初级）、Babel（5 年）、ESBuild（2 年）
**前端框架**：React（5 年，专家）、Vue 3（3 年，高级）、Next.js（2 年，中级）
**语言**：TypeScript（5 年，专家）、JavaScript（5 年，专家）
**组件与设计系统**：Radix UI（2 年）、Ant Design（3 年）、Element Plus（2 年）、设计系统搭建
**工程化与工具链**：CLI 工具开发、ESLint/Prettier 规范体系、Monorepo 管理（pnpm/Turborepo）
**微前端架构**：Module Federation（2 年，高级）、qiankun（2 年，高级）
**状态管理**：Redux Toolkit（4 年，专家）、Zustand（2 年，高级）、Pinia（2 年，高级）
**测试**：Playwright（2 年，高级）、Vitest（2 年，高级）、Cypress（2 年，中级）
**DevOps**：GitHub Actions（2 年，高级）、Docker（2 年，中级）、CI/CD 流水线设计
**后端与数据库**：Node.js（3 年，高级）、Express（3 年，中级）、Prisma（2 年，中级）、PostgreSQL（2 年，中级）

---

## 工作经历

### 腾讯 | 高级前端工程师 | 前端架构师 / Tech Lead
2023.03 - 至今 | 深圳

- 从零搭建基于 Radix UI 的企业级组件库体系，封装 50+ 业务组件覆盖 3 个产品线（控制台、云端 IDE、监控面板），建立前端编码规范和技术评审流程，消除跨团队样式与交互不一致，降低重复开发成本
- 主导腾讯云控制台微前端架构重构（Module Federation + qiankun），设计子应用联邦加载与沙箱隔离方案，将 6 个子应用解耦实现独立部署和故障隔离，构建时间缩短 40%（8min -> 4.5min），部署频率从周 2 次提升到日 3-4 次
- 推动 E2E 测试体系（Playwright）与 CI/CD 流水线集成，核心业务流程测试覆盖率从 0 提升至 85%，线上故障率降低约 60%
- 制定团队前端技术规范（代码风格、组件设计、架构决策记录），指导 3 名初级工程师，团队交付效率提升约 30%
- 技术栈：React 18、TypeScript、Radix UI、Module Federation、qiankun、Webpack、Playwright

### 字节跳动 | 前端工程师 | 核心开发者
2021.06 - 2023.02 | 深圳

- 设计基于 JSON Schema 的配置驱动动态表单引擎（内部研发框架），支持 30+ 种表单布局和 20+ 字段类型，提供可视化拖拽搭建器，实现配置即生效、无需发版
- 该引擎方案将运营配置效率提升 3 倍，新建活动上线周期从 3 天缩短至半天
- 方案被 3 个其他业务线（商品、营销、数据）复用，节省约 6 人/月的重复开发成本，验证了框架的通用性和扩展性
- 搭建前端监控体系（Sentry + 自研埋点 SDK），覆盖全链路性能指标采集，日均处理百万级事件
- 技术栈：Vue 3、Pinia、JSON Schema、Element Plus、Sentry

### Shopee | 前端开发工程师
2019.07 - 2021.05 | 深圳

- 主导团队从 jQuery 到 React 的技术栈迁移，完成 10+ 核心页面的现代化改造，制定迁移方案和兼容策略
- 优化 Webpack 构建配置（代码分割、Tree Shaking、缓存策略）和 CI/CD 流水线，构建时间减少 35%，发布效率提升约 50%
- 负责卖家中心核心页面开发，设计多语言支持方案覆盖东南亚 7 个国家和地区
- 技术栈：React、jQuery、Webpack、Node.js

---

## 项目经验

### 企业级组件库体系搭建
2023.03 - 至今 | 前端架构师 / Tech Lead

- 基于 Radix UI 封装 50+ 业务组件，建立组件设计规范（可访问性、主题化、国际化）
- 覆盖 3 个产品线（控制台、云端 IDE、监控面板），统一跨产品线交互和视觉语言
- 建立前端编码规范和技术评审流程，推动组件市场化和文档化
- 技术栈：React 18、TypeScript、Radix UI、Storybook、CSS Modules

### JSON Schema 动态表单引擎（内部研发框架）
2022.03 - 2023.02 | 核心开发者

- 设计配置驱动的表单引擎，支持 30+ 种表单布局、20+ 字段类型和自定义校验规则
- 配套可视化拖拽搭建器（内部工具），降低非技术运营人员使用门槛
- 配置即生效无需发版，方案被 3 个业务线复用，节省约 6 人/月重复开发成本
- 技术栈：Vue 3、Pinia、JSON Schema、Element Plus

### DevTools-Kit -- 前端开发者工具集 Chrome 扩展
2023.03 - 至今 | 独立开发者

- 开发面向前端开发者的工具集 Chrome 扩展，集成 15+ 常用开发工具
- 集成 Monaco Editor 提供类 IDE 编辑体验，周活跃用户 5000+
- Manifest V3 + Service Worker 架构，本地优先零数据外泄
- 技术栈：Chrome Extension MV3、React、Monaco Editor

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

- **OpenBook**：GitHub 2.3k Stars，跨平台电子书阅读器（Electron + React + TypeScript）
- **DevTools-Kit**：Chrome 扩展，周活 5000+ 用户
