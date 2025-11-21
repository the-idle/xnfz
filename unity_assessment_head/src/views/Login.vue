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
    console.error("登录报错:", error);

    // --- 核心修复：优先显示 Error 对象的 message ---
    // 因为我们在 auth.ts 里手动 throw new Error(resData.msg)
    let errorMsg = error.message || '登录失败';

    // 汉化处理
    if (errorMsg.includes('Incorrect username or password')) {
        errorMsg = '用户名或密码错误';
    }

    // 只有当是纯网络错误时，才去检查 response (防御性编程)
    if (errorMsg === 'Network Error') {
        errorMsg = '无法连接到服务器';
    }

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