import { PagePlaceholder } from '@aitee/shared'
import type { PortalModule } from '../index'

export const storeModule: PortalModule = {
  role: 'store',
  label: '加盟店',
  brand: {
    name: '加盟店',
    sub: '门店 · 设备 · 结算',
    primary: '#16a34a',
    gradient:
      'radial-gradient(80% 70% at 20% 0%, rgba(22,163,74,0.18) 0%, transparent 60%), linear-gradient(135deg, #f0fdf4 0%, #ecfeff 100%)',
  },
  menus: [
    { path: '/store/dashboard', title: '门店', icon: 'shop-o' },
    { path: '/store/devices', title: '设备', icon: 'desktop-o' },
    { path: '/store/settle', title: '结算', icon: 'balance-list-o' },
    { path: '/store/promo', title: '优惠', icon: 'gift-o' },
  ],
  routes: [
    { path: 'dashboard', name: 'store-dashboard', component: () => import('./Dashboard.vue'), meta: { title: '门店' } },
    { path: 'devices', name: 'store-devices', component: PagePlaceholder, meta: { title: '设备' } },
    { path: 'settle', name: 'store-settle', component: PagePlaceholder, meta: { title: '结算' } },
    { path: 'promo', name: 'store-promo', component: PagePlaceholder, meta: { title: '优惠' } },
  ],
  defaultUser: { username: 's_sz01', password: 'store123' },
  loginHint: 's_sz01（统一结算）/ s_cs01（自主结算），密码 store123',
}
