import { defineStore } from 'pinia'
import type { PortalRole, PortalUser } from './types'

interface Persisted {
  token: string
  user: PortalUser
  role: PortalRole
}

let _role: PortalRole = 'partner'
let _storageKey = 'aitee_portal_auth'

export function configurePortalAuth(role: PortalRole) {
  _role = role
  _storageKey = `aitee_${role}_auth`
}

function load(): Persisted | null {
  try {
    const raw = localStorage.getItem(_storageKey)
    return raw ? (JSON.parse(raw) as Persisted) : null
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('portal-auth', {
  state: () => {
    const p = load()
    return {
      token: p?.token ?? '',
      user: (p?.user as PortalUser | null) ?? null,
      role: p?.role ?? _role,
    }
  },
  getters: {
    isAuthed: (s) => !!s.token,
  },
  actions: {
    setAuth(token: string, user: PortalUser) {
      this.token = token
      this.user = user
      this.role = user.role
      localStorage.setItem(_storageKey, JSON.stringify({ token, user, role: user.role }))
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem(_storageKey)
      window.location.href = '/login'
    },
  },
})
