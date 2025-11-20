import { defineStore } from 'pinia';
import { ref } from 'vue';
import axios from 'axios'; // 使用原生 axios，绕过拦截器

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '');

  // 1. 确保这里的地址是你后端的真实地址
  // 注意：必须指向 /login/token
  const LOGIN_URL = 'http://127.0.0.1:8000/api/v1/login/token';

  const login = async (username, password) => {
    console.log("正在尝试登录:", username); // 调试日志

    // 2. 构建表单数据 (OAuth2 密码流标准)
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);

    try {
      // 3. 发送请求
      const res = await axios.post(LOGIN_URL, params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      console.log("登录响应:", res.data); // 调试日志

      // 4. 保存 Token
      if (res.data.access_token) {
        token.value = res.data.access_token;
        localStorage.setItem('token', res.data.access_token);
      } else {
        throw new Error('未获取到 Token');
      }
    } catch (error: any) {
      console.error("登录请求出错:", error);
      // 抛出错误让 Login.vue 捕获并显示提示
      throw error;
    }
  };

  const logout = () => {
    token.value = '';
    localStorage.removeItem('token');
  };

  return { token, login, logout };
});