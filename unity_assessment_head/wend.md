好的，遵照您的指示。我将重新分析您项目中的所有接口，并为您生成一份最新的、面向 AI 或前端开发者的 API 接口文档与开发指南。

这份文档将基于您代码的最新状态，特别是包含了最近可能修改过的业务逻辑（如 `crud_answer_log.py` 中的计分规则），确保前端可以准确、高效地开发后台管理系统。

---

### **Unity Assessment API - 接口文档与前端开发指南 (V1.1)**

#### **摘要**

本文档为 `Unity Assessment API` 的最新版本提供了一份全面的技术说明，旨在指导前端（包括 AI 辅助开发）快速、准确地构建一个功能完备的后台管理系统。文档详细描述了 API 的基础架构、认证流程、核心业务工作流、所有端点的技术细节，并特别指出了关键业务逻辑（如答题计分规则）。此外，本文档还提供了前端架构的技术选型和开发模式建议。

---

#### **1. 基础信息 (Base Information)**

*   **API 根路径 (Base URL)**: `http://<your_server_address>/api/v1`
*   **技术栈**: FastAPI, Pydantic, SQLAlchemy
*   **统一响应格式 (`app/schemas/response.py`)**: 所有 API 端点均遵循统一的响应结构，前端应封装一个统一的处理器来解析。
    ```typescript
    interface UnifiedResponse<T> {
      code: number;      // 业务状态码, 200 表示成功
      msg: string;       // 响应消息, "success" 或错误信息
      data?: T | null;   // 核心数据负载
    }
    ```

---

#### **2. 认证 (Authentication)**

系统采用 OAuth2 密码流和 JWT 进行认证。

1.  **获取访问令牌 (Access Token)**:
    *   **功能**: 用户登录，获取 `access_token`。
    *   **端点**: `POST /login/token`
    *   **请求头**: `Content-Type: application/x-www-form-urlencoded`
    *   **请求体 (Form Data)**: `username` (string), `password` (string)
    *   **成功响应 (200 OK)**:
        ```json
        {
          "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
          "token_type": "bearer"
        }
        ```

2.  **使用令牌**:
    *   在所有需要认证的 API 请求的 **请求头 (Header)** 中携带令牌。
    *   **格式**: `Authorization: Bearer <your_access_token>`

---

#### **3. 核心工作流与数据模型 (Core Workflow & Data Models)**

后台管理系统的核心是**内容管理**和**考核管理**。前端界面设计和路由应遵循此逻辑。

**层级结构**: `平台 (Platform)` -> `题库 (Question Bank)` -> `工序/点位 (Procedure)` -> `题目 (Question)`

**核心操作流程**:

1.  **内容创建**: 按照上述层级，依次创建平台、题库、工序、题目。
2.  **考核设置**: 创建一个 `考核场次 (Assessment)`，并关联一个 `题库`。
3.  **考生考试**: 客户端（如 Unity）通过 `客户端接口` 获取考核内容，并提交答案。
4.  **结果查看**: 在后台管理系统中，查看 `考核会话 (Assessment Session)` 和 `答题日志 (Answer Log)`，分析考核结果。

---

#### **4. API 端点详解 (Detailed API Endpoints)**

##### **4.1 平台管理 (Platforms)** - `app/api/endpoints/platforms.py`

*   `POST /platforms/`: **创建平台**
    *   请求体: `schemas.PlatformCreate` (`name`, `description`)
    *   注意: 平台名称唯一，重复会返回 400 错误。
*   `GET /platforms/`: **获取平台列表** (分页)
    *   查询参数: `skip`, `limit`
*   `GET /platforms/{platform_id}`: **获取单个平台**
*   `PUT /platforms/{platform_id}`: **更新平台**
    *   请求体: `schemas.PlatformUpdate` (所有字段可选)
*   `DELETE /platforms/{platform_id}`: **删除平台**

##### **4.2 题库管理 (Question Banks)** - `app/api/endpoints/question_banks.py`

*   `POST /platforms/{platform_id}/question-banks/`: **为平台创建题库**
    *   请求体: `schemas.QuestionBankCreate` (`name`)
*   `GET /platforms/{platform_id}/question-banks/`: **获取平台下的题库列表**

##### **4.3 工序/点位管理 (Procedures)** - `app/api/endpoints/procedures.py`

*   `POST /question-banks/{question_bank_id}/procedures/`: **为题库创建工序**
    *   请求体: `schemas.ProcedureCreate` (`name`)
*   `GET /question-banks/{question_bank_id}/procedures/`: **获取题库下的工序列表**

##### **4.4 题目管理 (Questions)** - `app/api/endpoints/questions.py`

*   `POST /procedures/{procedure_id}/questions/`: **为工序创建题目 (含图片)**
    *   **重要**: 这是一个 `multipart/form-data` 请求。
    *   **请求体 (Form Data)**:
        *   `question_data`: (string) 一个序列化为 JSON 字符串的题目对象，结构符合 `schemas.QuestionCreate`。
        *   `image_file`: (File) (可选) 图片文件。
    *   **`question_data` 示例**:
        ```json
        {
          "prompt": "题目文本",
          "question_type": "SINGLE_CHOICE", // "SINGLE_CHOICE" 或 "MULTIPLE_CHOICE"
          "scene_identifier": "unique_scene_id_01",
          "score": 10,
          "options": [
            { "option_text": "选项A", "is_correct": false },
            { "option_text": "选项B", "is_correct": true }
          ]
        }
        ```
*   `GET /procedures/{procedure_id}/questions/`: **获取工序下的题目列表**

##### **4.5 考核场次管理 (Assessments)** - `app/api/endpoints/assessments.py`

*   `POST /assessments/`: **创建考核场次**
    *   请求体: `schemas.AssessmentCreate` (`title`, `start_time`, `end_time`, `question_bank_id`)
    *   注意: 同一题库在时间上存在冲突的场次会返回 409 错误。
*   `GET /assessments/`: **获取考核场次列表**

##### **4.6 考核会话与结果 (Sessions & Results)** - `app/api/endpoints/sessions.py`

*   `GET /sessions/`: **获取所有考核会话列表** (分页)
    *   功能: 查看所有考生的考试记录。
    *   查询参数: `skip`, `limit`
*   `GET /sessions/{session_id}`: **获取单个考核会话详情**
    *   功能: 查看某一次具体考试的详细信息，包括总分和所有答题记录。
    *   响应: `schemas.AssessmentSessionWithLogs`

---

#### **5. 客户端接口与计分逻辑 (Client API & Scoring Logic)**

这部分接口主要由考生端（如 Unity）调用，但后台管理系统需要理解其逻辑以正确展示结果。

*   `GET /client/assessments/recent`: **获取最近的有效考核**
*   `POST /client/assessments/{assessment_id}/session`: **开始或恢复考核**
    *   请求体: `schemas.AssessmentStartRequest` (`examinee_identifier`)
    *   响应: 返回 `schemas.AssessmentBlueprintResponse`，包含该场考核的所有题目结构。
*   `POST /client/sessions/{session_id}/log`: **提交答案**
    *   请求体: `schemas.AnswerLogIn` (`question_id`, `selected_option_ids`)
    *   **核心计分逻辑 (`app/crud/crud_answer_log.py`)**:
        *   **单选题**:
            *   答对：得满分 (`question.score`)。
            *   答错：得 0 分。
        *   **多选题**:
            *   **全对**: 选项完全匹配，得满分 (`question.score`)。
            *   **漏选**: 选择了正确答案的子集，得一半的分数 (`round(question.score / 2)`)。
            *   **错选**: 只要包含一个错误选项，得 0 分。

---

#### **6. 前端开发执行指南 (Front-end Execution Guide)**

作为前端框架师，我建议 AI 或开发者按以下步骤执行，以最高效率生成后台管理系统：

*   **技术选型**:
    *   **框架**: **Vue 3 (Composition API)** + **TypeScript**
    *   **UI 库**: **Element Plus** 或 **Naive UI** (组件丰富，适合快速搭建)
    *   **HTTP 客户端**: **axios**
    *   **状态管理**: **Pinia**

*   **开发步骤**:

    1.  **环境搭建**: 使用 `Vite` 创建一个新的 Vue 3 + TypeScript 项目，并集成 Element Plus。
    2.  **API 层封装**:
        *   在 `src/api/` 目录下，按资源创建 `platform.ts`, `question.ts`, `assessment.ts` 等文件。
        *   封装 `axios` 实例，使用请求拦截器自动注入 `Authorization` 头，使用响应拦截器统一处理 `UnifiedResponse` 格式。
    3.  **类型定义**:
        *   在 `src/types/api/` 目录下，根据本文档中的 Schemas 创建对应的 TypeScript `interface`。这是实现类型安全和智能提示的关键。
    4.  **认证与路由**:
        *   创建登录页面 (`Login.vue`)。
        *   使用 Pinia 创建一个 `auth` store，管理 `token` 和用户信息。
        *   配置 `vue-router`，添加全局路由守卫 (`beforeEach`)，实现未登录跳转。
    5.  **布局与菜单**:
        *   创建主布局组件，包含侧边栏菜单和内容展示区。
        *   菜单结构应与核心工作流匹配：平台管理 -> 题库管理 -> ... -> 考核管理 -> 考核结果。
    6.  **页面开发 (CRUD)**:
        *   **平台管理**: 从最顶层的平台管理开始，实现一个包含表格 (Table) 和表单 (Form) 的标准 CRUD 页面。
        *   **层级深入**: 逐级实现题库、工序、题目的管理。在每一级的列表页面中，应有“查看下一级”或“管理子项”的入口。
        *   **题目创建**: 特别注意题目创建页面，需要使用 `El-Upload` 组件来处理 `multipart/form-data` 请求，将题目数据（JSON 字符串）和图片文件一并提交。
        *   **考核结果**: 创建页面展示 `GET /sessions/` 的数据。点击某条记录时，跳转到详情页，调用 `GET /sessions/{session_id}`，并以清晰的格式展示考生的每一题答案、得分和正确答案。
    7.  **部署**: 完成开发后，执行 `npm run build`，将 `dist` 目录下的静态文件部署到 Nginx 或其他 Web 服务器。

---

**结论**

这份更新后的文档为前端开发提供了清晰、准确的蓝图。API 设计合理，业务逻辑明确。请前端开发者（或 AI）严格遵循此文档，特别是注意 `multipart/form-data` 的处理和计分逻辑的展示。从认证和平台管理的 CRUD 开始，即可快速启动项目开发。