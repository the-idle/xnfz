import axios from 'axios';
import { ElMessage } from 'element-plus';
import { useAuthStore } from '@/stores/auth';

const service = axios.create({
  // 确保地址正确
  baseURL: 'http://127.0.0.1:8000/api/v1', 
  timeout: 5000,
});

// 请求拦截器
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

// 响应拦截器
service.interceptors.response.use(
  (response) => {
    const res = response.data;
    if (res.code && res.code !== 200) {
      ElMessage.error(res.msg || '系统错误');
      return Promise.reject(new Error(res.msg || 'Error'));
    }
    return res.data !== undefined ? res.data : res;
  },
  (error) => {
    const status = error.response ? error.response.status : 0;
    const msg = error.response?.data?.detail || error.message || '网络请求失败';

    // --- 核心修复：401 彻底阻断报错 ---
    if (status === 401) {
      // 1. 避免在登录页重复触发
      if (!window.location.pathname.includes('/login')) {
        console.warn('Token 失效，正在强制登出...');
        
        // 2. 物理清除 Token (绕过 Pinia，防止 Store 未初始化报错)
        localStorage.removeItem('token');
        
        // 3. 提示用户
        ElMessage.error('登录已过期，请重新登录');
        
        // 4. 强制跳转 (使用 replace 防止后退)
        window.location.replace('/login');
        
        // 5. 【关键】返回一个永远 pending 的 Promise
        // 这会中断后续代码执行（如组件里的 catch），防止控制台报红字
        return new Promise(() => {}); 
      }
    }

    // --- 400/422 业务错误 ---
    if (status === 400 || status === 422) {
      return Promise.reject(error);
    }

    // --- 其他错误 ---
    ElMessage.error(msg);
    return Promise.reject(error);
  }
);

export default service;