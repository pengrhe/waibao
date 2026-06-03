import { get, post, put, del, http } from '@/utils/request'

export interface PageData<T = any> {
  items: T[]
  total: number
  page: number
  page_size: number
}

// ============ Products ============
export const ProductApi = {
  list: (params?: any) => get<PageData>('/admin/products', params),
  detail: (id: number) => get<any>(`/admin/products/${id}`),
  create: (data: any) => post<any>('/admin/products', data),
  update: (id: number, data: any) => put<any>(`/admin/products/${id}`, data),
  remove: (id: number) => del<any>(`/admin/products/${id}`),
  toggle: (id: number) => post<any>(`/admin/products/${id}/toggle`),
}

export const ProductSkuApi = {
  update: (id: number, data: any) => put(`/admin/skus/${id}`, data),
}

// ============ Patterns ============
export const PatternApi = {
  list: (params?: any) => get<PageData>('/admin/patterns', params),
  create: (data: any) => post('/admin/patterns', data),
  update: (id: number, data: any) => put(`/admin/patterns/${id}`, data),
  remove: (id: number) => del(`/admin/patterns/${id}`),
  toggle: (id: number) => post(`/admin/patterns/${id}/toggle`),
}

export const PatternCategoryApi = {
  list: (params?: any) => get<PageData>('/admin/pattern-categories', params),
  create: (data: any) => post('/admin/pattern-categories', data),
  update: (id: number, data: any) => put(`/admin/pattern-categories/${id}`, data),
  remove: (id: number) => del(`/admin/pattern-categories/${id}`),
}

export const ProductCategoryApi = {
  list: (params?: any) => get<PageData>('/admin/product-categories', params),
  create: (data: any) => post('/admin/product-categories', data),
  update: (id: number, data: any) => put(`/admin/product-categories/${id}`, data),
  remove: (id: number) => del(`/admin/product-categories/${id}`),
}

// ============ Coupons ============
export const CouponApi = {
  list: (params?: any) => get<PageData>('/admin/coupons', params),
  create: (data: any) => post('/admin/coupons', data),
  update: (id: number, data: any) => put(`/admin/coupons/${id}`, data),
  remove: (id: number) => del(`/admin/coupons/${id}`),
}

// ============ Banners / Topics ============
export const BannerApi = {
  list: (params?: any) => get<PageData>('/admin/banners', params),
  create: (data: any) => post('/admin/banners', data),
  update: (id: number, data: any) => put(`/admin/banners/${id}`, data),
  remove: (id: number) => del(`/admin/banners/${id}`),
  toggle: (id: number) => post(`/admin/banners/${id}/toggle`),
}

export const TopicApi = {
  list: (params?: any) => get<PageData>('/admin/topics', params),
  create: (data: any) => post('/admin/topics', data),
  update: (id: number, data: any) => put(`/admin/topics/${id}`, data),
  remove: (id: number) => del(`/admin/topics/${id}`),
  toggle: (id: number) => post(`/admin/topics/${id}/toggle`),
}

// ============ System Configs ============
export const SystemConfigApi = {
  list: (params?: any) => get<PageData>('/admin/system-configs', params),
  create: (data: any) => post('/admin/system-configs', data),
  update: (id: number, data: any) => put(`/admin/system-configs/${id}`, data),
  remove: (id: number) => del(`/admin/system-configs/${id}`),
}

// ============ Model Channels ============
export const ModelChannelApi = {
  list: () => get<{ items: any[]; total: number }>('/admin/model-channels'),
  create: (data: any) => post('/admin/model-channels', data),
  update: (id: number, data: any) => put(`/admin/model-channels/${id}`, data),
  remove: (id: number) => del(`/admin/model-channels/${id}`),
  activate: (id: number) => post(`/admin/model-channels/${id}/activate`),
}

// ============ Users ============
export const UserApi = {
  list: (params?: any) => get<PageData>('/admin/users', params),
  update: (id: number, data: any) => put(`/admin/users/${id}`, data),
  disable: (id: number) => post(`/admin/users/${id}/disable`),
  enable: (id: number) => post(`/admin/users/${id}/enable`),
}

// ============ Orders ============
export const OrderApi = {
  list: (params?: any) => get<PageData>('/admin/orders', params),
  detail: (id: number) => get<any>(`/admin/orders/${id}`),
  changeStatus: (id: number, data: { status: string; reason?: string }) =>
    post(`/admin/orders/${id}/status`, data),
  refund: (id: number, data: { reason: string }) => post(`/admin/orders/${id}/refund`, data),
  exportUrl: '/api/v1/admin/orders/export.csv',
}

// ============ Partners / Stores ============
export const PartnerApi = {
  list: (params?: any) => get<PageData>('/admin/partners', params),
  create: (data: any) => post('/admin/partners', data),
  update: (id: number, data: any) => put(`/admin/partners/${id}`, data),
  remove: (id: number) => del(`/admin/partners/${id}`),
  audit: (id: number, action: 'approve' | 'reject', reject_reason?: string) =>
    post(`/admin/partners/${id}/audit`, undefined, { params: { action, reject_reason } } as any),
}

export const StoreApi = {
  list: (params?: any) => get<PageData>('/admin/stores', params),
  create: (data: any) => post('/admin/stores', data),
  update: (id: number, data: any) => put(`/admin/stores/${id}`, data),
  remove: (id: number) => del(`/admin/stores/${id}`),
  audit: (id: number, action: 'approve' | 'reject', reject_reason?: string) =>
    post(`/admin/stores/${id}/audit`, undefined, { params: { action, reject_reason } } as any),
  staffs: (id: number) => get<any>(`/admin/stores/${id}/staffs`),
}

// ============ City IPs ============
export const CityIpApi = {
  list: (params?: any) => get<{ items: any[]; total: number }>('/admin/city-ips', params),
  create: (data: any) => post('/admin/city-ips', data),
  update: (id: number, data: any) => put(`/admin/city-ips/${id}`, data),
  remove: (id: number) => del(`/admin/city-ips/${id}`),
}

export const CityIpItemApi = {
  create: (data: any) => post('/admin/city-ip-items', data),
  remove: (id: number) => del(`/admin/city-ip-items/${id}`),
}

export const CulturalElementApi = {
  list: (params?: any) => get<{ items: any[]; total: number }>('/admin/cultural-elements', params),
  create: (data: any) => post('/admin/cultural-elements', data),
  update: (id: number, data: any) => put(`/admin/cultural-elements/${id}`, data),
  remove: (id: number) => del(`/admin/cultural-elements/${id}`),
}

// ============ QR codes ============
export const QrCodeApi = {
  list: (params?: any) => get<{ items: any[]; total: number }>('/admin/qrcodes', params),
  create: (data: any) => post('/admin/qrcodes', data),
  remove: (id: number) => del(`/admin/qrcodes/${id}`),
  toggle: (id: number) => post(`/admin/qrcodes/${id}/toggle`),
}
