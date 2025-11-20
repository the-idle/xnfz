import axios from 'axios';
import { ElMessage } from 'element-plus';
// 假设你在 store 中管理 token
import { useAuthStore } from '@/stores/auth';

const service = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/v1', // 替换你的服务器地址
  timeout: 5000,
});

// 请求拦截器：注入 Token
service.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore();
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器：处理 UnifiedResponse
service.interceptors.response.use(
  (response) => {
    const res = response.data;
    
    // 文档定义：code === 200 为成功
    if (res.code === 200) {
      return res.data; // 直接返回核心数据 data
    } else {
      // 业务错误处理
      ElMessage.error(res.msg || '系统错误');
      return Promise.reject(new Error(res.msg || 'Error'));
    }
  },
  (error) => {
    // HTTP 状态码错误处理 (401, 404, 500)
    if (error.response && error.response.status === 401) {
      ElMessage.error('登录已过期，请重新登录');
      // 这里可以执行登出逻辑
    } else {
      ElMessage.error(error.message || '网络请求失败');
    }
    return Promise.reject(error);
  }
);

export default service;