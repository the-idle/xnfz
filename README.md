# Unity Assessment API 前端快速上手接口文档

面向前端/Unity 客户端的接口说明，包含端点、授权、请求体与响应示例，以及单选、多选、扣分单选的操作与评分规则，帮助你快速联调。

- 基础地址（Base URL）：`http://127.0.0.1:8000/api/v1`
- 统一响应结构：`{ code, msg, data }`
- 授权方式：Bearer Token（Swagger 右上角 Authorize）

## 一、授权登录

- 端点：`POST /login/token`
- 描述：使用用户名/密码换取访问令牌（access_token）
- 请求（表单，OAuth2PasswordRequestForm）：
  - `username`: `admin`
  - `password`: `password`
- 响应示例：
```json
{
  "access_token": "xxx.yyy.zzz",
  "token_type": "bearer"
}
```
- 用法：在后续所有需要管理员权限的操作中，在 Header 中加入：
  - `Authorization: Bearer {access_token}`

## 二、数据准备（后台管理员）

按此顺序创建资源。所有路径均带 `/api/v1` 前缀。

### 1) 创建平台（Platform）
- 端点：`POST /platforms/`（需要管理员权限）
- 请求体：
```json
{ "name": "综合技能考核平台 V2" }
```
- 响应字段（data）：
  - `id`: 平台 ID（记录下来，示例记作 `platform_id = 1`）

### 2) 创建题库（Question Bank）
- 端点：`POST /platforms/{platform_id}/question-banks/`（需要管理员权限）
- 路径参数：`platform_id = 1`
- 请求体：
```json
{ "name": "车间安全操作题库" }
```
- 响应字段（data）：
  - `id`: 题库 ID（记录下来，示例记作 `question_bank_id = 1`）

### 3) 创建工序/点位（Procedure）
- 端点：`POST /question-banks/{question_bank_id}/procedures/`（需要管理员权限）
- 路径参数：`question_bank_id = 1`
- 请求体：
```json
{ "name": "车床安全检查点" }
```
- 响应字段（data）：
  - `id`: 工序/点位 ID（记录下来，示例记作 `procedure_id = 1`）

### 4) 创建题目（Question，含选项，支持图片）
- 端点：`POST /procedures/{procedure_id}/questions/`（需要管理员权限）
- 路径参数：`procedure_id = 1`
- Content-Type：`multipart/form-data`
- 字段说明：
  - `question_data`: 字符串类型的 JSON（必须），结构应符合下方示例
  - `image_file`: 图片文件（可选，`image/jpeg|png|gif`）
- `question_data` 示例（字符串内容为下方 JSON）：
```json
{
  "prompt": "在操作车床前，必须佩戴的个人防护用品是什么？",
  "question_type": "SINGLE_CHOICE",
  "scene_identifier": "lathe_safety_check_01",
  "score": 10,
  "image_url": null,
  "options": [
    { "option_text": "手套", "is_correct": false },
    { "option_text": "防护眼镜", "is_correct": true },
    { "option_text": "安全帽", "is_correct": false }
  ]
}
```
- 注意：
  - `question_type` 可选值：
    - `SINGLE_CHOICE`（单选题）
    - `MULTIPLE_CHOICE`（多选题）
    - `DEDUCTION_SINGLE_CHOICE`（扣分单选题）
  - 服务端会把 `image_file` 存储到 `static/images`，并将相对路径写入题目的 `image_url`
  - 如果 `scene_identifier` 重复，服务端会拒绝创建（避免 Unity 场景标识冲突）

### 5) 创建考核场次（Assessment）
- 端点：`POST /assessments/`（需要管理员权限）
- 请求体：
```json
{
  "title": "2025年度车间安全专项考核",
  "start_time": "2025-01-01T00:00:00",
  "end_time": "2025-12-31T23:59:59",
  "question_bank_id": 1
}
```
- 响应字段（data）：
  - `id`: 考核场次 ID（记录下来，示例记作 `assessment_id = 1`）
- 说明：服务端会校验同平台下的时间冲突，若冲突返回 409

## 三、客户端联调（Unity / 前端）

### 1) 获取最近可用的考核
- 端点：`GET /client/assessments/recent`
- 描述：返回最近且正在进行中的一场考核
- 响应（data）：`Assessment` 对象（包含 `id`, `title`, `start_time`, `end_time`, `question_bank_id`）

### 2) 开始/继续考核会话
- 端点：`POST /client/assessments/{assessment_id}/session`
- 路径参数：`assessment_id = 1`
- 请求体：
```json
{ "examinee_identifier": "UNITY_CLIENT_001" }
```
- 响应（data）：
```json
{
  "assessment_result_id": 1,
  "procedures": [
    {
      "id": 1,
      "name": "车床安全检查点",
      "questions": [
        {
          "id": 1,
          "scene_identifier": "lathe_safety_check_01",
          "prompt": "在操作车床前，必须佩戴的个人防护用品是什么？",
          "question_type": "single_choice",
          "score": 10,
          "image_url": "/static/images/xxx.jpg",
          "options": [
            { "id": 10, "option_text": "手套" },
            { "id": 11, "option_text": "防护眼镜" },
            { "id": 12, "option_text": "安全帽" }
          ]
        }
      ]
    }
  ]
}
```
- 说明：
  - 返回的 `options.id` 是“真实选项 ID”，用于答案提交（不存在“临时 answer_id”）
  - `question_type` 值为小写枚举：`single_choice` / `multiple_choice` / `deduction_single_choice`

### 3) 提交答案（关键）
- 端点：`POST /client/assessment-results/{result_id}/answer`
- 路径参数：`result_id = 1`（来自会话响应的 `assessment_result_id`）
- 请求体（统一结构）：
```json
{
  "examinee_identifier": "UNITY_CLIENT_001",
  "procedure_id": 1,
  "question_id": 1,
  "selected_option_ids": [11]
}
```
- 字段说明：
  - `examinee_identifier`：必须与会话创建时一致（服务端会校验）
  - `procedure_id`：该题所属工序/点位的 ID
  - `question_id`：题目 ID
  - `selected_option_ids`：
    - 单选题：数组中应只有一个选项 ID（例如 `[11]`）
    - 多选题：数组中包含所有选择的选项 ID（例如 `[11, 12]`）
- 响应（data）：
```json
{
  "status": "ok",
  "score_awarded": 10,
  "is_correct": true
}
```

#### 评分规则（请严格遵循）
- 单选题 `single_choice`：
  - 选择集合与正确集合完全相同（通常是单个 ID），`is_correct = true`，`score_awarded = 题目满分`
  - 否则 `is_correct = false`，`score_awarded = 0`

- 多选题 `multiple_choice`：
  - 若提交的选项包含任何错误选项（不属于正确集合），`is_correct = false`，`score_awarded = 0`
  - 若提交选项为“正确集合的子集但不完全相等”，`is_correct = false`，`score_awarded = round(题目满分 / 2)`（半分）
  - 若提交选项与正确集合完全相同，`is_correct = true`，`score_awarded = 题目满分`

- 扣分单选题 `deduction_single_choice`：
  - 答对不得分：`is_correct = true`，`score_awarded = 0`
  - 答错扣满分：`is_correct = false`，`score_awarded = -题目满分`（总分会被扣减）

- 其他重要约束：
  - 同一会话中同一题目只能提交一次；否则服务端返回 `400`（重复提交）
  - 提交时间必须在考核时间范围内；否则返回 `403`
  - 所有分数累计到 `result.total_score`（可能为负数，如果有扣分题）

### 4) 结束考核
- 端点：`POST /client/assessment-results/{result_id}/finish`
- 路径参数：`result_id = 1`
- 请求体：
```json
{ "examinee_identifier": "UNITY_CLIENT_001" }
```
- 响应（data）：
```json
{ "status": "finished", "final_score": 10 }
```
- 说明：结束后会话 `end_time` 写入，不可再提交答案

## 四、统一响应结构

所有业务端点统一返回：
```json
{
  "code": 200,
  "msg": "success",
  "data": { ... }
}
```
- 成功：HTTP 200，`code=200`
- 业务异常：HTTP 200，但 `code != 200`（由服务端业务异常处理器转换）
- 标准 HTTP 异常：如 400/403/404/409，`code` 与 HTTP 状态码一致

## 五、常见错误与排查

- 401 未授权：忘记 Authorize 或 Token 过期
- 403 时间限制：当前不在考核时间范围
- 404 资源不存在：检查 ID 是否正确
- 400 重复提交：同一题不可再次提交
- 415/400 创建题目：`multipart/form-data` 与 `question_data` JSON 字符串格式不正确

## 六、快速联调流程（复盘）

1. Authorize 登录（`admin/password`）
2. 创建平台 → 题库 → 工序/点位 → 题目（可带图片） → 考核场次
3. 客户端开始会话（拿到 `assessment_result_id`）
4. 按题提交答案（单选/多选/扣分单选遵循评分规则）
5. 结束考核（得到 `final_score`）
