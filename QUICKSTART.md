# 快速启动指南

本文档提供项目快速启动的完整步骤。

## 一、后端启动

### 1. 环境准备
```bash
# 激活虚拟环境
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 数据库配置
确保 MySQL 服务已启动，并在项目根目录创建 `.env` 文件：
```bash
APP_NAME="Unity Assessment API"
DEBUG=True
SECRET_KEY="change-this-secret"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL="mysql+pymysql://root:root@localhost:3306/unity_assessment"
```

### 3. 数据库迁移
```bash
alembic upgrade head
```

### 4. 初始化管理员
```bash
python initial_data.py
```
默认账号：`admin / password`

### 5. 启动后端服务

**开发模式（推荐，热重载）：**
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**生产/压测模式（多 worker，支持高并发）：**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

> 提示：日常开发使用 `--reload` 模式即可，支持代码修改后自动重启。压测或生产环境建议使用多 worker 模式。

访问 Swagger UI: http://127.0.0.1:8000/docs

---

## 二、前端启动

### 1. 进入前端目录
```bash
cd unity_assessment_head
```

### 2. 安装依赖
```bash
npm install
```

### 3. 配置环境变量（可选）
在 `unity_assessment_head` 目录创建 `.env` 文件：
```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```

### 4. 启动前端服务
```bash
npm run dev
```

前端访问地址：http://localhost:3000

---

## 三、完整测试流程

### 1. 功能测试
1. 访问前端：http://localhost:3000
2. 使用 `admin / password` 登录
3. 创建平台 → 题库 → 工序 → 题目 → 考核场次
4. 使用客户端接口开始考试并提交答案

### 2. 自动交卷测试
1. 创建一场短期考核（开始时间=当前+1分钟，结束时间=当前+3分钟）
2. 开始会话后不提交任何答案，也不手动结束
3. 等待考核结束时间后，检查会话是否自动提交（`end_time` 字段被设置）

### 3. 并发测试
1. 使用多 worker 模式启动后端
2. 使用 JMeter 或类似工具进行压力测试
3. 观察连接池和调度器是否正常工作

---

## 四、常见问题排查

### 后端无法启动
- 检查 MySQL 服务是否运行
- 检查 `.env` 配置是否正确
- 检查端口 8000 是否被占用

### 前端无法连接后端
- 检查后端服务是否启动
- 检查 `.env` 中的 `VITE_API_BASE_URL` 配置
- 检查浏览器控制台错误信息

### 自动交卷不工作
- 检查启动日志中是否有 "APScheduler started..."
- 检查数据库中是否有 `apscheduler_jobs` 表
- 查看调度器日志是否有错误

### 高并发连接被拒绝
- 使用多 worker 模式启动：`--workers 4`
- 检查数据库连接池配置（`app/db/session.py`）
- 确保 MySQL 最大连接数足够

---

## 五、项目结构

```
unity_assessment/
├── app/                    # 后端应用
│   ├── api/               # API 路由
│   ├── core/              # 核心配置（调度器、缓存等）
│   ├── crud/              # 数据访问层
│   ├── models/            # 数据库模型
│   └── schemas/           # 数据验证模型
├── unity_assessment_head/ # 前端应用
│   ├── src/
│   │   ├── views/         # 页面组件
│   │   ├── stores/        # 状态管理
│   │   └── utils/         # 工具函数
│   └── package.json
├── alembic/               # 数据库迁移
├── static/                # 静态资源
└── requirements.txt       # Python 依赖
```

---

## 六、相关文档

- [项目详细说明](./PROJECT_OVERVIEW.md)
- [API 接口文档](./README.md)
- [更新日志](./CHANGELOG.md)
- [待实现功能](./TODO_FEATURES.md)

