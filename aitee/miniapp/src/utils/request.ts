import { API_BASE, PLATFORM } from './env'
import { useAuthStore } from '../store/auth'

interface Options {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: Record<string, unknown> | unknown[] | string
  header?: Record<string, string>
  loading?: boolean
}

interface Resp<T> {
  code: number
  msg: string
  data: T
}

export function request<T = unknown>(url: string, options: Options = {}): Promise<T> {
  const { method = 'GET', data, header = {}, loading } = options
  const auth = useAuthStore()
  if (auth.token) header['Authorization'] = `Bearer ${auth.token}`
  header['Content-Type'] = header['Content-Type'] || 'application/json'
  header['X-Aitee-Channel'] = PLATFORM === 'mp-toutiao' ? 'dy_app' : PLATFORM === 'mp-weixin' ? 'wx_app' : 'h5'

  if (loading) uni.showLoading({ title: '加载中', mask: true })

  return new Promise((resolve, reject) => {
    uni.request({
      url: `${API_BASE}${url}`,
      method,
      data,
      header,
      success: (res) => {
        if (loading) uni.hideLoading()
        const body = res.data as Resp<T> | T
        if (body && typeof body === 'object' && 'code' in body) {
          const r = body as Resp<T>
          if (r.code === 0) return resolve(r.data)
          if (res.statusCode === 401) {
            auth.logout()
          }
          uni.showToast({ title: r.msg || '请求失败', icon: 'none' })
          return reject(new Error(r.msg || 'biz error'))
        }
        resolve(body as T)
      },
      fail: (err) => {
        if (loading) uni.hideLoading()
        uni.showToast({ title: err.errMsg || '网络错误', icon: 'none' })
        reject(err)
      },
    })
  })
}

export const http = {
  get: <T = unknown>(url: string, params?: Record<string, unknown>, opt: Options = {}) => {
    if (params) {
      const q = Object.entries(params)
        .filter(([, v]) => v !== undefined && v !== null && v !== '')
        .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`)
        .join('&')
      if (q) url += (url.includes('?') ? '&' : '?') + q
    }
    return request<T>(url, { ...opt, method: 'GET' })
  },
  post: <T = unknown>(url: string, data?: any, opt: Options = {}) =>
    request<T>(url, { ...opt, method: 'POST', data }),
}
