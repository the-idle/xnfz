<template>
    <div class="app-layout">
      <!-- 左侧侧边栏 -->
      <el-aside width="220px" class="sidebar">
        <div class="logo">虚拟实训考核后台管理</div>
        <el-menu
          :default-active="$route.path"
          router
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
        >
          <el-sub-menu index="1">
            <template #title>
              <el-icon><Files /></el-icon><span>内容管理</span>
            </template>
            <el-menu-item index="/platforms">平台列表</el-menu-item>
          </el-sub-menu>
          <el-menu-item index="/users">
            <template #title>
              <el-icon><User /></el-icon><span>用户管理</span>
            </template>
            </el-menu-item>
          <el-sub-menu index="2">
            <template #title>
              <el-icon><Timer /></el-icon><span>考核管理</span>
            </template>
            <el-menu-item index="/assessments">场次发布</el-menu-item>
            <el-menu-item index="/sessions">成绩记录</el-menu-item>
          </el-sub-menu>

          <el-menu-item index="/simulator">
            <template #title>
              <el-icon><User /></el-icon><span>模拟考生(Debug)</span>
            </template>
            </el-menu-item>
        </el-menu>
      </el-aside>
  
      <!-- 右侧主体 -->
      <el-container>
        <el-header class="header">
          <div class="breadcrumb">
            <!-- 这里可以加面包屑 -->
            {{ $route.meta.title }}
          </div>
          <el-button type="danger" link @click="handleLogout">退出登录</el-button>
        </el-header>
        
        <el-main class="main-content">
          <!-- 核心：路由出口 -->
          <router-view /> 
        </el-main>
      </el-container>
    </div>
  </template>
  
  <script setup lang="ts">
  import { useRouter } from 'vue-router';
  import { useAuthStore } from '@/stores/auth';
  import { Files, Timer } from '@element-plus/icons-vue'; // 记得安装 icons
  
  const router = useRouter();
  const authStore = useAuthStore();
  
  const handleLogout = () => {
    authStore.logout();
    router.push('/login');
  };
  </script>
  
  <style scoped>
  .app-layout { display: flex; height: 100vh; }
  .sidebar { background-color: #304156; color: white; }
  .logo { height: 60px; line-height: 60px; text-align: center; font-weight: bold; font-size: 20px; background: #2b3649; }
  .header { background: #fff; border-bottom: 1px solid #dcdfe6; display: flex; justify-content: space-between; align-items: center; padding: 0 20px; }
  .main-content { background: #f0f2f5; padding: 20px; }
  </style>