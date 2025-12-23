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

## 待修复 BUG

### 1. 成绩记录显示不完全 [待修复]

**问题**：只显示了99条数据，数据库里面已经有1000条数据

**可能原因**：前端或后端有默认的分页限制（limit=100）

---

## 接口压测问题记录

### 问题1：数据库连接池资源不足
```
sqlalchemy.exc.TimeoutError: QueuePool limit of size 5 overflow 10 reached,
connection timed out, timeout 30.00
```

### 问题2：并发重复插入
```
sqlalchemy.exc.IntegrityError: (1062, "Duplicate entry 'user318117' for key
'ix_examinees_identifier'")
```

---

*更新时间：2025-12*
