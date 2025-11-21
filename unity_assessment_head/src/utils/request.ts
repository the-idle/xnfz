import axios from 'axios';
import { ElMessage } from 'element-plus';
import { useAuthStore } from '@/stores/auth';

const service = axios.create({
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

// 响应拦截器 (核心逻辑)
service.interceptors.response.use(
  (response) => {
    const res = response.data;

    // 1. 业务成功 (Code 200)
    if (res.code === 200) {
      // 直接返回 data，页面里拿到的就是核心数据
      return res.data;
    }

    // 2. 业务失败 (Code 400, 401, 404, 500 等)
    // 构造一个 Error 对象，把后端的 msg 放进去
    const error = new Error(res.msg || '未知错误');
    // 把业务状态码也挂载上去，方便后续判断
    (error as any).code = res.code;
    
    // 特殊处理 401 (Token 过期)
    if (res.code === 401) {
      if (!window.location.pathname.includes('/login')) {
        ElMessage.error(res.msg || '登录已过期，请重新登录');
        localStorage.removeItem('token');
        window.location.href = '/login';
        return new Promise(() => {}); // 阻断后续逻辑
      }
    }

    // 抛出错误，让页面组件 (Login.vue) 去 catch 并显示
    return Promise.reject(error);
  },
  (error) => {
    // 这里处理的是 HTTP 状态码非 200 的情况 (网络断开、Nginx 报错等)
    console.error('Network Error:', error);
    ElMessage.error(error.message || '网络连接异常');
    return Promise.reject(error);
  }
);

export default service;