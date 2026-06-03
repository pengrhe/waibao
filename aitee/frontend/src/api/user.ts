import { mockCall } from './request'
import { lsGet, lsSet, StorageKeys } from '@/utils/storage'
import { avatarImage } from '@/utils/placeholder'
import { REAL_API, rpost, setToken, clearToken } from './http'

export interface UserProfile {
  id: string
  phone: string
  nickname: string
  avatar: string
  loggedIn: boolean
}

export async function fetchProfile(): Promise<UserProfile> {
  return mockCall(() => {
    const cur = lsGet<UserProfile | null>(StorageKeys.user, null)
    if (cur) return cur
    const guest: UserProfile = {
      id: 'guest',
      phone: '',
      nickname: '游客',
      avatar: avatarImage('A', '#9CA3AF'),
      loggedIn: false,
    }
    return guest
  }, 80, 160)
}

export async function loginMock(): Promise<UserProfile> {
  if (REAL_API) {
    const u: any = await rpost('/user/auth/login', {
      channel: 'h5',
      phone: '13800138000',
      nickname: 'aitee 用户',
    })
    setToken(u.token)
    const out: UserProfile = {
      id: String(u.user.id),
      phone: u.user.phone,
      nickname: u.user.nickname || 'aitee 用户',
      avatar: u.user.avatar_url || avatarImage('A', '#FF4D4F'),
      loggedIn: true,
    }
    lsSet(StorageKeys.user, out)
    return out
  }
  return mockCall(() => {
    const u: UserProfile = {
      id: 'u_demo',
      phone: '13800138000',
      nickname: 'aitee 用户',
      avatar: avatarImage('A', '#FF4D4F'),
      loggedIn: true,
    }
    lsSet(StorageKeys.user, u)
    return u
  })
}

export async function logoutMock(): Promise<void> {
  clearToken()
  return mockCall(() => {
    lsSet(StorageKeys.user, null)
  }, 60, 120)
}
