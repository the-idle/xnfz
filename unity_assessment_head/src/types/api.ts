// types.ts

// --- 通用 API 响应结构 ---
// T 代表具体的数据类型，比如 Platform[] 或 User
export interface ApiResponse<T = any> {
  code: number;
  msg: string;
  data: T;
}

// --- 平台 ---
export interface Platform {
  id: number;
  name: string;
  description?: string;
}

// --- 题目创建参数 ---
export interface QuestionCreate {
  prompt: string;
  question_type: 'SINGLE_CHOICE' | 'MULTIPLE_CHOICE';
  scene_identifier: string;
  score: number;
  options: { option_text: string; is_correct: boolean }[];
}

// --- 考核场次 (Assessment) ---
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
  is_active: boolean;
}

// --- 答题日志 (Answer Log) ---
export interface AnswerLog {
  id: number;
  question_id: number;
  selected_option_ids: number[];
  is_correct: boolean;
  score_awarded: number;
  timestamp: string;
  question?: {
    prompt: string;
    score: number;
    options: { id: number; option_text: string; is_correct: boolean }[];
  };
}

// --- 考核会话 (Session) ---
export interface AssessmentSession {
  id: number;
  examinee_identifier: string;
  start_time: string;
  end_time?: string;
  total_score: number;
  assessment_id: number;
}

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

// 题目列表项
export interface Question {
  id: number;
  prompt: string;
  question_type: 'SINGLE_CHOICE' | 'MULTIPLE_CHOICE';
  score: number;
  scene_identifier: string;
  image_url?: string;
}