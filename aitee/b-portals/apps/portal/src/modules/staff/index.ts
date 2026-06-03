import { PagePlaceholder } from '@aitee/shared'
import type { PortalModule } from '../index'

export const staffModule: PortalModule = {
  role: 'staff',
  label: '店员',
  brand: {
    name: '店员端',
    sub: '订单 · 核销 · 设备',
    primary: '#ff7a2a',
    gradient:
      'radial-gradient(80% 70% at 20% 0%, rgba(255,122,42,0.22) 0%, transparent 60%), linear-gradient(135deg, #fff7ed 0%, #fff1f2 100%)',
  },
  menus: [
    { path: '/staff/dashboard', title: '订单', icon: 'orders-o' },
    { path: '/staff/scan', title: '核销', icon: 'scan' },
    { path: '/staff/manual', title: '录单', icon: 'edit' },
    { path: '/staff/devices', title: '设备', icon: 'tv-o' },
  ],
  routes: [
    { path: 'dashboard', name: 'staff-dashboard', component: () => import('./Dashboard.vue'), meta: { title: '订单' } },
    { path: 'scan', name: 'staff-scan', component: PagePlaceholder, meta: { title: '核销' } },
    { path: 'manual', name: 'staff-manual', component: PagePlaceholder, meta: { title: '录单' } },
    { path: 'devices', name: 'staff-devices', component: PagePlaceholder, meta: { title: '设备' } },
  ],
  defaultUser: { username: 'st_sz01_a', password: 'staff123' },
  loginHint: 'st_sz01_a / st_sz01_b / st_cs01_a，密码 staff123',
}
