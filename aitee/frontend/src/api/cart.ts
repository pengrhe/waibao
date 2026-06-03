import { mockCall } from './request'
import { lsGet, lsSet, StorageKeys } from '@/utils/storage'
import type { CartItem } from '@/types'
import { reportPref } from './prefs'

export async function listCart(): Promise<CartItem[]> {
  return mockCall(() => lsGet<CartItem[]>(StorageKeys.cart, []), 100, 200)
}

export async function addToCart(item: CartItem): Promise<CartItem[]> {
  // 偏好埋点：颜色 / 尺码 / 商品 ID
  reportPref('color', item.color)
  reportPref('size', item.size)
  reportPref('product_id', item.productId)
  return mockCall(() => {
    const list = lsGet<CartItem[]>(StorageKeys.cart, [])
    const exist = list.find(
      (i) =>
        i.designId === item.designId &&
        i.color === item.color &&
        i.size === item.size,
    )
    if (exist) {
      exist.qty += item.qty
    } else {
      list.unshift(item)
    }
    lsSet(StorageKeys.cart, list)
    return list
  })
}

export async function updateCartItem(id: string, patch: Partial<CartItem>): Promise<CartItem[]> {
  return mockCall(() => {
    const list = lsGet<CartItem[]>(StorageKeys.cart, [])
    const it = list.find((i) => i.id === id)
    if (it) Object.assign(it, patch)
    lsSet(StorageKeys.cart, list)
    return list
  }, 60, 120)
}

export async function removeCartItem(ids: string[]): Promise<CartItem[]> {
  return mockCall(() => {
    const list = lsGet<CartItem[]>(StorageKeys.cart, []).filter((i) => !ids.includes(i.id))
    lsSet(StorageKeys.cart, list)
    return list
  })
}

export async function clearCart(): Promise<void> {
  return mockCall(() => lsSet(StorageKeys.cart, []), 60, 120)
}
