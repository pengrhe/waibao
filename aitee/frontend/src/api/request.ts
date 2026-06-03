import { randomDelay } from '@/utils/delay'

/** 通用 mock 调用：返回深拷贝后的数据，模拟网络延迟 */
export async function mockCall<T>(data: T | (() => T), min = 200, max = 500): Promise<T> {
  await randomDelay(min, max)
  const value = typeof data === 'function' ? (data as () => T)() : data
  return clone(value)
}

export function clone<T>(value: T): T {
  if (value == null || typeof value !== 'object') return value
  return JSON.parse(JSON.stringify(value))
}
