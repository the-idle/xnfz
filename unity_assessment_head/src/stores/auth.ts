import { defineStore } from 'pinia';
import { ref } from 'vue';
import axios from 'axios';
// 引入我们封装好的 request，而不是原生 axios，这样才能享受拦截器的红利！
import request from '@/utils/request'; 

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '');

  const login = async (username, password) => {
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);

    try {
      // 使用封装好的 request 发送请求
      // 注意：baseURL 已经在 request.ts 里配好了，这里只写相对路径
      // 这里的 res 已经是拦截器解包后的 data 部分了（如果包含 token）
      // 但因为登录接口比较特殊，Token 有时不在 data 里，我们做个兼容
      
      // 为了处理特殊的登录格式，我们这里还是得用原生 axios 发一次请求，
      // 但要手动处理一下结果，保持和拦截器逻辑一致
      const rawRes = await axios.post('http://127.0.0.1:8000/api/v1/login/token', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });

      const resData = rawRes.data;

      // 1. 检查业务状态码
      if (resData.code && resData.code !== 200) {
        // 直接抛出后端返回的中文 msg
        throw new Error(resData.msg);
      }

      // 2. 提取 Token
      const accessToken = resData.access_token || resData.data?.access_token;

      if (accessToken) {
        token.value = accessToken;
        localStorage.setItem('token', accessToken);
      } else {
        throw new Error('登录成功，但未获取到令牌');
      }

    } catch (error: any) {
      // 抛出错误给 Login.vue
      throw error;
    }
  };

  const logout = () => {
    token.value = '';
    localStorage.removeItem('token');
  };

  return { token, login, logout };
});