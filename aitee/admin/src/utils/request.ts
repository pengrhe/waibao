import axios, { AxiosError, type AxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/store/auth'

export const http = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
})

http.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers = config.headers ?? {}
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

http.interceptors.response.use(
  (resp) => {
    const body = resp.data
    if (body && typeof body === 'object' && 'code' in body) {
      if (body.code !== 0) {
        ElMessage.error(body.msg || '请求失败')
        return Promise.reject(new Error(body.msg || 'biz error'))
      }
      return body.data
    }
    return body
  },
  (err: AxiosError<any>) => {
    if (err.response?.status === 401) {
      const auth = useAuthStore()
      auth.logout()
      ElMessage.error('登录已失效，请重新登录')
    } else {
      const msg =
        err.response?.data?.msg ||
        err.response?.data?.detail ||
        err.message ||
        '网络错误'
      ElMessage.error(typeof msg === 'string' ? msg : '网络错误')
    }
    return Promise.reject(err)
  },
)

export function get<T = unknown>(url: string, params?: any, config: AxiosRequestConfig = {}): Promise<T> {
  return http.get(url, { params, ...config })
}

export function post<T = unknown>(url: string, data?: any, config: AxiosRequestConfig = {}): Promise<T> {
  return http.post(url, data, config)
}

export function put<T = unknown>(url: string, data?: any): Promise<T> {
  return http.put(url, data)
}

export function del<T = unknown>(url: string, params?: any): Promise<T> {
  return http.delete(url, { params })
}
