import { defineStore } from 'pinia';
import { ref } from 'vue';
import axios from 'axios';

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '');

  // 确保地址正确
  const LOGIN_URL = 'http://127.0.0.1:8000/api/v1/login/token';

  const login = async (username, password) => {
    // 构建表单数据
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);

    try {
      // 发送请求
      const res = await axios.post(LOGIN_URL, params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      const resData = res.data;

      // --- 核心修复：优先处理统一响应格式的错误 ---
      // 你的截图显示后端返回了 { code: 400, msg: "...", data: null }
      if (resData.code && resData.code !== 200) {
        // 抛出后端返回的具体错误信息 (例如 "Incorrect username or password")
        throw new Error(resData.msg || '登录失败');
      }

      // --- 获取 Token ---
      // 兼容两种情况：
      // 1. 标准 OAuth2: 直接在根对象 { access_token: "..." }
      // 2. 统一响应: 在 data 字段 { data: { access_token: "..." } }
      const accessToken = resData.access_token || resData.data?.access_token;

      if (accessToken) {
        token.value = accessToken;
        localStorage.setItem('token', accessToken);
      } else {
        // 如果 code 是 200 但没有 token，这才是真正的“未获取到 Token”
        throw new Error('登录成功但未获取到令牌');
      }

    } catch (error: any) {
      // 重新抛出错误给 Login.vue 处理
      // 如果是 axios 的网络错误，保留原样；如果是我们上面 throw new Error 的，也保留
      throw error;
    }
  };

  const logout = () => {
    token.value = '';
    localStorage.removeItem('token');
  };

  return { token, login, logout };
});