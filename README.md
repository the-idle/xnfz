测试
### **最终联调测试：完整流程验证**

请打开您的 Swagger UI (`http://127.0.0.1:8000/docs`)，并严格按照以下步骤操作。

#### **第一阶段：【后台管理员】准备考核内容**

**1. 登录 (获取钥匙)**
   *   进入 `login` 分组。
   *   点击右上角的 **"Authorize"** 按钮。
   *   在弹窗中输入 `username: admin`, `password: password`，然后点击 "Authorize" 获取全局授权。

**2. 创建平台 (Platform)**
   *   进入 `platforms` 分组。
   *   使用 `POST /platforms/` 创建一个平台。
   *   请求体：`{ "name": "综合技能考核平台 V2" }`
   *   **记下**返回的 `id`，假设是 **`1`**。

**3. 创建题库 (Question Bank)**
   *   进入 `question-banks` 分组。
   *   使用 `POST /question-banks/` 创建一个题库。
   *   请求体：`{ "name": "车间安全操作题库", "platform_id": 1 }` (这里的 platform_id 就是上一步的ID)
   *   **记下**返回的 `id`，假设是 **`1`**。

**4. 创建工序/点位 (Procedure)**
   *   进入 `procedures` 分组。
   *   使用 `POST /question-banks/{question_bank_id}/procedures/`。
   *   路径参数 `question_bank_id`: **`1`**。
   *   请求体：`{ "name": "车床安全检查点" }`
   *   **记下**返回的 `id`，假设是 **`1`**。

**5. 创建题目 (Question)**
   *   进入 `questions` 分组。
   *   使用 `POST /procedures/{procedure_id}/questions/`。
   *   路径参数 `procedure_id`: **`1`**。
   *   **请求体 (这是一个包含选项的复杂JSON):**
     ```json
     {
       "prompt": "在操作车床前，必须佩戴的个人防护用品是什么？",
       "question_type": "SINGLE_CHOICE",
       "scene_identifier": "lathe_safety_check_01",
       "score": 10,
       "image_url": null,
       "options": [
         {
           "option_text": "手套",
           "is_correct": false
         },
         {
           "option_text": "防护眼镜",
           "is_correct": true
         },
         {
           "option_text": "安全帽",
           "is_correct": false
         }
       ]
     }
     ```
   *   执行创建。

**6. 创建考核场次 (Assessment)**
   *   进入 `assessments` 分组。
   *   使用 `POST /assessments/`。
   *   请求体：
     ```json
     {
       "title": "2025年度车间安全专项考核",
       "start_time": "2025-01-01T00:00:00",
       "end_time": "2025-12-31T23:59:59",
       "question_bank_id": 1
     }
     ```
   *   **记下**返回的 `id`，假设是 **`1`**。

至此，我们的后台数据准备工作全部完成！我们有了一个完整的、可供考核的数据链条。

---

#### **第二阶段：【Unity 客户端】进行考核**

现在，我们切换到 `client` 分组，模拟考生的操作。

**7. 考生开始考核**
   *   进入 `client` 分组。
   *   使用 `POST /client/assessments/{assessment_id}/session`。
   *   路径参数 `assessment_id`: **`1`**。
   *   请求体：`{ "examinee_identifier": "UNITY_CLIENT_001" }`
   *   **验证与记录**:
      *   **预期结果**: 您应该会收到一个 `200 OK` 的响应。
      *   响应体中的 `procedures` 列表应该不再是空的，它会包含一个名为“车床安全检查点”的工序，该工序下包含了我们刚刚创建的那道题目，并且每个选项都有一个临时的 `answer_id`。
      *   **记下**返回的 `assessment_result_id` (假设是 **`1`**) 和 “防护眼镜” 那个选项的 `answer_id` (假设是 **`2`**)。

**8. 考生提交答案**
   *   **【重要】** 这一步我们的后端逻辑还没有完全实现（之前的代码是简化版），但我们可以测试接口是否能被调用。
   *   找到 `client` 分组下的 `POST /assessment-results/{result_id}/answer` 接口。
   *   路径参数 `result_id`: **`1`**。
   *   请求体：`{ "selected_answer_ids": [2] }` (提交“防护眼镜”的答案ID)
   *   **验证**:
      *   **预期结果**: 您应该会收到一个 `200 OK` 的响应，`score_awarded` 可能是 10，`is_correct` 是 `true`。

**9. （可选）断点续考验证**
   *   再次执行第 7 步的 `POST /client/assessments/1/session` 请求。
   *   **预期结果**: 理想情况下（在我们实现了完整的断点续考逻辑后），返回的 `procedures` 列表中应该不再包含您刚刚回答过的那道题。在当前的简化实现下，它可能仍然会返回所有题目。

**10. 结束考核**
    *   找到 `client` 分组下的 `POST /assessment-results/{result_id}/finish` 接口。
    *   路径参数 `result_id`: **`1`**。
    *   执行请求。
    *   **预期结果**: 收到 `200 OK`，状态为 `finished`，`final_score` 为您在考核中获得的总分。

---
