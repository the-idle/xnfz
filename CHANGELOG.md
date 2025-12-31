# 更新日志 (Changelog)

## 最近更新 (2025-12)

### [时间统一修复] - 2025-12-31
**修复：统一所有业务时间为北京时间**
- 修复考生提交的交卷时间使用UTC的问题，现在统一为北京时间
- 统一以下时间处理为北京时间：
  - 考生交卷时间（`AssessmentResult.end_time`）
  - 会话开始时间（`AssessmentResult.start_time`）
  - 答题记录时间（`AnswerLog.answered_at`）
  - 自动交卷时间（调度器强制提交）
- 所有时间统一存储为 naive datetime（去掉时区信息），但逻辑上视为北京时间
- 保持考试时间（后台设置）和业务时间的一致性

**涉及文件：**
- `app/api/endpoints/client.py` - 考生交卷时间
- `app/core/scheduler.py` - 自动交卷时间
- `app/crud/crud_assessment_result.py` - 会话开始时间
- `app/crud/crud_answer_log.py` - 答题记录时间

---

### [cb5c7d8] - 2025-12-31
**更新内容：配置文件上传**
- 添加前端环境变量配置文件 `.env`
- 支持通过环境变量配置 API Base URL

### [e0a55a6] - 2025-12-30
**更新内容：重构 BaseURL 和前端启动配置**
- 重构前端 API 配置，统一使用 `src/constants/index.ts` 管理
- 支持通过环境变量 `VITE_API_BASE_URL` 配置后端地址
- 更新 `vite.config.ts`，前端服务监听 `0.0.0.0:3000`（支持外部访问）
- 统一请求工具使用新的配置常量
- 更新相关视图组件使用新的配置方式

**涉及文件：**
- `unity_assessment_head/src/constants/helpers.ts` (新增)
- `unity_assessment_head/src/constants/index.ts` (新增)
- `unity_assessment_head/src/main.ts`
- `unity_assessment_head/src/stores/auth.ts`
- `unity_assessment_head/src/utils/request.ts`
- `unity_assessment_head/src/views/ClientSimulator.vue`
- `unity_assessment_head/src/views/QuestionCreate.vue`
- `unity_assessment_head/src/views/QuestionList.vue`
- `unity_assessment_head/vite.config.ts`

### [d6b0d67] - 2025-12-30
**更新内容：更新平台名称和 Logo**
- 平台更名为"数字孪生基础比赛管理平台"
- 更换平台 Logo（`public/icon.png`）
- 更新登录页面显示

**涉及文件：**
- `unity_assessment_head/index.html`
- `unity_assessment_head/public/icon.png` (新增)
- `unity_assessment_head/public/电脑.svg` (删除)
- `unity_assessment_head/src/views/Login.vue`

### [b61a55e] - 2025-12-27
**修复：题库总分计算错误**
- 修复计算题库总分时未过滤扣分题的问题
- 现在总分计算会排除 `DEDUCTION_SINGLE_CHOICE` 类型的题目（扣分题不计入总分）

**涉及文件：**
- `app/crud/crud_question_bank.py`

**修复逻辑：**
```python
# 修改前：计算所有题目分数
# 修改后：过滤掉扣分单选题
Question.question_type != QuestionType.DEDUCTION_SINGLE_CHOICE
```

### [857f38e] - 2025-12-27
**优化：高并发场景数据库连接池配置**
- 大幅提升数据库连接池容量，支持 1000+ 并发
- 连接池配置：
  - `pool_size=100`：常驻连接数从 30 提升到 100
  - `max_overflow=400`：最大溢出连接从 70 提升到 400
  - `pool_timeout=3`：连接超时时间缩短到 3 秒
  - `pool_recycle=300`：连接回收时间缩短到 5 分钟
  - `pool_use_lifo=False`：改为先进先出，适合高并发
- 添加连接参数优化（超时、读写超时）
- 增强连接池线程安全性

**涉及文件：**
- `app/db/session.py`
- `app/main.py`
- `.gitignore`

**性能提升：**
- 支持 1000+ 并发用户同时访问
- 减少连接池耗尽导致的超时错误
- 优化连接复用和回收机制

---

## 历史更新

### 自动交卷调度系统优化
- 实现持久化 JobStore（使用数据库存储调度任务）
- 添加每分钟兜底扫描任务，确保超时会话自动提交
- 提升调度器线程池和容错能力

### Redis 缓存系统
- 引入 Redis 缓存题库蓝图数据
- 支持降级到内存缓存（Redis 不可用时）
- 数据变更时自动使缓存失效

### 并发安全优化
- 修复并发创建会话的竞态条件
- 使用异常捕获处理唯一键冲突
- 优化考生和会话的并发创建逻辑

### 成绩记录分页
- 为成绩记录页面添加分页功能
- 支持查看所有历史记录

### 题库管理优化
- 题库列表增加总分列显示
- 修复删除工序时的外键约束错误

