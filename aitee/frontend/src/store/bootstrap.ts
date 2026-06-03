import { lsGet, lsSet, lsClearAll, StorageKeys } from '@/utils/storage'
import { seedAddresses, seedCoupons } from '@/mock/seed'
import type { Address, Coupon } from '@/types'

const SEED_FLAG = 'seeded:v1'

export function bootstrapSeed() {
  if (lsGet<string>(SEED_FLAG, '') === 'ok') return
  // 写入种子（仅首次）
  if (!lsGet<Address[]>(StorageKeys.addresses, []).length) {
    lsSet(StorageKeys.addresses, seedAddresses)
  }
  if (!lsGet<Coupon[]>(StorageKeys.coupons, []).length) {
    lsSet(StorageKeys.coupons, seedCoupons)
  }
  lsSet(SEED_FLAG, 'ok')
}

export function resetDemoAll() {
  lsClearAll()
  bootstrapSeed()
}
