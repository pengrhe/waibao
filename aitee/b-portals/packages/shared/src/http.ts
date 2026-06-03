import axios, { type AxiosInstance } from 'axios'
import { showFailToast } from 'vant'
import { useAuthStore } from './auth'

let _http: AxiosInstance | null = null

export function getHttp(): AxiosInstance {
  if (_http) return _http
  _http = axios.create({ baseURL: '/api/v1', timeout: 30000 })
  _http.interceptors.request.use((cfg) => {
    const auth = useAuthStore()
    if (auth.token) {
      cfg.headers = cfg.headers ?? {}
      cfg.headers.Authorization = `Bearer ${auth.token}`
    }
    return cfg
  })
  _http.interceptors.response.use(
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
        const auth = useAuthStore()
        auth.logout()
        showFailToast('登录已失效')
      } else {
        const msg = err.response?.data?.msg || err.response?.data?.detail || err.message || '网络错误'
        showFailToast(typeof msg === 'string' ? msg : '网络错误')
      }
      return Promise.reject(err)
    },
  )
  return _http
}
