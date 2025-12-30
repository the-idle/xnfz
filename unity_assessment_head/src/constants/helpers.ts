// src/constants/helpers.ts
import constants, { API_BASE_URL, API_CONFIG } from './index';

/**
 * 获取完整的 API URL
 */
export function getApiUrl(endpoint: string): string {
  return `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
}

/**
 * 获取 API 配置
 */
export function getApiConfig() {
  return { ...API_CONFIG };
}

/**
 * 导出所有常量
 */
export { API_BASE_URL, API_CONFIG, constants };
export default constants;