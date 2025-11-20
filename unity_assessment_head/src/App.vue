<template>
  <!-- 路由出口：所有页面都会渲染在这里 -->
  <router-view />
</template>

<script setup lang="ts">
// 这里是根组件，通常不需要写太多逻辑
</script>

<style>
/* 全局样式重置，确保全屏布局 */
html, body, #app {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}
</style>