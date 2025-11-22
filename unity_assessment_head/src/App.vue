<template>
  <!-- 使用 ElConfigProvider 包裹路由出口，并绑定中文语言包 -->
  <el-config-provider :locale="locale">
    <router-view />
  </el-config-provider>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElConfigProvider } from 'element-plus'
// 引入中文语言包
import zhCn from 'element-plus/es/locale/lang/zh-cn'

const locale = ref(zhCn)
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