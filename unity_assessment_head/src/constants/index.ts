// src/constants/index.ts
// 类型定义
export interface ApiConfig {
  BASE_URL: string;
  TIMEOUT: number;
}

// 常量定义
export const API_CONFIG: ApiConfig = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
  TIMEOUT: 30000,
} as const;

// 导出单个常量（便于导入）
export const API_BASE_URL = API_CONFIG.BASE_URL;
export const API_TIMEOUT = API_CONFIG.TIMEOUT;

// 导出默认对象
const constants = {
  API: API_CONFIG,
} as const;

export type AppConstants = typeof constants;
export default constants;