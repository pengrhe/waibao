const NS = 'aitee:'

export function lsGet<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(NS + key)
    if (raw == null) return fallback
    return JSON.parse(raw) as T
  } catch {
    return fallback
  }
}

export function lsSet<T>(key: string, value: T): void {
  try {
    localStorage.setItem(NS + key, JSON.stringify(value))
  } catch {
    /* ignore */
  }
}

export function lsRemove(key: string): void {
  try {
    localStorage.removeItem(NS + key)
  } catch {
    /* ignore */
  }
}

export function lsClearAll(): void {
  try {
    const keys: string[] = []
    for (let i = 0; i < localStorage.length; i++) {
      const k = localStorage.key(i)
      if (k && k.startsWith(NS)) keys.push(k)
    }
    keys.forEach((k) => localStorage.removeItem(k))
  } catch {
    /* ignore */
  }
}

export const StorageKeys = {
  user: 'user',
  cart: 'cart',
  designs: 'designs',
  orders: 'orders',
  addresses: 'addresses',
  coupons: 'coupons',
  patternFavs: 'patternFavs',
} as const
