import { createWebHistory, createRouter, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@aitee/shared'
import { modules, moduleList } from '../modules'

const Shell = () => import('../views/Shell.vue')
const Login = () => import('../views/Login.vue')

// 把每个 role 的子路由挂在 /:role/* 下，共用 Shell
const moduleRoutes: RouteRecordRaw[] = moduleList.map((m) => ({
  path: `/${m.role}`,
  component: Shell,
  redirect: `/${m.role}/dashboard`,
  meta: { requiredRole: m.role },
  children: m.routes,
}))

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: Login,
    meta: { public: true },
  },
  ...moduleRoutes,
  { path: '/', redirect: '/login' },
  { path: '/:pathMatch(.*)*', redirect: '/login' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.meta?.public) {
    // 已登录访问 login → 直接跳对应主页
    if (to.name === 'login' && auth.isAuthed && auth.user?.role) {
      return { path: `/${auth.user.role}/dashboard`, replace: true }
    }
    return true
  }

  if (!auth.isAuthed || !auth.user) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  // 角色越权：访问别的 role 的路由 → 跳回自己 dashboard
  const required = (to.meta?.requiredRole as string | undefined)
    ?? (typeof to.path === 'string' ? to.path.split('/')[1] : undefined)
  if (required && required in modules && required !== auth.user.role) {
    return { path: `/${auth.user.role}/dashboard`, replace: true }
  }

  return true
})

export default router
