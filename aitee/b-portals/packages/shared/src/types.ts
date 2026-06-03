export type PortalRole = 'partner' | 'store' | 'staff'

export interface PortalBrand {
  name: string
  sub: string
  primary: string
  gradient: string
}

export interface PortalUser {
  id: number
  username: string
  name?: string
  role: PortalRole
  extra?: Record<string, unknown>
}

export interface PortalLoginResp {
  token: string
  user: PortalUser
}

export interface PortalMenuItem {
  path: string
  title: string
  icon?: string
}
