<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header><h2>Unity考核系统登录</h2></template>
      <el-form :model="form" label-position="top">
        <el-form-item label="用户名">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input 
            v-model="form.password" 
            type="password" 
            show-password 
            placeholder="请输入密码"
            @keyup.enter="handleLogin" 
          />
        </el-form-item>
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
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入用户名和密码');
    return;
  }

  loading.value = true;
  try {
    await authStore.login(form.value.username, form.value.password);
    
    ElMessage.success('登录成功');
    router.push('/platforms'); 
  } catch (error: any) {
    console.error("Login error:", error);
    
    // --- 核心修复：直接显示错误信息 ---
    // 这里的 error.message 就是后端返回的 "用户名或密码错误"
    const msg = error.message || '登录失败，请检查网络';
    ElMessage.error(msg);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-container { height: 100vh; display: flex; justify-content: center; align-items: center; background: #2d3a4b; }
.login-card { width: 400px; }
</style>