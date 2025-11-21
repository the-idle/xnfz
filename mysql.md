这是一个为您编写的配套说明文档。您可以将此文档作为**后端开发文档**或**Unity 开发接入指南**存档。

---

# 虚拟实训考核平台 V1.0 - 数据库说明文档

**文档版本：** 1.0
**数据库名称：** `unity_assessment_v1.0`
**更新日期：** 2025-11-22

---

## 1. 概述
本项目数据库旨在支持《虚拟实训考核平台》的数据存储需求。系统采用 MySQL 8.0+ 构建，主要功能包括：
*   **基础数据管理**：管理平台信息、题库版本。
*   **考核内容管理**：分层级存储“工序（点位）”、“问题”、“选项”及关联图片资源。
*   **用户与成绩管理**：存储考生信息、考试场次、答题日志及最终得分。

## 2. 核心层级结构
为了适配 3D 虚拟仿真场景，数据库采用了以下层级逻辑，Unity 客户端应按此逻辑请求数据：

1.  **平台 (Platforms)**：顶层容器（如：虚拟实训考核平台）。
2.  **题库 (Question Banks)**：具体的试卷集合（如：题库 1.0）。
3.  **工序/点位 (Procedures)**：**对应 3D 场景中的具体位置**（如：“工序一”、“班组园地”）。玩家走到该位置触发答题。
4.  **题目 (Questions)**：该点位下包含的一道或多道题目。
5.  **选项 (Options)**：题目对应的答案选项。

---

## 3. 数据表与 Markdown 题库映射说明

上一轮导入的 SQL 数据是根据 Markdown 题库文件生成的。以下是字段的对应关系，方便开发人员理解数据来源：

| Markdown 概念 | 数据库表 (Table) | 关键字段说明 | 备注 |
| :--- | :--- | :--- | :--- |
| **点位** | `procedures` | `name` | 例如："工序一"、"灭火器检查场景" |
| **问题** | `questions` | `prompt` (题干) | 例如："物料标识卡是否存在问题？" |
| **图片** | `questions` | `image_url` | 存储相对路径，例如 `/assets/images/场景/工序一.jpg` |
| **类型** | `questions` | `question_type` | `SINGLE_CHOICE` (单选), `MULTIPLE_CHOICE` (多选) |
| **分数** | `questions` | `score` | 该题目的分值 |
| **选项** | `options` | `option_text` | 选项的具体内容 |
| **答案** | `options` | `is_correct` | `1` 为正确，`0` 为错误 |

---

## 4. 资源路径配置 (Unity 注意事项)

在 SQL 脚本中，涉及图片的题目已自动生成了 `image_url` 字段。Unity 客户端需要根据实际的资源存放方式进行读取：

*   **数据库中的值示例**：`/assets/images/工序一/物料标识卡.jpg`
*   **开发建议**：
    *   **方案 A (本地加载)**：将图片放在 Unity 的 `StreamingAssets` 文件夹下，读取时将数据库路径拼接为 `Application.streamingAssetsPath + db_url`。
    *   **方案 B (网络加载)**：如果图片部署在 Web 服务器上，拼接 Base URL，例如 `http://your-server.com/static` + `db_url`。

---

## 5. 默认管理员账户

初始化脚本中包含了一个默认的管理员账户，用于后台管理系统（如有）：

*   **用户名 (username)**: `admin`
*   **密码 (password)**: `123456`
    *   *注意：数据库中存储的是 Bcrypt 哈希值，并非明文。*

---

## 6. 常用 SQL 查询语句 (开发调试用)

### 6.1 查询某个点位的所有题目
```sql
SELECT 
    p.name AS 点位名称, 
    q.prompt AS 题目, 
    q.score AS 分数, 
    q.question_type AS 类型
FROM procedures p
JOIN questions q ON p.id = q.procedure_id
WHERE p.name = '工序一';
```

### 6.2 查询某道题的正确答案
```sql
SELECT 
    q.prompt AS 题目, 
    o.option_text AS 正确选项
FROM questions q
JOIN options o ON q.id = o.question_id
WHERE q.prompt LIKE '%物料标识卡%' AND o.is_correct = 1;
```

### 6.3 重置所有考试记录 (清空流水)
在测试阶段，如果你想清空所有答题记录但保留题库：
```sql
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE answer_logs;
TRUNCATE TABLE assessment_results;
TRUNCATE TABLE examinees;
SET FOREIGN_KEY_CHECKS = 1;
```

---

## 7. 扩展性建议

1.  **图片资源替换**：
    目前的图片路径是模拟生成的。请让 UI/3D 设计师导出对应的图片，并更新数据库中的 `image_url` 字段，或者将图片重命名以匹配数据库中的路径。
2.  **评分逻辑**：
    *   **单选**：选中 `is_correct=1` 的选项即得分。
    *   **多选**：数据库中该题目对应的所有 `is_correct=1` 的选项ID必须完全匹配用户提交的选项ID列表（少选/错选的逻辑需在代码层实现，数据库仅存储标准答案）。

---

**文档结束**