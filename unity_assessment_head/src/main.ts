import { createApp } from 'vue'
import { createPinia } from 'pinia'

// --- 1. 引入 Element Plus 及其样式 ---
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
// 引入图标
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'

const app = createApp(App)

// --- 2. 注册插件 ---
app.use(createPinia())
app.use(router)
app.use(ElementPlus) // 启用 UI 库

// --- 3. 全局注册图标 ---
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.mount('#app')