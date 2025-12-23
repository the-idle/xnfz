# 虚拟实训考核平台优化记录

---

## 已完成

### 1. 题库管理增加总分列 [已完成]

**需求**：前端题库管理的表格增加一列题库总分

**修改文件**：
- `app/schemas/question_bank.py` - 添加 `total_score` 字段
- `app/crud/crud_question_bank.py` - 添加 `get_total_score()` 方法计算题库总分
- `app/api/endpoints/question_banks.py` - 在返回题库列表时计算并填入总分
- `unity_assessment_head/src/views/BankList.vue` - 前端显示总分列

---

### 2. 工序管理删除工序报错 [已修复]

**问题**：删除工序时报 500 错误
```
pymysql.err.IntegrityError: (1451, 'Cannot delete or update a parent row:
a foreign key constraint fails (`unity_assessment_v1.0`.`answer_logs`,
CONSTRAINT `fk_logs_question` FOREIGN KEY (`question_id`) REFERENCES `questions` (`id`))')
```

**原因**：删除工序会级联删除题目，但题目被 `answer_logs` 表的外键引用

**解决方案**：在删除工序前，先删除相关的 `answer_logs` 记录

**修改文件**：
- `app/crud/crud_procedure.py` - 重写 `remove()` 方法，删除前先清理关联的 answer_logs

---

### 3. 成绩记录显示不完全 [已修复]

**问题**：只显示了99条数据，数据库里面已经有1000条数据

**原因**：后端 API 默认 `limit=100`，前端没有分页功能

**解决方案**：为成绩记录页面添加分页功能

**修改文件**：
- `app/crud/crud_assessment_result.py` - 添加 `get_count_by_assessment()` 方法获取总数
- `app/api/endpoints/results.py` - 修改 API 返回 `{ items, total }` 分页格式
- `unity_assessment_head/src/views/SessionList.vue` - 添加 el-pagination 分页组件

---

### 4. 接口压测问题优化 [已优化]

#### 问题1：数据库连接池资源不足
```
sqlalchemy.exc.TimeoutError: QueuePool limit of size 5 overflow 10 reached,
connection timed out, timeout 30.00
```

**解决方案**：优化连接池配置

**修改文件**：
- `app/db/session.py` - 优化连接池参数
  - `pool_size=30` - 常驻连接数
  - `max_overflow=70` - 最大溢出连接数
  - `pool_timeout=10` - 缩短超时时间，快速失败
  - `pool_use_lifo=True` - 后进先出，减少空闲连接超时
  - `pool_recycle=1800` - 30分钟回收连接
  - `expire_on_commit=False` - 减少不必要的刷新查询
  - `echo=False` - 关闭SQL日志减少开销

---

#### 问题2：并发重复插入
```
sqlalchemy.exc.IntegrityError: (1062, "Duplicate entry 'user318117' for key
'ix_examinees_identifier'")
```

**原因**：`get_or_create_by_identifier` 存在竞态条件（Race Condition）
- 线程 A 查询不存在 → 线程 B 查询不存在 → 线程 A 插入成功 → 线程 B 插入失败

**解决方案**：使用异常捕获处理并发冲突

**修改文件**：
- `app/crud/crud_examinee.py` - 重写 `get_or_create_by_identifier()` 方法
  - 使用 `try/except IntegrityError` 捕获唯一键冲突
  - 冲突后回滚并重新查询

- `app/crud/crud_assessment_result.py` - 添加 `get_or_create_active_session()` 方法
  - 同样使用异常捕获处理会话创建的并发冲突

- `app/api/endpoints/client.py` - 使用新的并发安全方法

---

## 待实现功能

### 1. 密码查看功能（暂缓）

**需求描述**：
- **用户管理界面**：每行用户旁添加密码列，默认显示 `**` 状态，点击小眼睛可以展示明文密码
- **平台管理界面**：同上，添加密码列用于查看平台密码

**技术难点**：
当前系统使用 `hashed_password` 存储加密后的密码（单向哈希），无法还原为明文密码。

**可选方案**：
1. **新增明文密码字段**：在数据库中新增 `plain_password` 字段存储明文密码
   - 优点：可随时查看密码
   - 缺点：安全性较低，需要修改数据库模型、添加迁移、修改CRUD逻辑

2. **仅在创建/修改时显示**：只在创建或修改密码的响应中返回明文密码
   - 优点：安全性较高
   - 缺点：错过查看时机后无法再查看

**涉及修改文件**：
- 后端：
  - `app/models/user_management.py` - User 模型
  - `app/models/question_management.py` - Platform 模型
  - `app/schemas/user.py` - 用户响应模型
  - `app/schemas/platform.py` - 平台响应模型
  - `app/crud/` - 相关 CRUD 操作
  - 需要新增 Alembic 迁移脚本

- 前端：
  - `unity_assessment_head/src/views/UserList.vue`
  - `unity_assessment_head/src/views/PlatformList.vue`

---

*更新时间：2025-12*
