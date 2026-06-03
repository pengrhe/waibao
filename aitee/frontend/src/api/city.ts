import type { CityIp, CityIpItem } from '@/types'
import { cityIpData, cityHints, popularCities } from '@/mock/city-ip'
import { mockCall } from './request'

export async function fetchPopularCities(): Promise<string[]> {
  return mockCall([...popularCities], 80, 180)
}

export async function fetchCityHints(): Promise<Record<string, string>> {
  return mockCall({ ...cityHints }, 60, 140)
}

/** 按城市名取该城市的 AI 文化图库（demo：直接 return 静态 mock） */
export async function fetchCityIp(city: string): Promise<CityIp> {
  const data = cityIpData[city]
  if (data) return mockCall(data, 400, 900)
  // 城市不在预置清单 → 返回深圳数据但替换 city 名，假装 AI 生成出来
  const fallback: CityIp = {
    ...cityIpData['深圳'],
    city,
    totalCount: 480 + Math.floor(Math.random() * 80),
    elements: ['代表景点', '本地美食', '方言文化', '历史符号'],
    generatedAt: Date.now(),
  }
  return mockCall(fallback, 800, 1500)
}

/** "重新生成" demo：shuffle 当前城市的 items 顺序 + 更新 generatedAt */
export async function regenCityIp(
  city: string,
  elements: string[],
): Promise<CityIp> {
  const base = cityIpData[city] ?? cityIpData['深圳']
  const items = shuffle([...base.items]) as CityIpItem[]
  const data: CityIp = {
    ...base,
    city,
    elements: [...elements],
    items,
    totalCount: 480 + Math.floor(Math.random() * 100),
    generatedAt: Date.now(),
  }
  return mockCall(data, 1200, 2200)
}

function shuffle<T>(arr: T[]): T[] {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[a[i], a[j]] = [a[j], a[i]]
  }
  return a
}
