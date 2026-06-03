import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from './auth'

export function createPortalRouter(routes: RouteRecordRaw[]) {
  const router = createRouter({
    history: createWebHistory(),
    routes,
  })
  router.beforeEach((to) => {
    const auth = useAuthStore()
    if (to.meta?.public) return true
    if (!auth.isAuthed) {
      return { path: '/login', query: { redirect: to.fullPath } }
    }
    return true
  })
  return router
}
