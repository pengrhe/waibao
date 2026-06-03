import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const Layout = () => import('@/layouts/AdminLayout.vue')
const Placeholder = () => import('@/views/_placeholder/index.vue')

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/login/index.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '工作台', icon: 'DataLine', group: 'main' },
      },
      // 商品 / 内容
      { path: 'products', name: 'products', component: () => import('@/views/products/index.vue'), meta: { title: '商品管理', icon: 'Goods', group: 'catalog' } },
      { path: 'patterns', name: 'patterns', component: () => import('@/views/patterns/index.vue'), meta: { title: '印花库', icon: 'Picture', group: 'catalog' } },
      { path: 'banners', name: 'banners', component: () => import('@/views/banners/index.vue'), meta: { title: 'Banner', icon: 'Picture', group: 'catalog' } },
      { path: 'topics', name: 'topics', component: () => import('@/views/topics/index.vue'), meta: { title: '首页专区', icon: 'Collection', group: 'catalog' } },
      { path: 'city-ip', name: 'city-ip', component: () => import('@/views/city-ip/index.vue'), meta: { title: '城市 IP 库', icon: 'LocationFilled', group: 'catalog' } },
      // C 端
      { path: 'users', name: 'users', component: () => import('@/views/users/index.vue'), meta: { title: '用户管理', icon: 'User', group: 'c_user' } },
      { path: 'coupons', name: 'coupons', component: () => import('@/views/coupons/index.vue'), meta: { title: '优惠券', icon: 'Discount', group: 'c_user' } },
      // 订单
      { path: 'orders', name: 'orders', component: () => import('@/views/orders/index.vue'), meta: { title: '订单管理', icon: 'List', group: 'order' } },
      { path: 'refunds', name: 'refunds', component: Placeholder, meta: { title: '退款审核', icon: 'RefreshLeft', group: 'order' } },
      // B 端
      { path: 'partners', name: 'partners', component: () => import('@/views/partners/index.vue'), meta: { title: '联营伙伴', icon: 'Connection', group: 'b_user' } },
      { path: 'stores', name: 'stores', component: () => import('@/views/stores/index.vue'), meta: { title: '加盟店', icon: 'Shop', group: 'b_user' } },
      { path: 'staff', name: 'staff', component: Placeholder, meta: { title: '店员', icon: 'Avatar', group: 'b_user' } },
      { path: 'devices', name: 'devices', component: Placeholder, meta: { title: '打印机/设备', icon: 'Printer', group: 'b_user' } },
      // 财务
      { path: 'finance', name: 'finance', component: Placeholder, meta: { title: '财务总览', icon: 'Money', group: 'finance' } },
      { path: 'withdrawals', name: 'withdrawals', component: Placeholder, meta: { title: '提现审核', icon: 'CreditCard', group: 'finance' } },
      { path: 'reconciliations', name: 'reconciliations', component: Placeholder, meta: { title: '对账', icon: 'Tickets', group: 'finance' } },
      // 数据 / 系统
      { path: 'bi', name: 'bi', component: Placeholder, meta: { title: '数据统计', icon: 'TrendCharts', group: 'system' } },
      { path: 'model-channels', name: 'model-channels', component: () => import('@/views/model-channels/index.vue'), meta: { title: 'AI 模型通道', icon: 'MagicStick', group: 'system' } },
      { path: 'system-config', name: 'system-config', component: () => import('@/views/system-config/index.vue'), meta: { title: '系统配置', icon: 'Setting', group: 'system' } },
      { path: 'admin-users', name: 'admin-users', component: Placeholder, meta: { title: '后台账号', icon: 'UserFilled', group: 'system' } },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

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

export default router
