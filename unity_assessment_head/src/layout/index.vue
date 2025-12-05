<template>
  <div class="app-layout">
    <!-- 左侧侧边栏 -->
    <el-aside width="220px" class="sidebar">
      
      <!-- Logo 区域 (修复版：使用图标代替图片，防止报错) -->
      <div class="logo-container">
        <el-icon class="logo-icon" :size="28"><Monitor /></el-icon>
        <span class="logo-text">实训考核管理平台</span>
      </div>

      <el-menu
        :default-active="$route.path"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        class="el-menu-vertical"
      >
        <!-- 1. 内容管理 -->
        <el-sub-menu index="1">
          <template #title>
            <el-icon><Files /></el-icon><span>内容管理</span>
          </template>
          <el-menu-item index="/platforms">平台列表</el-menu-item>
          <!-- 将用户管理放在内容管理下，或者单独放都可以，这里按你之前的习惯单独放 -->
        </el-sub-menu>

        <!-- 2. 用户管理 (独立一级菜单) -->
        <el-menu-item index="/users">
          <el-icon><User /></el-icon><span>用户管理</span>
        </el-menu-item>

        <!-- 3. 考核管理 -->
        <el-sub-menu index="2">
          <template #title>
            <el-icon><Timer /></el-icon><span>考核管理</span>
          </template>
          <el-menu-item index="/assessments">场次发布</el-menu-item>
          <el-menu-item index="/sessions">成绩记录</el-menu-item>
        </el-sub-menu>

        <!-- 4. 模拟端 -->
        <el-menu-item index="/simulator">
          <el-icon><DataBoard /></el-icon><span>模拟考生(Debug)</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 右侧主体 -->
    <el-container>
      <el-header class="header">
        <div class="breadcrumb">
          <!-- 简单的当前页面标题显示 -->
          {{ $route.meta.title }}
        </div>
        <div class="header-right">
          <el-button type="danger" link @click="handleLogout">退出登录</el-button>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <router-view /> 
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
// 引入需要的图标
import { Files, Timer, User, Monitor, DataBoard } from '@element-plus/icons-vue';

const router = useRouter();
const authStore = useAuthStore();

const handleLogout = () => {
  authStore.logout();
  router.push('/login');
};
</script>

<style scoped>
.app-layout { display: flex; height: 100vh; }

.sidebar { 
  background-color: #304156; 
  color: white; 
  display: flex;
  flex-direction: column;
  overflow: hidden; /* 防止Logo溢出 */
}

/* --- Logo 区域样式 --- */
.logo-container {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #2b3649; /* 比侧边栏稍深，形成区分 */
  box-shadow: 0 1px 4px rgba(0,0,0,0.12);
  color: #fff;
  font-weight: 600;
  font-size: 16px;
  letter-spacing: 1px;
  white-space: nowrap; /* 防止文字换行 */
}

.logo-icon {
  margin-right: 10px;
  color: #409EFF; /* 图标用品牌色点缀 */
}

.el-menu-vertical {
  border-right: none;
  width: 100%;
}

/* --- 顶部 Header --- */
.header { 
  background: #fff; 
  border-bottom: 1px solid #dcdfe6; 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  padding: 0 20px; 
  height: 64px;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
}

.breadcrumb {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.main-content { 
  background: #f0f2f5; 
  padding: 20px; 
}
</style>