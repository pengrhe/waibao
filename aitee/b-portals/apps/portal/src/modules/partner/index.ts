import { PagePlaceholder } from '@aitee/shared'
import type { PortalModule } from '../index'

export const partnerModule: PortalModule = {
  role: 'partner',
  label: '联营伙伴',
  brand: {
    name: '联营伙伴',
    sub: '推广 · 分润 · 提现',
    primary: '#5b6cff',
    gradient:
      'radial-gradient(80% 70% at 20% 0%, rgba(91,108,255,0.22) 0%, transparent 60%), linear-gradient(135deg, #eef2ff 0%, #f5ebff 100%)',
  },
  menus: [
    { path: '/partner/dashboard', title: '看板', icon: 'chart-trending-o' },
    { path: '/partner/qr', title: '二维码', icon: 'qr' },
    { path: '/partner/profit', title: '分润', icon: 'gold-coin-o' },
    { path: '/partner/withdraw', title: '提现', icon: 'balance-pay' },
  ],
  routes: [
    { path: 'dashboard', name: 'partner-dashboard', component: () => import('./Dashboard.vue'), meta: { title: '看板' } },
    { path: 'qr', name: 'partner-qr', component: PagePlaceholder, meta: { title: '我的二维码' } },
    { path: 'profit', name: 'partner-profit', component: PagePlaceholder, meta: { title: '分润明细' } },
    { path: 'withdraw', name: 'partner-withdraw', component: PagePlaceholder, meta: { title: '提现' } },
  ],
  defaultUser: { username: 'p_zhang', password: 'partner123' },
  loginHint: 'p_zhang / p_li / p_wang，密码 partner123',
}
