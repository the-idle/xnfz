# Unity Assessment API 项目说明与运行指南

Unity Assessment API 是一个基于 FastAPI 的后端服务，用于管理和下发“平台-题库-工序/点位-题目-选项”的分层考核内容，并为 Unity 客户端提供考核会话、答案提交、成绩查询等接口。

- 框架与技术栈：FastAPI, Pydantic v2, SQLAlchemy, Alembic, JWT(OAuth2), MySQL/SQLite, Uvicorn
- 统一响应：所有业务端点返回统一结构 `{ code, msg, data }`
- API 前缀：`/api/v1`
- 静态资源：`/static`（图片等）

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
开发（热重载）：
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

生产 / 压测推荐（多 worker，缓解拒连）：
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```
可按机器核数调整 `--workers`，并确保数据库/Redis 连接池参数与之匹配。

Swagger UI: http://127.0.0.1:8000/docs

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

## 常见问题
- 401 未授权：未授权或 Token 过期
- 403 时间不在考核范围：未开始或已结束
- 400 重复提交题目：同一会话内每题只允许提交一次
- MySQL 连接失败：检查服务启动、账户权限与库是否存在
- Alembic 失败：确保已激活虚拟环境
