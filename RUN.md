# AI Job Hunter — 运行指南

## 环境要求

| 依赖 | 最低版本 | 说明 |
|------|---------|------|
| Python | 3.12+ | 后端运行环境 |
| Node.js | 20+ | 前端构建 |
| npm | 10+ | 前端包管理 |
| Redis | 7+ | Celery 消息队列（可选，开发环境可跳过） |
| Docker | 24+ | 容器化部署（可选） |

---

## 快速启动（3 步）

### 第一步：环境变量

```bash
cd backend
cp .env.example .env   # 或手动创建
```

编辑 `backend/.env`，填入 Anthropic API Key：

```env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
JWT_SECRET_KEY=your-production-secret
DATABASE_URL=sqlite+aiosqlite:///./aijob.db
```

> 不填 API Key 也可以启动，但所有 AI 相关功能（简历生成、职位解析、Offer 评估等）将不可用。

### 第二步：安装依赖

```bash
# 后端
cd backend
pip install -r requirements.txt

# 前端
cd ../frontend
npm install
```

### 第三步：启动

```bash
# 终端 1 — 后端 API (http://localhost:8000)
cd backend
uvicorn app.main:app --reload --port 8000

# 终端 2 — 前端 Dev Server (http://localhost:5173)
cd frontend
npm run dev
```

浏览器打开 http://localhost:5173，注册账号即可使用。

### 可选：启动 Celery Worker

```bash
# 终端 3 — 异步任务处理（需要 Redis）
cd backend
celery -A app.worker worker --loglevel=info --concurrency=2
```

---

## 种子数据

运行 demo 数据填充脚本（创建用户 + 画像 + 职位 + 公司）：

```bash
cd backend
python scripts/seed.py
```

Demo 登录：`demo@aijob.com` / `demo123`

种子数据来源于 `docs/data/*.json`，可在运行前编辑。

---

## Docker 一键部署

```bash
# 在项目根目录
docker compose up -d
```

服务分布：

| 服务 | 端口 | 说明 |
|------|------|------|
| frontend (nginx) | 5173 | React SPA 静态文件 + API 代理 |
| backend (uvicorn) | 8000 | FastAPI 后端 |
| redis | 6379 | 消息队列（Celery broker） |
| worker (celery) | — | 异步 LLM 调用 |

需要 Anthropic API Key：

```bash
ANTHROPIC_API_KEY=sk-ant-... docker compose up -d
```

---

## 6 Phase 求职流水线

```
Phase 0  入职引导    →  智能推断偏好，确认关键约束
Phase 1  画像构建    →  解析简历，生成结构化画像
Phase 2  职位搜索    →  跨平台搜索 + 双向匹配 + 反欺诈
Phase 3  批量投递    →  定制简历 + 求职信 + 人脉策略
Phase 4  面试准备    →  公司专项训练 + 模拟面试
Phase 5  Offer 决策  →  多维度对比 + 薪资谈判
```

每个 Phase 通过状态机的门禁条件自动推进。左侧导航栏按 Phase 顺序排列。

---

## 项目结构

```
ai-job-hunter/
├── backend/
│   ├── app/
│   │   ├── api/          # 16 个路由模块（51 个端点）
│   │   ├── core/         # 数据库、认证、LLM 客户端、配置
│   │   ├── engine/       # Phase 状态机
│   │   ├── models/       # SQLAlchemy ORM 模型
│   │   ├── prompts/      # 6 个 Agent 系统提示词 + tool schema
│   │   ├── schemas/      # Pydantic 请求/响应模型
│   │   └── services/     # 8 个业务服务
│   ├── scripts/
│   │   └── seed.py       # Demo 数据填充
│   ├── tests/            # 39 个 pytest 测试
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/   # 布局 + 通用组件
│   │   ├── pages/        # 11 个页面
│   │   └── api/          # HTTP 客户端
│   ├── nginx.conf
│   ├── Dockerfile
│   └── package.json
├── docs/
│   └── data/             # 种子数据 JSON 文件
├── docker-compose.yml
└── RUN.md                # 你在这里
```

---

## 常用命令

```bash
# 后端测试
cd backend && python -m pytest tests/ -v

# 后端类型检查（需要 mypy）
cd backend && mypy app/

# 前端类型检查
cd frontend && npx tsc --noEmit

# 前端生产构建
cd frontend && npx vite build

# 数据库重置（删除 SQLite 文件）
rm backend/aijob.db

# API 文档（启动后端后访问）
http://localhost:8000/docs        # Swagger
http://localhost:8000/redoc       # ReDoc

# 演示流程验证
# 1. POST /api/v1/auth/register  注册
# 2. PUT  /api/v1/preferences     填写偏好
# 3. POST /api/v1/phases/advance  推进 Phase
# 4. PUT  /api/v1/profile         填写画像
# 5. POST /api/v1/jobs/import     导入职位
# 6. POST /api/v1/jobs/search     搜索匹配
# ...
```

---

## 环境变量参考

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./aijob.db` | 数据库连接。生产环境改为 PostgreSQL |
| `ANTHROPIC_API_KEY` | — | Anthropic API Key，AI 功能必需 |
| `JWT_SECRET_KEY` | `dev-secret-change...` | JWT 签名密钥，生产环境务必更换 |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis 连接 |
| `CELERY_BROKER_URL` | `redis://localhost:6379/1` | Celery broker |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/2` | Celery 结果后端 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | JWT 过期时间 |
| `SMTP_HOST` | — | 邮件服务器（可选） |
| `SMTP_PORT` | 587 | 邮件端口 |
| `SMTP_USER` | — | 邮件账号 |
| `SMTP_PASSWORD` | — | 邮件密码 |
| `SMTP_FROM` | `noreply@aijobhunter.local` | 发件人地址 |

---

## 技术栈速览

| 层 | 技术 |
|---|------|
| 后端框架 | Python 3.12 + FastAPI |
| 数据库 | SQLAlchemy 2.0 async (SQLite/PostgreSQL) |
| AI | Anthropic SDK (Haiku/Sonnet/Opus 3 模型路由) |
| 异步任务 | Celery + Redis |
| 前端框架 | React 19 + TypeScript + Vite |
| 样式 | Tailwind CSS 4 |
| 状态管理 | TanStack React Query |
| 路由 | React Router 7 |
| 部署 | Docker Compose |
