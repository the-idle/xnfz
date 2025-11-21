import axios from 'axios';
import { ElMessage } from 'element-plus';
import { useAuthStore } from '@/stores/auth';

const service = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/v1', 
  timeout: 5000,
});

// 请求拦截器 (保持不变)
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

// 响应拦截器 (核心修改)
service.interceptors.response.use(
  (response) => {
    // 此时 HTTP 状态码是 200
    // res 结构类似: { code: 404, msg: "No upcoming...", data: null }
    const res = response.data; 

    // 1. 业务成功
    if (res.code === 200) {
      // 兼容：有的接口可能没有 wrap data，或者直接返回了
      return res.data !== undefined ? res.data : res;
    }

    // 2. 业务失败 - 特殊处理 404 (未找到)
    // 我们不希望 404 弹红色的 "系统错误" 或 "No upcoming..."
    if (res.code === 404) {
      // 直接拒绝，把整个 res 对象抛给页面的 catch 去处理
      return Promise.reject(res);
    }

    // 3. 其他业务失败 (如 500, 400 参数错误等)
    // 弹红框提示
    ElMessage.error(res.msg || '操作失败');
    return Promise.reject(new Error(res.msg || 'Error'));
  },
  (error) => {
    // 这里处理 HTTP 状态码非 200 的情况 (如网络断开, Nginx 502 等)
    // ... 之前的 401 处理逻辑保持不变 ...
    const status = error.response ? error.response.status : 0;
    
    if (status === 401) {
        // ... 之前的强制跳转逻辑 ...
        localStorage.removeItem('token');
        if (!window.location.pathname.includes('/login')) {
            ElMessage.error('登录已过期');
            window.location.href = '/login';
            return new Promise(() => {});
        }
    }
    
    ElMessage.error(error.message || '网络请求错误');
    return Promise.reject(error);
  }
);

export default service;