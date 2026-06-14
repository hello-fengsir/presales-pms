# 售前CRM系统 v3 (Super PMS)

> 售前项目全生命周期管理 — 客户/项目/渠道/产品/报价/跟进一站式管理

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Vue 3](https://img.shields.io/badge/Vue-3-42b883.svg)](https://vuejs.org/)
[![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ 功能特性

| 模块 | 功能 |
|---|---|
| 📊 **仪表盘** | KPI 卡片、项目漏斗、近期跟进、业绩趋势 |
| 🏢 **客户管理** | 客户档案、联系人、客户分级(A/B/C)、标签 |
| 📁 **项目管理** | 项目看板、阶段漏斗、金额/概率、方案描述、拓扑图 |
| 🤝 **渠道管理** | 代理商/集成商/咨询公司、佣金、合同 |
| 📦 **产品管理** | 产品目录、型号管理、技术参数、Excel 批量导入 |
| 💰 **报价管理** | 报价单生成、成本/毛利计算 |
| 📝 **跟进记录** | 多类型跟进(call/meeting/email/note)、附件管理 |
| 📈 **报表分析** | 业绩统计、渠道分析、产品分析 |
| 👨‍💼 **销售人员** | 销售团队管理、业绩跟踪 |
| 🔑 **API Key 管理** | 多模型 AI 支持（DeepSeek/OpenAI/通义千问） |
| 🤖 **AI 会议纪要** | 会议记录 → AI 解析 → 自动生成项目/客户/跟进 |
| 📱 **手机端适配** | 响应式布局 — 汉堡菜单、侧边栏抽屉、看板自适应 |

---

## 🏗️ 技术栈

### 前端
- **Vue 3** + TypeScript + Vite
- **Naive UI** 组件库
- **Tailwind CSS** 样式
- **Vue Router** 路由

### 后端
- **FastAPI** + Python 3.11
- **SQLAlchemy** ORM
- **PostgreSQL** 数据库
- **Redis** 缓存
- **JWT** 认证

---

## 🚀 快速开始

### 前置要求

- Docker & Docker Compose

### 部署

```bash
git clone https://github.com/hello-fengsir/presales-crm.git
cd presales-crm

# 创建 .env 文件
cp .env.example .env
# 编辑 .env 填入你的配置

docker compose up -d
```

打开浏览器访问 `http://localhost:8092`

### 默认账号

- 用户名：`admin`
- 密码：`admin123`

> ⚠️ 首次登录后请立即修改密码

---

## 📁 项目结构

```
presales-crm/
├── frontend/               # 前端 Vue 3 项目
│   ├── src/
│   │   ├── views/          # 页面组件
│   │   ├── components/     # 公共组件
│   │   ├── api/            # API 接口
│   │   ├── router/         # 路由配置
│   │   ├── composables/    # 组合式函数
│   │   └── assets/         # 静态资源
│   ├── Dockerfile
│   └── nginx.conf
├── backend/                # 后端 FastAPI 项目
│   ├── app/
│   │   ├── modules/        # 业务模块
│   │   │   ├── auth/       # 认证模块
│   │   │   └── presales/   # 售前业务模块
│   │   │       ├── routers/    # API 路由
│   │   │       ├── models.py   # 数据模型
│   │   │       └── schemas.py  # 数据结构
│   │   └── services/       # 服务层
│   │       └── ai_service.py   # AI 服务
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
└── .env.example
```

---

## 🗃️ 数据模型

```
Customer (客户)
  ├── Contact (联系人)
  └── Project (项目)
        ├── Channel (渠道)
        ├── Product (产品)
        ├── Quotation (报价)
        ├── Attachment (附件)
        └── ProjectFollowUp (跟进记录)
```

---

## 🔧 配置说明

### 环境变量

| 变量 | 说明 | 默认值 |
|---|---|---|
| `SECRET_KEY` | JWT 密钥 | `crm-secret-change-in-production` |
| `DATABASE_URL` | PostgreSQL 连接串 | `postgresql://crm:crm-pass@crm-db:5432/crm` |
| `REDIS_URL` | Redis 连接串 | `redis://crm-redis:6379/0` |
| `DEEPSEEK_API_KEY` | DeepSeek API Key（可选） | - |

### AI 模型配置

系统支持在前端页面配置多个 AI 模型：
- DeepSeek
- OpenAI
- 通义千问
- 其他兼容 OpenAI API 的模型

---

## 📄 License

MIT License © [峰Sir](https://github.com/hello-fengsir)
