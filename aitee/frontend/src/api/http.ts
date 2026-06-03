/**
 * 真后端 HTTP 客户端（aitee-backend on 8200）。
 *
 * 模式切换：vite 启动时设置 VITE_API_MODE
 *   - "mock" (默认): 所有 api 走 mock，离线可演示
 *   - "real": 高价值接口（登录/AI/订单/偏好等）走真后端，其他保留 mock
 *
 * 切换示例：在 .env.local 写 VITE_API_MODE=real
 */
import axios, { type AxiosRequestConfig } from 'axios'
import { showFailToast } from 'vant'

const TOKEN_KEY = 'aitee_c_token'

export function getToken(): string {
  return localStorage.getItem(TOKEN_KEY) || ''
}

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
}

export const REAL_API: boolean = String(import.meta.env.VITE_API_MODE || '').toLowerCase() === 'real'

const http = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
})

http.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers = config.headers ?? {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

http.interceptors.response.use(
  (resp) => {
    const body = resp.data
    if (body && typeof body === 'object' && 'code' in body) {
      if (body.code !== 0) {
        showFailToast(body.msg || '请求失败')
        return Promise.reject(new Error(body.msg || 'biz error'))
      }
      return body.data
    }
    return body
  },
  (err) => {
    if (err.response?.status === 401) {
      clearToken()
    }
    return Promise.reject(err)
  },
)

export function rget<T = unknown>(url: string, params?: any, config: AxiosRequestConfig = {}): Promise<T> {
  return http.get(url, { params, ...config }) as any
}
export function rpost<T = unknown>(url: string, data?: any, config: AxiosRequestConfig = {}): Promise<T> {
  return http.post(url, data, config) as any
}
export function rput<T = unknown>(url: string, data?: any): Promise<T> {
  return http.put(url, data) as any
}
export function rdel<T = unknown>(url: string, params?: any): Promise<T> {
  return http.delete(url, { params }) as any
}
