# 项目详情

## OpenBook — 开源电子书阅读器

**时间:** 2022.06 - 至今
**角色:** 独立开发者
**技术栈:** Electron, React, TypeScript, IndexedDB, Web Workers
**GitHub:** github.com/zhangsan/openbook (2.3k Stars)

### 核心功能
- EPUB/PDF/Markdown 多格式渲染引擎
- 自定义注释系统，支持高亮、笔记、书签
- 笔记导出：支持 Notion、Flomo、Markdown 文件
- 阅读统计：阅读时长、进度追踪、阅读热力图
- 主题市场：社区贡献的 30+ 阅读主题

### 技术亮点
- 大文件 PDF 的分片渲染策略，100MB+ 文件无卡顿
- 基于 CRDT 的注释同步方案（开发中）
- Web Worker 处理文档解析，主线程零阻塞

---

## DevTools-Kit — 前端开发者工具集

**时间:** 2023.03 - 至今
**角色:** 独立开发者
**技术栈:** Chrome Extension Manifest V3, React, Monaco Editor
**用户量:** 周活 5000+

### 功能列表
1. 正则表达式测试器（支持 PCRE/JavaScript 双引擎）
2. JSON 格式化与校验（支持 JSON Schema）
3. 颜色选择器与调色板生成
4. Base64 / URL 编解码
5. 时间戳转换
6. JWT 解析与调试
7. 二维码生成与解析
8. 文本差异对比
9. Markdown 实时预览
10. CSS 三角形/渐变生成器
11. SQL 格式化
12. IP 地址查询与 CIDR 计算
13. UUID 生成器
14. Cron 表达式解析
15. Hash 计算（MD5/SHA）

### 技术亮点
- Manifest V3 架构，Service Worker 生命周期管理
- Monaco Editor 集成，提供类 IDE 编辑体验
- 本地优先，所有数据存储在 localStorage，无隐私泄露风险

---

## 腾讯云控制台 — 微前端架构重构

**时间:** 2023.03 - 至今
**角色:** 前端架构师 / Tech Lead
**技术栈:** React 18, TypeScript, Module Federation, qiankun

### 重构目标
- 解决 6 个子应用的构建依赖耦合
- 统一技术栈（Vue 2 → React 18）
- 独立部署、独立构建

### 成果
- 构建时间：平均 8 分钟 → 4.5 分钟（↓40%）
- 部署频率：周 2 次 → 日 3-4 次
- 子应用故障隔离，单个崩溃不影响整体

---

## 抖音电商后台 — 动态表单引擎

**时间:** 2022.03 - 2023.02
**角色:** 核心开发者
**技术栈:** Vue 3, Pinia, JSON Schema, Element Plus

### 解决的问题
- 运营配置页面有 30+ 种不同表单布局
- 每新增一种活动类型需要前端改代码 + 发版
- 产品/运营等待周期长

### 方案
- 基于 JSON Schema 的配置驱动表单引擎
- 可视化拖拽表单搭建器（内部工具）
- 支持 20+ 字段类型，自定义校验规则
- 配置即生效，无需发版

### 成果
- 运营配置效率提升 3 倍
- 新活动类型上线周期：3 天 → 半天
- 被 3 个其他业务线复用
