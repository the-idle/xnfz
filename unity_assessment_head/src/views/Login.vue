<template>
    <div class="login-container">
      <el-card class="login-card">
        <template #header><h2>Unity考核系统登录</h2></template>
        <el-form :model="form" label-position="top">
          <el-form-item label="用户名">
            <el-input v-model="form.username" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="form.password" type="password" show-password @keyup.enter="handleLogin" />
          </el-form-item>
          <!-- 绑定点击事件 -->
          <el-button type="primary" style="width: 100%" @click="handleLogin" :loading="loading">
            登录
          </el-button>
        </el-form>
      </el-card>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref } from 'vue';
  import { useRouter } from 'vue-router';
  import { useAuthStore } from '@/stores/auth';
  import { ElMessage } from 'element-plus';
  
  const router = useRouter();
  const authStore = useAuthStore();
  const form = ref({ username: '', password: '' });
  const loading = ref(false);
  
  const handleLogin = async () => {
    console.log("点击了登录按钮"); // 1. 确认点击生效
    
    if (!form.value.username || !form.value.password) {
      ElMessage.warning('请输入用户名和密码');
      return;
    }
  
    loading.value = true;
    try {
      await authStore.login(form.value.username, form.value.password);
      ElMessage.success('登录成功');
      router.push('/platforms'); // 跳转到平台列表
    } catch (error: any) {
      console.error("登录失败详情:", error);
      // 显示具体错误信息
      const errorMsg = error.response?.data?.detail || '登录失败，请检查后端连接';
      ElMessage.error(errorMsg);
    } finally {
      loading.value = false;
    }
  };
  </script>
  
  <style scoped>
  .login-container { height: 100vh; display: flex; justify-content: center; align-items: center; background: #2d3a4b; }
  .login-card { width: 400px; }
  </style>