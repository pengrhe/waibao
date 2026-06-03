import { defineStore } from 'pinia'

const STORAGE_KEY = 'aitee_miniapp_auth'

export interface MiniUser {
  id?: number
  nickname?: string
  avatar_url?: string
  phone?: string
}

interface PersistState {
  token: string
  user: MiniUser
}

function load(): PersistState | null {
  try {
    const raw = uni.getStorageSync(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as PersistState) : null
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('miniapp-auth', {
  state: () => {
    const p = load()
    return {
      token: p?.token ?? '',
      user: p?.user ?? {} as MiniUser,
    }
  },
  getters: {
    isAuthed: (s) => !!s.token,
  },
  actions: {
    setAuth(token: string, user: MiniUser) {
      this.token = token
      this.user = user
      uni.setStorageSync(STORAGE_KEY, JSON.stringify({ token, user }))
    },
    logout() {
      this.token = ''
      this.user = {}
      uni.removeStorageSync(STORAGE_KEY)
      uni.reLaunch({ url: '/pages/index/index' })
    },
  },
})
