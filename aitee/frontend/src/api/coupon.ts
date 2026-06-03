import { mockCall } from './request'
import { lsGet, lsSet, StorageKeys } from '@/utils/storage'
import type { Coupon, CouponStatus } from '@/types'

function refreshStatus(c: Coupon): Coupon {
  if (c.status === 'used') return c
  if (c.expireAt < Date.now()) return { ...c, status: 'expired' }
  return c
}

export async function listCoupons(status?: CouponStatus): Promise<Coupon[]> {
  return mockCall(() => {
    const list = lsGet<Coupon[]>(StorageKeys.coupons, []).map(refreshStatus)
    lsSet(StorageKeys.coupons, list)
    if (!status) return list
    return list.filter((c) => c.status === status)
  })
}

export async function consumeCoupon(id: string): Promise<void> {
  return mockCall(() => {
    const list = lsGet<Coupon[]>(StorageKeys.coupons, [])
    const c = list.find((x) => x.id === id)
    if (c) c.status = 'used'
    lsSet(StorageKeys.coupons, list)
  }, 80, 160)
}

export async function bestCouponForAmount(amount: number): Promise<Coupon | undefined> {
  return mockCall(() => {
    const list = lsGet<Coupon[]>(StorageKeys.coupons, [])
      .map(refreshStatus)
      .filter((c) => c.status === 'unused' && amount >= c.threshold)
    if (!list.length) return undefined
    let best = list[0]
    let bestSave = 0
    for (const c of list) {
      const save = c.type === 'amount' ? c.value : amount * (1 - c.value)
      if (save > bestSave) {
        bestSave = save
        best = c
      }
    }
    return best
  }, 80, 160)
}
