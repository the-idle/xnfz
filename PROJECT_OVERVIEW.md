# Unity Assessment API 项目说明与运行指南

Unity Assessment API 是一个基于 FastAPI 的后端服务，用于管理和下发"平台-题库-工序/点位-题目-选项"的分层考核内容，并为 Unity 客户端提供考核会话、答案提交、成绩查询等接口。

- **平台名称**：数字孪生基础比赛管理平台
- **框架与技术栈**：FastAPI, Pydantic v2, SQLAlchemy, Alembic, JWT(OAuth2), MySQL/SQLite, Uvicorn, APScheduler
- **前端技术栈**：Vue 3, TypeScript, Element Plus, Vite, Pinia
- **统一响应**：所有业务端点返回统一结构 `{ code, msg, data }`
- **API 前缀**：`/api/v1`
- **静态资源**：`/static`（图片等）

> 📋 **最近更新**：查看 [CHANGELOG.md](./CHANGELOG.md) 了解详细更新内容

## 目录结构（简述）

- `app/main.py`：FastAPI 应用入口，挂载路由与静态资源
- `app/api/api.py`：统一路由注册（`/api/v1` 前缀）
- `app/api/endpoints/`：各业务端点（登录、平台、题库、工序、题目、考核、客户端、成绩）
- `app/core/config.py`：读取 .env 配置
- `app/schemas/`：Pydantic 模型（请求/响应/蓝图/统一响应）
- `app/models/`：SQLAlchemy ORM 模型
- `app/crud/`：数据访问 CRUD 层
- `alembic/`：数据库迁移版本
- `initial_data.py`：初始化管理员用户脚本
- `static/images/`：图片上传存储位置
- `.env`：环境变量

## 环境准备

- 操作系统：Windows
- Python：建议 3.11+
- 数据库：
  - 默认使用 MySQL：`mysql+pymysql://root:root@localhost:3306/unity_assessment`
  - 亦可改用 SQLite：`sqlite:///./assessment.db`

### 1) 激活虚拟环境
```bash
venv\Scripts\activate
```

### 2) 安装依赖
```bash
pip install -r requirements.txt
```

### 3) 配置环境变量（.env）
```bash
APP_NAME="Unity Assessment API"
DEBUG=True
SECRET_KEY="change-this-secret"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

# 默认 MySQL
```bash
DATABASE_URL="mysql+pymysql://root:root@localhost:3306/unity_assessment"
```

# 也可使用 SQLite
```bash
# DATABASE_URL="sqlite:///./assessment.db"
```


### 4) 执行数据库迁移（Alembic）
```bash
alembic upgrade head
```
或使用 venv 中的 alembic：
```bash
venv\Scripts\alembic.exe upgrade head
```

### 5) 初始化管理员账号
```bash
python initial_data.py
```
默认创建 `admin / password` 用于 Swagger 授权。

### 6) 启动服务

**开发模式（推荐，热重载）：**
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**生产 / 压测模式（多 worker，支持高并发）：**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```
> 注意：可按机器核数调整 `--workers`，并确保数据库/Redis 连接池参数与之匹配。开发时使用 `--reload` 模式即可。

Swagger UI: http://127.0.0.1:8000/docs

## 前端运行指南

### 环境要求
- Node.js: ^20.19.0 或 >=22.12.0
- npm 或 yarn

### 1) 进入前端目录
```bash
cd unity_assessment_head
```

### 2) 安装依赖
```bash
npm install
```

### 3) 配置环境变量（可选）
在 `unity_assessment_head` 目录下创建 `.env` 文件：
```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```
如果不配置，默认使用 `http://127.0.0.1:8000`

### 4) 启动前端开发服务器
```bash
npm run dev
```
前端服务将运行在：http://0.0.0.0:3000（支持外部访问）

### 5) 构建生产版本
```bash
npm run build
```
构建产物在 `dist/` 目录

### 6) 预览生产构建
```bash
npm run preview
```

## 统一响应结构
所有业务端点采用统一响应模型：
```json
{
  "code": 200,
  "msg": "success",
  "data": { ... }
}
```

## 身份认证
- Swagger 右上角 "Authorize"
- `tokenUrl = /api/v1/login/token`
- 默认账号：`admin / password`

## 静态资源与图片上传
- 静态资源挂载：`/static`
- 上传图片：`POST /api/v1/utils/upload/image/`（仅管理员）
- 存储路径：`static/images`，响应 `data.file_url` 可直接用于前端显示。

## API 分组一览（路径均带 `/api/v1` 前缀）
- 登录认证：`POST /login/token`，`POST /login/test-token`
- 平台：`/platforms`（增删改查）
- 题库：`/platforms/{platform_id}/question-banks`（创建/列表）
- 工序/点位：`/question-banks/{question_bank_id}/procedures`（创建）
- 题目：`/procedures/{procedure_id}/questions`（创建，含图片上传）
- 考核场次：`/assessments`（创建/列表/详情/更新）
- 客户端：`/client`（开始会话、提交答案、结束）
- 管理成绩：`/admin/assessments/{assessment_id}/results/`（列表）

## 健康检查
`GET /` 返回：
```json
{ "status": "ok", "app_name": "Unity Assessment API" }
```

## 最新更新亮点

### 高并发优化 (2025-12-27)
- **数据库连接池大幅扩容**：支持 1000+ 并发用户
  - 连接池容量：`pool_size=100`, `max_overflow=400`
  - 优化连接超时和回收机制
  - 提升连接池线程安全性

### 自动交卷调度系统 (2025-12)
- **持久化调度任务**：使用数据库存储，服务重启不丢失
- **兜底扫描机制**：每分钟自动检查并提交超时会话
- **提升调度器性能**：线程池扩容，容错时间延长

### 前端配置优化 (2025-12-30)
- **统一配置管理**：使用 `src/constants/index.ts` 管理 API 配置
- **环境变量支持**：通过 `.env` 文件配置后端地址
- **服务监听优化**：前端服务监听 `0.0.0.0:3000`，支持外部访问

### 功能修复 (2025-12-27)
- **题库总分计算修复**：排除扣分题（`DEDUCTION_SINGLE_CHOICE`）计入总分

### 时间统一修复 (2025-12-31)
- **统一时间处理**：所有业务时间统一使用北京时间
  - 考试时间（后台设置）：北京时间
  - 考生交卷时间：北京时间
  - 答题记录时间：北京时间
  - 会话开始时间：北京时间
  - 自动交卷时间：北京时间
- **修复问题**：之前考生提交的交卷时间使用UTC，现在统一为北京时间

## 常见问题

### 后端问题
- **401 未授权**：未授权或 Token 过期
- **403 时间不在考核范围**：未开始或已结束
- **400 重复提交题目**：同一会话内每题只允许提交一次
- **MySQL 连接失败**：检查服务启动、账户权限与库是否存在
- **连接池耗尽**：使用多 worker 模式启动，或检查连接池配置
- **Alembic 失败**：确保已激活虚拟环境

### 前端问题
- **API 请求失败**：检查 `.env` 中的 `VITE_API_BASE_URL` 配置是否正确
- **跨域问题**：确保后端 CORS 配置允许前端域名
- **端口被占用**：修改 `vite.config.ts` 中的端口号

### 调度器问题
- **自动交卷失效**：检查调度器是否正常启动（查看启动日志）
- **任务丢失**：确保数据库连接正常，调度器使用持久化存储
- **兜底扫描未执行**：检查 `register_housekeeping_jobs()` 是否在启动时调用
