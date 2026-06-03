import type { RouteRecordRaw } from 'vue-router'
import type { PortalBrand, PortalMenuItem, PortalRole } from '@aitee/shared'

import { partnerModule } from './partner'
import { storeModule } from './store'
import { staffModule } from './staff'

export interface PortalModule {
  role: PortalRole
  label: string                  // 登录页 tab 显示
  brand: PortalBrand
  menus: PortalMenuItem[]
  routes: RouteRecordRaw[]       // 子路由（不含父 Shell）
  defaultUser?: { username: string; password: string }  // demo 默认账号
  loginHint?: string
}

export const modules: Record<PortalRole, PortalModule> = {
  partner: partnerModule,
  store: storeModule,
  staff: staffModule,
}

export const moduleList: PortalModule[] = [partnerModule, storeModule, staffModule]
