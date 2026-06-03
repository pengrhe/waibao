import { mockCall } from './request'
import { lsGet, lsSet, StorageKeys } from '@/utils/storage'
import type { Design } from '@/types'

export async function listDesigns(): Promise<Design[]> {
  return mockCall(() => lsGet<Design[]>(StorageKeys.designs, []))
}

export async function saveDesign(design: Design): Promise<Design> {
  return mockCall(() => {
    const list = lsGet<Design[]>(StorageKeys.designs, [])
    const idx = list.findIndex((d) => d.id === design.id)
    const now = Date.now()
    const next: Design = { ...design, status: 'saved', updatedAt: now }
    if (idx >= 0) {
      list[idx] = next
    } else {
      list.unshift(next)
    }
    lsSet(StorageKeys.designs, list)
    return next
  })
}

export async function deleteDesign(id: string): Promise<void> {
  return mockCall(() => {
    const list = lsGet<Design[]>(StorageKeys.designs, []).filter((d) => d.id !== id)
    lsSet(StorageKeys.designs, list)
  })
}

export async function getDesign(id: string): Promise<Design | undefined> {
  return mockCall(() => lsGet<Design[]>(StorageKeys.designs, []).find((d) => d.id === id))
}
