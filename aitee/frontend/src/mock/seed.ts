import type { Address, Coupon } from '@/types'
import { uid } from '@/utils/id'

const ONE_DAY = 24 * 60 * 60 * 1000
const now = Date.now()

export const seedAddresses: Address[] = [
  {
    id: uid('addr_'),
    name: '林同学',
    phone: '13800138000',
    region: '广东省 深圳市 南山区',
    detail: '科技园南路 9 号 · 1 栋 1 单元 1801',
    isDefault: true,
  },
]

export const seedCoupons: Coupon[] = [
  {
    id: uid('cp_'),
    type: 'discount',
    value: 0.78,
    threshold: 0,
    title: '新人 7.8 折',
    desc: '全场可用 · 限新人',
    expireAt: now + 3 * ONE_DAY - 60_000,
    status: 'unused',
  },
  {
    id: uid('cp_'),
    type: 'amount',
    value: 30,
    threshold: 199,
    title: '满 199 减 30',
    desc: '部分商品可用',
    expireAt: now + 7 * ONE_DAY,
    status: 'unused',
  },
  {
    id: uid('cp_'),
    type: 'amount',
    value: 10,
    threshold: 99,
    title: '满 99 减 10',
    desc: '已使用',
    expireAt: now - ONE_DAY,
    status: 'used',
  },
]
