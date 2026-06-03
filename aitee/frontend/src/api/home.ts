import { banners } from '@/mock/banners'
import { recommendItems } from '@/mock/recommend'
import { topics } from '@/mock/topics'
import { mockCall } from './request'

export async function fetchHomeBanners(location: 'home_top' | 'home_recommend' | 'mine_invite' = 'home_top') {
  return mockCall(() => banners.filter((b) => b.location === location))
}

export async function fetchRecommend() {
  return mockCall(() => recommendItems)
}

export async function fetchTopics() {
  return mockCall(() => topics)
}
