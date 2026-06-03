import { defineStore } from 'pinia'

const STORAGE_KEY = 'aitee_admin_auth'

interface PersistState {
  token: string
  user: { id?: number; username: string; name?: string; role?: string }
}

function load(): PersistState | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as PersistState) : null
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('auth', {
  state: () => {
    const persisted = load()
    return {
      token: persisted?.token ?? '',
      user: persisted?.user ?? { username: '' },
    }
  },
  getters: {
    isAuthed: (s) => !!s.token,
  },
  actions: {
    setAuth(token: string, user: PersistState['user']) {
      this.token = token
      this.user = user
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ token, user }))
    },
    logout() {
      this.token = ''
      this.user = { username: '' }
      localStorage.removeItem(STORAGE_KEY)
      window.location.href = '/login'
    },
  },
})
