import { mockCall } from './request'
import { lsGet, lsSet, StorageKeys } from '@/utils/storage'
import { uid } from '@/utils/id'
import type { Address } from '@/types'

export async function listAddresses(): Promise<Address[]> {
  return mockCall(() => lsGet<Address[]>(StorageKeys.addresses, []))
}

export async function saveAddress(addr: Omit<Address, 'id'> & { id?: string }): Promise<Address[]> {
  return mockCall(() => {
    const list = lsGet<Address[]>(StorageKeys.addresses, [])
    if (addr.isDefault) list.forEach((a) => (a.isDefault = false))
    if (addr.id) {
      const i = list.findIndex((a) => a.id === addr.id)
      if (i >= 0) list[i] = { ...list[i], ...addr } as Address
    } else {
      const next: Address = { ...(addr as Address), id: uid('addr_') }
      list.unshift(next)
      if (list.length === 1) list[0].isDefault = true
    }
    lsSet(StorageKeys.addresses, list)
    return list
  })
}

export async function deleteAddress(id: string): Promise<Address[]> {
  return mockCall(() => {
    const list = lsGet<Address[]>(StorageKeys.addresses, []).filter((a) => a.id !== id)
    if (list.length && !list.some((a) => a.isDefault)) list[0].isDefault = true
    lsSet(StorageKeys.addresses, list)
    return list
  })
}

export async function defaultAddress(): Promise<Address | undefined> {
  return mockCall(() => {
    const list = lsGet<Address[]>(StorageKeys.addresses, [])
    return list.find((a) => a.isDefault) || list[0]
  }, 80, 160)
}
