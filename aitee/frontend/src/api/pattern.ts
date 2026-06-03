import { patternCategories, patterns } from '@/mock/patterns'
import { mockCall } from './request'
import { lsGet, lsSet, StorageKeys } from '@/utils/storage'
import type { Pattern, PatternCategory } from '@/types'

export async function fetchPatternCategories(): Promise<PatternCategory[]> {
  return mockCall(() => patternCategories)
}

export async function fetchPatterns(categoryId?: number): Promise<Pattern[]> {
  return mockCall(() => {
    if (!categoryId) return patterns
    return patterns.filter((p) => p.categoryId === categoryId)
  })
}

export async function fetchPatternById(id: number): Promise<Pattern | undefined> {
  return mockCall(() => patterns.find((p) => p.id === id))
}

export async function fetchFavoritePatterns(): Promise<Pattern[]> {
  return mockCall(() => {
    const favIds = lsGet<number[]>(StorageKeys.patternFavs, [])
    return patterns.filter((p) => favIds.includes(p.id))
  })
}

export async function togglePatternFav(id: number): Promise<boolean> {
  return mockCall(() => {
    const favIds = lsGet<number[]>(StorageKeys.patternFavs, [])
    const idx = favIds.indexOf(id)
    if (idx >= 0) {
      favIds.splice(idx, 1)
      lsSet(StorageKeys.patternFavs, favIds)
      return false
    }
    favIds.push(id)
    lsSet(StorageKeys.patternFavs, favIds)
    return true
  }, 100, 200)
}
