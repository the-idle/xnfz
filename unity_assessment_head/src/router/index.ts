import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth' // 假设你使用 Pinia 管理 Auth





// 定义路由配置
const routes: Array<RouteRecordRaw> = [
  // 1. 登录页 (独立页面)
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' }
  },

  // 2. 主布局 (包含侧边栏和顶部的容器)
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/layout/index.vue'), // 下面我会提供这个文件的代码
    redirect: '/platforms', // 默认跳转到平台管理
    children: [
      // --- 平台与内容管理 ---
      {
        path: 'platforms',
        name: 'PlatformList',
        component: () => import('@/views/PlatformList.vue'),
        meta: { title: '平台管理' }
      },
      // 题库管理 (通常从平台列表跳转过来)
      {
        path: 'platforms/:platformId/banks',
        name: 'BankList',
        component: () => import('@/views/BankList.vue'), // 需要你补充这个文件，逻辑同 PlatformList
        meta: { title: '题库管理' }
      },
      // 工序管理
      {
        path: 'banks/:bankId/procedures',
        name: 'ProcedureList',
        component: () => import('@/views/ProcedureList.vue'), // 需要你补充这个文件
        meta: { title: '工序管理' }
      },
      // 题目列表
      {
        path: 'procedures/:procedureId/questions',
        name: 'QuestionList',
        component: () => import('@/views/QuestionList.vue'), // 需要你补充这个文件
        meta: { title: '题目管理' }
      },
      // 题目创建 (我们之前写的复杂表单)
      {
        path: 'procedures/:procedureId/questions/create',
        name: 'QuestionCreate',
        component: () => import('@/views/QuestionCreate.vue'),
        meta: { title: '创建题目' }
      },
      {
        path: 'procedures/:procedureId/questions/:questionId/edit',
        name: 'QuestionEdit',
        component: () => import('@/views/QuestionCreate.vue'),
        meta: { title: '编辑题目' }
      },

      // --- 考核管理 ---
      {
        path: 'assessments',
        name: 'AssessmentList',
        component: () => import('@/views/AssessmentList.vue'),
        meta: { title: '考核发布' }
      },

      // --- 成绩与会话 ---
      {
        path: 'sessions',
        name: 'SessionList',
        component: () => import('@/views/SessionList.vue'),
        meta: { title: '成绩记录' }
      },
      {
        path: 'sessions/:id',
        name: 'SessionDetail',
        component: () => import('@/views/SessionDetail.vue'),
        meta: { title: '考核详情' }
      },
      {
        path: 'simulator',
        name: 'ClientSimulator',
        component: () => import('@/views/ClientSimulator.vue'),
        meta: { title: '模拟考生(Debug)' }
      },
      {
        path: 'users',
        name: 'UserList',
        component: () => import('@/views/UserList.vue'),
        meta: { title: '用户管理' }
      },
    ]
  },

  // 3. 404 处理
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/404.vue') // 建议创建一个简单的 404 页
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// 全局路由守卫：处理登录鉴权
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const isAuthenticated = !!authStore.token // 或者检查 localStorage.getItem('token')

  if (to.name !== 'Login' && !isAuthenticated) {
    // 未登录且去的不是登录页 -> 重定向到登录
    next({ name: 'Login' })
  } else {
    next()
  }
})

export default router