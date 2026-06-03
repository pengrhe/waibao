import { createRouter, createWebHashHistory, type RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/pages/home/index.vue'),
    meta: { title: 'aitee', tabbar: true },
  },
  {
    path: '/gallery',
    name: 'gallery',
    component: () => import('@/pages/gallery/index.vue'),
    meta: { title: '印花库', tabbar: true },
  },
  {
    path: '/editor',
    name: 'editor',
    component: () => import('@/pages/editor/index.vue'),
    meta: { title: '定制', tabbar: true },
  },
  {
    path: '/cart',
    name: 'cart',
    component: () => import('@/pages/cart/index.vue'),
    meta: { title: '购物车', tabbar: true },
  },
  {
    path: '/mine',
    name: 'mine',
    component: () => import('@/pages/mine/index.vue'),
    meta: { title: '我的', tabbar: true },
  },
  {
    path: '/product-picker',
    name: 'product-picker',
    component: () => import('@/pages/product-picker/index.vue'),
    meta: { title: '款式选择' },
  },
  {
    path: '/checkout',
    name: 'checkout',
    component: () => import('@/pages/checkout/index.vue'),
    meta: { title: '确认订单' },
  },
  {
    path: '/order/list',
    name: 'order-list',
    component: () => import('@/pages/order/list.vue'),
    meta: { title: '我的订单' },
  },
  {
    path: '/order/:id',
    name: 'order-detail',
    component: () => import('@/pages/order/detail.vue'),
    meta: { title: '订单详情' },
  },
  {
    path: '/design-list',
    name: 'design-list',
    component: () => import('@/pages/design-list/index.vue'),
    meta: { title: '我的设计' },
  },
  {
    path: '/address/list',
    name: 'address-list',
    component: () => import('@/pages/address/list.vue'),
    meta: { title: '收货地址' },
  },
  {
    path: '/address/edit',
    name: 'address-edit',
    component: () => import('@/pages/address/edit.vue'),
    meta: { title: '编辑地址' },
  },
  {
    path: '/coupon',
    name: 'coupon',
    component: () => import('@/pages/coupon/index.vue'),
    meta: { title: '我的优惠券' },
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/pages/login/index.vue'),
    meta: { title: '登录' },
  },
  {
    path: '/ai-create',
    name: 'ai-create',
    component: () => import('@/pages/ai-create/index.vue'),
    meta: { title: 'AI 创作' },
  },
  {
    path: '/upload-result',
    name: 'upload-result',
    component: () => import('@/pages/upload-result/index.vue'),
    meta: { title: '来图定制' },
  },
  {
    path: '/city-ip',
    name: 'city-ip',
    component: () => import('@/pages/city-ip/index.vue'),
    meta: { title: 'AI 城市文化底座' },
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.afterEach((to) => {
  const title = (to.meta?.title as string | undefined) ?? 'aitee'
  document.title = title
})

export default router
