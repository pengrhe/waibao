import { post } from '@/utils/request'

export interface LoginPayload {
  username: string
  password: string
}

export interface LoginResp {
  token: string
  user: { id: number; username: string; name?: string; role: string }
}

export function login(p: LoginPayload) {
  return post<LoginResp>('/admin/auth/login', p)
}
