export type ProductType = 'tshirt' | 'tote' | 'hoodie' | 'parent-child' | 'pet'

export interface Product {
  id: number
  name: string
  type: ProductType
  basePrice: number
  description: string
  tags: string[]
  colors: string[]
  sizes: string[]
  isHot: boolean
  sort: number
}

export interface PatternCategory {
  id: number
  name: string
  sort: number
}

export interface Pattern {
  id: number
  categoryId: number
  title: string
  imageUrl: string
  tags: string[]
  isHot: boolean
  sort: number
}

export type LayerSource = 'pattern' | 'text' | 'upload' | 'ai'
export type LayerSide = 'front' | 'back'

export interface DesignLayer {
  id: string
  source: LayerSource
  data: string
  text?: string
  textColor?: string
  fontSize?: number
  x: number
  y: number
  width: number
  height: number
  rotation: number
  opacity: number
  side: LayerSide
}

export type DesignStatus = 'draft' | 'saved'

export interface Design {
  id: string
  productId: number
  color: string
  layers: DesignLayer[]
  previewUrl?: string
  status: DesignStatus
  createdAt: number
  updatedAt: number
}

export interface CartItem {
  id: string
  designId: string
  productId: number
  productName: string
  color: string
  size: string
  qty: number
  price: number
  previewUrl: string
  selected: boolean
}

export interface Address {
  id: string
  name: string
  phone: string
  region: string
  detail: string
  isDefault: boolean
}

export type CouponType = 'discount' | 'amount'
export type CouponStatus = 'unused' | 'used' | 'expired'

export interface Coupon {
  id: string
  type: CouponType
  value: number
  threshold: number
  title: string
  desc: string
  expireAt: number
  status: CouponStatus
}

export interface OrderItem {
  designId: string
  productId: number
  productName: string
  color: string
  size: string
  qty: number
  price: number
  previewUrl: string
}

export type OrderStatus =
  | 'pending_pay'
  | 'pending_print'
  | 'printing'
  | 'pending_pickup'
  | 'done'
  | 'cancelled'

export interface Order {
  id: string
  no: string
  items: OrderItem[]
  total: number
  payAmount: number
  couponId?: string
  status: OrderStatus
  address?: Address
  paidAt?: number
  createdAt: number
}

export interface Banner {
  id: number
  title: string
  subtitle?: string
  cta?: string
  imageUrl: string
  link?: string
  location: 'home_top' | 'home_recommend' | 'mine_invite'
}

export interface RecommendItem {
  id: number
  title: string
  badge?: string
  imageUrl: string
  link?: string
}

export interface TopicSection {
  id: string
  title: string
  subtitle?: string
  items: TopicItem[]
}

export interface TopicItem {
  id: number
  title?: string
  imageUrl: string
  link?: string
}

export interface AiSample {
  id: number
  prompt: string
  style: string
  imageUrl: string
}

export type CityIpCategory = 'landmark' | 'folk' | 'symbol'

export interface CityIpItem {
  id: string
  category: CityIpCategory
  title: string
  imageUrl: string
  tags: string[]
}

export interface CityIpStyleWeight {
  style: string
  ratio: number
}

export interface CityIp {
  city: string
  totalCount: number
  /** 该城市文化元素，可被用户增删后影响重新生成 */
  elements: string[]
  /** 三类图库 */
  items: CityIpItem[]
  /** 基于本地用户历史订单偏好的风格权重 */
  styleWeights: CityIpStyleWeight[]
  generatedAt: number
}
