// 平台
export interface Platform {
    id: number;
    name: string;
    description?: string;
  }
  
  // 题目创建参数
export interface QuestionCreate {
prompt: string;
question_type: 'SINGLE_CHOICE' | 'MULTIPLE_CHOICE';
scene_identifier: string;
score: number;
options: { option_text: string; is_correct: boolean }[];
}

// --- 1. 考核场次 (Assessment) ---
export interface AssessmentCreate {
    title: string;
    start_time: string; // ISOString
    end_time: string;   // ISOString
    question_bank_id: number;
  }
  
  export interface Assessment {
    id: number;
    title: string;
    start_time: string;
    end_time: string;
    question_bank_id: number;
    is_active: boolean; // 假设后端有这个字段推导，或者前端根据时间判断
  }
  
  // --- 2. 答题日志 (Answer Log) ---
  // 对应后端 schema: AnswerLog
  export interface AnswerLog {
    id: number;
    question_id: number;
    selected_option_ids: number[];
    is_correct: boolean;
    score_awarded: number; // 实际得分 (核心字段：用于展示 0分, 半分, 满分)
    timestamp: string;
    // 通常列表接口可能不会返回题目详情，但在详情页我们需要知道题干
    // 假设后端 Session详情接口 嵌套了 question 信息，或者前端需要额外获取
    question?: { 
      prompt: string; 
      score: number; // 题目满分
      options: { id: number; option_text: string; is_correct: boolean }[] 
    }; 
  }
  
  // --- 3. 考核会话 (Session) ---
  // 对应后端 schema: AssessmentSession
  export interface AssessmentSession {
    id: number;
    examinee_identifier: string; // 考生标识
    start_time: string;
    end_time?: string;
    total_score: number;
    assessment_id: number;
  }
  
  // 对应后端 schema: AssessmentSessionWithLogs (详情页用)
  export interface AssessmentSessionDetail extends AssessmentSession {
    logs: AnswerLog[];
  }

  export interface QuestionBank {
  id: number;
  name: string;
  platform_id: number;
}

export interface Procedure {
  id: number;
  name: string;
  question_bank_id: number;
}

// 题目列表项（简化版）
export interface Question {
  id: number;
  prompt: string;
  question_type: 'SINGLE_CHOICE' | 'MULTIPLE_CHOICE';
  score: number;
  scene_identifier: string;
  image_url?: string; // 假设后端返回这个
}