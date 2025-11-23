import axios, { type InternalAxiosRequestConfig, type AxiosResponse } from 'axios';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useAuthStore } from '@/stores/auth';
import router from '@/router'; // 建议引入路由实例，用来做无刷新跳转

const service = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/v1',
  timeout: 5000,
});

// --- 辅助函数：处理登出逻辑 ---
// 避免在两个地方写重复的代码
const handleLogout = () => {
  const authStore = useAuthStore();
  // 1. 清除 Token (Pinia 和 LocalStorage)
  authStore.logout(); // 假设你在 store 里封装了 logout action，如果没有，就手动 clear
  localStorage.removeItem('token'); // 双重保险

  // 2. 防止重复弹窗
  if (!window.location.pathname.includes('/login')) {
    ElMessageBox.alert('登录状态已失效，请重新登录', '系统提示', {
      confirmButtonText: '重新登录',
      type: 'warning',
      callback: () => {
        // 3. 跳转回登录页 (使用 window.location 会强制刷新，更干净)
        window.location.href = '/login'; 
      }
    });
  }
};

// --- 请求拦截器 ---
service.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const authStore = useAuthStore();
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// --- 响应拦截器 ---
service.interceptors.response.use(
  (response: AxiosResponse) => {
    // 注意：这里拿到的 response.data 是后端返回的完整 JSON { code: 200, msg: "OK", data: [...] }
    const res = response.data;

    // 情况 A：后端框架封装的业务成功
    if (res.code === 200) {
      return res.data; // 脱壳，直接返回核心数据
    }

    // 情况 B：后端返回 HTTP 200，但业务 Code 是 401 (软 401)
    if (res.code === 401) {
      handleLogout();
      return Promise.reject(new Error(res.msg || 'Token expired'));
    }

    // 情况 C：其他业务错误 (如 code: 400 参数错误, 403 无权限)
    ElMessage.error(res.msg || '系统未知错误');
    const error = new Error(res.msg || '未知错误');
    // @ts-ignore 用于后续逻辑判断
    error.code = res.code; 
    return Promise.reject(error);
  },
  (error) => {
    // 情况 D：HTTP 状态码非 200 (硬错误)
    // ★★★ 这里是你之前遗漏的关键点 ★★★
    
    // 1. 捕获 HTTP 401 (FastAPI/Spring Security 等标准鉴权失败)
    if (error.response && error.response.status === 401) {
      handleLogout();
      return Promise.reject(error);
    }

    // 2. 处理其他 HTTP 错误
    console.error('Network Error:', error);
    let message = error.message || '请求失败';
    if (error.response && error.response.data) {
       // 尝试读取后端返回的详细错误信息
       message = error.response.data.detail || error.response.data.msg || message;
    }
    
    ElMessage.error(message);
    return Promise.reject(error);
  }
);

export default service;