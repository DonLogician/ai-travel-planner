ai-travel-planner/
# AI 旅行规划助手

一个面向中文用户的智能旅行规划平台，通过大语言模型理解需求、自动生成行程，并提供预算管理、地图导航与语音交互等全流程辅助工具。本项目为“大模型辅助软件工程”课程作业，包含前后端完整实现与相关文档。

## 目录
- [AI 旅行规划助手](#ai-旅行规划助手)
  - [目录](#目录)
  - [功能亮点](#功能亮点)
  - [系统架构](#系统架构)
  - [环境准备](#环境准备)
  - [快速开始](#快速开始)
    - [方案一：Docker Compose（推荐）](#方案一docker-compose推荐)
    - [方案二：本地开发（Conda + npm）](#方案二本地开发conda--npm)
  - [环境变量说明](#环境变量说明)
    - [根目录 `.env`](#根目录-env)
    - [`backend/.env`](#backendenv)
    - [`frontend/.env`](#frontendenv)
  - [数据库结构](#数据库结构)
  - [常用命令](#常用命令)
  - [常见问题](#常见问题)
  - [更多资料](#更多资料)

## 功能亮点
- **智能行程规划**：支持语音或文字输入需求，使用千问（Qwen）或豆包（Doubao）大模型生成“日程+预算+推荐”的完整旅行方案。
- **实时预算监管**：记录开销、对比预算，分类统计并可视化展示超支风险。
- **语音驱动体验**：集成科大讯飞语音识别，实现语音规划与语音记账。
- **地图与路线**：调用高德地图 API，提供 POI 搜索与多种出行方式的路线规划。
- **云端同步**：基于 Supabase 存储行程与费用，可在多设备查看与更新。
- **完整栈实现**：FastAPI + Vue3 + Pinia + Vite，配套 Docker Compose、测试与中文文档。

更多交互细节与界面设想请参阅 `FEATURES.md` 与 `PRD.md`。

## 系统架构
```
用户 → 前端（Vue3 + Vite） → 后端（FastAPI） → 外部服务
                                      ├─ Supabase（数据库/认证）
                                      ├─ 千问 / 豆包（行程 AI）
                                      ├─ 高德地图（导航）
                                      └─ 科大讯飞（语音识别）
```
- 前端：SPA 架构，Pinia 管理跨页状态，Axios 服务层统一封装 API。
- 后端：服务化设计（行程、费用、导航、语音、LLM 等），统一通过 FastAPI 暴露 RESTful 接口。
- 数据库：Supabase（PostgreSQL），提供行程与费用两张核心表，后续可扩展用户体系。
- DevOps：Dockerfile + docker-compose，一键启动开发环境；`setup.sh` 支持类 Unix 环境快速初始化。

架构细节参见 `ARCHITECTURE.md`。

## 环境准备
| 组件           | 版本建议 | 备注                          |
| -------------- | -------- | ----------------------------- |
| Python         | 3.10+    | 推荐通过 Conda 管理环境       |
| Node.js        | 18+      | 搭配 npm                      |
| Docker Desktop | 最新版   | 启用 WSL2 后端（Windows）     |
| Supabase 账号  | -        | 需创建项目与数据库表          |
| API Key        | -        | 千问/豆包、高德、讯飞均需申请 |

> **Windows 用户建议**：优先使用 PowerShell + Conda 或 WSL；若运行 `setup.sh`，请在 WSL/Git Bash 中执行。

## 快速开始

### 方案一：Docker Compose（推荐）
```powershell
# 1. 在仓库根目录填写 .env 与 backend/.env（详见下节）
# 2. 构建并启动服务
docker compose up --build

# 后续启动可省略 --build
docker compose up

# 停止服务
docker compose down
```
- 前端：<http://localhost:5173>
- 后端 API：<http://localhost:8000/api>
- Swagger 文档：<http://localhost:8000/api/docs>

### 方案二：本地开发（Conda + npm）
```powershell
# backend
conda create -n ai-travel-planner python=3.10 -y
conda activate ai-travel-planner
cd backend
pip install --upgrade pip
pip install -r requirements.txt
python -m uvicorn app.main:app --reload

# frontend（另开终端）
cd frontend
npm install
npm run dev -- --host
```

## 环境变量说明
项目已提供示例 `.env` 文件，请根据实际凭据替换其中的示例值。

### 根目录 `.env`
```env
SUPABASE_URL=...
SUPABASE_KEY=...
IFLYTEK_APP_ID=...
IFLYTEK_API_KEY=...
IFLYTEK_API_SECRET=...
AMAP_API_KEY=...
QWEN_API_KEY=...
QWEN_MODEL=qwen-turbo
DOUBAO_API_KEY=your_doubao_api_key
DOUBAO_MODEL=doubao-pro
LLM_PROVIDER=qwen
SECRET_KEY=...
```

### `backend/.env`
包含应用基础配置（端口、DEBUG 等），以及与根目录相同的密钥字段。若修改，请保持两个文件同步或在 docker-compose 中单独配置。

> **提示**：`SECRET_KEY` 已预置随机值，建议本地或生产环境重新生成。示例命令：
```powershell
python - <<'PY'
import secrets
print(secrets.token_urlsafe(48))
PY
```

### `frontend/.env`
```
VITE_API_BASE_URL=http://localhost:8000/api
```
如部署到其他域名，请同步修改。

## 数据库结构
在 Supabase SQL Editor 中执行以下语句（需启用 `uuid-ossp` 扩展或使用 Supabase 默认 UUID）。

```sql
CREATE TABLE IF NOT EXISTS itineraries (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id TEXT NOT NULL,
  destination TEXT NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  budget NUMERIC NOT NULL,
  daily_itinerary JSONB NOT NULL,
  total_estimated_cost NUMERIC NOT NULL,
  recommendations TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS expenses (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id TEXT NOT NULL,
  itinerary_id UUID REFERENCES itineraries(id) ON DELETE CASCADE,
  category TEXT NOT NULL,
  amount NUMERIC NOT NULL,
  description TEXT NOT NULL,
  date TIMESTAMP NOT NULL,
  location TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS users (
  user_id TEXT NOT NULL,
  password TEXT
);
```

可选：根据需要开启 Row Level Security，并为匿名访问配置策略。

## 常用命令
| 目的             | 命令                                      |
| ---------------- | ----------------------------------------- |
| 运行后端（开发） | `python -m uvicorn app.main:app --reload` |
| 运行前端（开发） | `npm run dev -- --host`                   |
| 后端测试         | `pytest tests -v`                         |
| 前端测试         | `npm run test`                            |
| 构建前端产物     | `npm run build`                           |
| Docker 全量构建  | `docker compose up --build`               |

## 常见问题
- **API Key 放在哪？** 所有敏感信息请写入 `.env` 文件并加入 `.gitignore`；远程部署请使用 CI/CD Secret 管理。
- **语音功能未生效？** 检查讯飞控制台是否启用对应接口，网络是否能够访问 `www.xfyun.cn`，并确定上传音频格式符合要求（默认 16k PCM）。
- **行程生成超时？** 大模型调用存在 6~8 秒延迟，建议在前端展示加载动画，同时在后端设置合理的超时与重试。
- **数据库报错 uuid_generate_v4 不存在？** 在 Supabase 执行 `CREATE EXTENSION IF NOT EXISTS "uuid-ossp";`。

## 更多资料
- `PRD.md`：完整产品需求说明
- `ARCHITECTURE.md`：系统架构与技术细节
- `API.md`：后端 REST API 文档（含请求示例）
- `FEATURES.md`：前端交互设计与功能拆解
- `PROJECT_SUMMARY.md`：阶段总结与后续展望

欢迎在课程项目中基于本仓库进行扩展，若有问题可通过 Issue 反馈或提交 PR。