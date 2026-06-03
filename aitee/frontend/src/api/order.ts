import { mockCall } from './request'
import { lsGet, lsSet, StorageKeys } from '@/utils/storage'
import { orderNo, uid } from '@/utils/id'
import type { Address, CartItem, Coupon, Order, OrderStatus } from '@/types'

export async function listOrders(status?: OrderStatus | 'all'): Promise<Order[]> {
  return mockCall(() => {
    const list = lsGet<Order[]>(StorageKeys.orders, [])
    if (!status || status === 'all') return list
    return list.filter((o) => o.status === status)
  })
}

export async function getOrder(id: string): Promise<Order | undefined> {
  return mockCall(() => lsGet<Order[]>(StorageKeys.orders, []).find((o) => o.id === id))
}

export async function createOrder(opts: {
  items: CartItem[]
  address?: Address
  coupon?: Coupon
}): Promise<Order> {
  return mockCall(() => {
    const total = opts.items.reduce((s, i) => s + i.price * i.qty, 0)
    let pay = total
    if (opts.coupon && opts.coupon.status === 'unused' && total >= opts.coupon.threshold) {
      if (opts.coupon.type === 'amount') pay = Math.max(0, total - opts.coupon.value)
      else if (opts.coupon.type === 'discount') pay = +(total * opts.coupon.value).toFixed(2)
    }
    const order: Order = {
      id: uid('o_'),
      no: orderNo(),
      items: opts.items.map((i) => ({
        designId: i.designId,
        productId: i.productId,
        productName: i.productName,
        color: i.color,
        size: i.size,
        qty: i.qty,
        price: i.price,
        previewUrl: i.previewUrl,
      })),
      total,
      payAmount: pay,
      couponId: opts.coupon?.id,
      status: 'pending_pay',
      address: opts.address,
      createdAt: Date.now(),
    }
    const list = lsGet<Order[]>(StorageKeys.orders, [])
    list.unshift(order)
    lsSet(StorageKeys.orders, list)
    return order
  })
}

/** 模拟支付：立刻把订单标记为已付款，并在 3 秒后自动跳转到 pending_print */
export async function payOrder(id: string): Promise<Order | undefined> {
  return mockCall(() => {
    const list = lsGet<Order[]>(StorageKeys.orders, [])
    const o = list.find((x) => x.id === id)
    if (!o) return undefined
    o.status = 'pending_print'
    o.paidAt = Date.now()
    lsSet(StorageKeys.orders, list)
    // 进一步推进
    setTimeout(() => {
      const cur = lsGet<Order[]>(StorageKeys.orders, [])
      const cu = cur.find((x) => x.id === id)
      if (cu && cu.status === 'pending_print') {
        cu.status = 'printing'
        lsSet(StorageKeys.orders, cur)
      }
    }, 8000)
    return o
  }, 800, 1200)
}

export async function cancelOrder(id: string): Promise<Order | undefined> {
  return mockCall(() => {
    const list = lsGet<Order[]>(StorageKeys.orders, [])
    const o = list.find((x) => x.id === id)
    if (!o) return undefined
    if (o.status === 'pending_pay' || o.status === 'pending_print') {
      o.status = 'cancelled'
      lsSet(StorageKeys.orders, list)
    }
    return o
  })
}

export async function pickupOrder(id: string): Promise<Order | undefined> {
  return mockCall(() => {
    const list = lsGet<Order[]>(StorageKeys.orders, [])
    const o = list.find((x) => x.id === id)
    if (!o) return undefined
    if (o.status === 'pending_pickup' || o.status === 'printing') {
      o.status = 'done'
      lsSet(StorageKeys.orders, list)
    }
    return o
  })
}
