/**
 * miniapp 业务 API 集合（对齐 aitee-backend /api/v1 接口）。
 *
 * 所有方法返回 backend 解包后的 data；失败由 utils/request 统一 toast。
 */
import { http } from '../utils/request'

// ============ Auth ============
export const Auth = {
  login: (data: { channel?: string; phone?: string; nickname?: string; code?: string }) =>
    http.post<{ token: string; user: any }>('/user/auth/login', {
      channel: 'wx_app',
      ...data,
    }),
  me: () => http.get<any>('/user/auth/me'),
}

// ============ User ============
export const User = {
  profile: () => http.get<any>('/user/profile'),
  updateProfile: (data: any) => http.post('/user/profile', data, { method: 'PUT' as any }),
  reportPref: (pref_type: string, value: string | number) =>
    http.post('/user/prefs', { pref_type, value: String(value) }),
  prefs: () => http.get<{ defaults: Record<string, string>; history: any[] }>('/user/prefs'),
}

// ============ Address ============
export const Address = {
  list: () => http.get<any[]>('/addresses'),
  create: (data: any) => http.post<any>('/addresses', data),
  update: (id: number, data: any) => httpPut(`/addresses/${id}`, data),
  remove: (id: number) => httpDelete(`/addresses/${id}`),
  default: () => http.get<any>('/addresses/default'),
}

// ============ Coupons ============
export const Coupon = {
  templates: () => http.get<any[]>('/coupons/templates'),
  mine: (status?: string) => http.get<any[]>('/coupons/mine', status ? { status_filter: status } : undefined),
  claim: (coupon_id: number) => http.post<any>(`/coupons/claim/${coupon_id}`),
  best: (amount: number) => http.get<any>(`/coupons/best/${amount}`),
}

// ============ Product ============
export const Product = {
  list: (category_id?: number) => http.get<any[]>('/products', category_id ? { category_id } : undefined),
  detail: (id: number) => http.get<any>(`/products/${id}`),
  categories: () => http.get<any[]>('/products/categories'),
  sku: (id: number) => http.get<any>(`/products/sku/${id}`),
}

// ============ Pattern ============
export const Pattern = {
  list: (category_id?: number) => http.get<any[]>('/patterns', category_id ? { category_id } : undefined),
  detail: (id: number) => http.get<any>(`/patterns/${id}`),
  categories: () => http.get<any[]>('/patterns/categories'),
}

// ============ Design ============
export const Design = {
  list: () => http.get<any[]>('/designs'),
  create: (data: any) => http.post<any>('/designs', data),
  update: (id: number, data: any) => httpPut(`/designs/${id}`, data),
  remove: (id: number) => httpDelete(`/designs/${id}`),
  detail: (id: number) => http.get<any>(`/designs/${id}`),
}

// ============ Cart ============
export const Cart = {
  list: () => http.get<any[]>('/cart'),
  add: (data: { sku_id: number; qty?: number; design_id?: number; snapshot?: any }) =>
    http.post<any>('/cart', data),
  update: (id: number, data: { qty?: number; selected?: boolean }) => httpPut(`/cart/${id}`, data),
  remove: (ids: number[]) => http.post<any[]>('/cart/remove', { ids }),
  clear: () => httpDelete('/cart/clear'),
}

// ============ Order ============
export const Order = {
  list: (status?: string) => http.get<any[]>('/orders', status ? { status_filter: status } : undefined),
  detail: (id: number) => http.get<any>(`/orders/${id}`),
  create: (data: any) => http.post<any>('/orders', data),
  pay: (id: number, pay_method: string = 'mock') =>
    http.post<any>(`/orders/${id}/pay`, { pay_method }),
  cancel: (id: number, reason?: string) =>
    http.post<any>(`/orders/${id}/cancel`, { reason: reason || '用户取消' }),
  pickup: (id: number) => http.post<any>(`/orders/${id}/pickup`),
}

// ============ Home ============
export const Home = {
  banners: (position: string = 'home_top') =>
    http.get<any[]>('/home/banners', { position }),
  topics: () => http.get<any[]>('/home/topics'),
}

// ============ City IP ============
export const CityIp = {
  popular: () => http.get<string[]>('/city-ip/popular'),
  hints: () => http.get<Record<string, string>>('/city-ip/hints'),
  detail: (city: string) => http.get<any>(`/city-ip/${encodeURIComponent(city)}`),
  regen: (city: string, elements: string[]) =>
    http.post<any>(`/city-ip/${encodeURIComponent(city)}/regenerate`, { elements }),
}

// ============ AI ============
export const AI = {
  styles: () => http.get<string[]>('/ai/styles'),
  generate: (opts: { type?: string; prompt?: string; style?: string; source_image_url?: string; n?: number }) =>
    http.post<{ samples: any[]; status: string; fallback: boolean }>('/ai/generate', { type: 't2i', n: 4, ...opts }),
}

// ============ Messages ============
export const Messages = {
  list: () => http.get<any[]>('/messages'),
  unreadCount: () => http.get<{ count: number }>('/messages/unread-count'),
  read: (id: number) => http.post(`/messages/${id}/read`),
  readAll: () => http.post('/messages/read-all'),
}

// ============ QR scan ============
export const QR = {
  scan: (code: string) => http.get<any>(`/qr/${code}`),
}

// ============ Payments ============
export const Payments = {
  mockNotify: (order_no: string, success = true, pay_method = 'mock') =>
    http.post<any>('/payments/mock/notify', { order_no, success, pay_method }),
}

// ============ helpers ============
// http.ts 没暴露 put/del，这里用 request 直发
import { request } from '../utils/request'

function httpPut<T = any>(url: string, data?: any) {
  return request<T>(url, { method: 'PUT', data })
}
function httpDelete<T = any>(url: string) {
  return request<T>(url, { method: 'DELETE' })
}
