import { createRouter, createWebHistory } from 'vue-router'
import { checkAuth } from '../api'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { title: '登录', noAuth: true },
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { title: '仪表盘' },
  },
  {
    path: '/posts',
    name: 'PostList',
    component: () => import('../views/PostList.vue'),
    meta: { title: '文章管理' },
  },
  {
    path: '/posts/new',
    name: 'PostCreate',
    component: () => import('../views/PostEditor.vue'),
    meta: { title: '新建文章' },
  },
  {
    path: '/posts/:id/edit',
    name: 'PostEdit',
    component: () => import('../views/PostEditor.vue'),
    meta: { title: '编辑文章' },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/Settings.vue'),
    meta: { title: '网站设置' },
  },
  {
    path: '/images',
    name: 'Images',
    component: () => import('../views/Images.vue'),
    meta: { title: '图片管理' },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// 导航守卫：未登录重定向到登录页
router.beforeEach(async (to) => {
  // 登录页不需要认证
  if (to.meta.noAuth) return true

  const token = localStorage.getItem('admin_token')

  // 有 token → 验证是否有效
  if (token) {
    try {
      await checkAuth()
      return true
    } catch {
      // token 失效，清除并重定向
      localStorage.removeItem('admin_token')
      return { name: 'Login' }
    }
  }

  // 无 token → 检查服务器是否需要认证
  try {
    await checkAuth()
    // 服务器不需要认证（未设 ADMIN_PASSWORD），直接通过
    return true
  } catch {
    // 需要认证，重定向到登录页
    return { name: 'Login' }
  }
})

export default router
