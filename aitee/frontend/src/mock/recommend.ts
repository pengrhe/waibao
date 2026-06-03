import type { RecommendItem } from '@/types'
import { recommendCard } from '@/utils/placeholder'

export const recommendItems: RecommendItem[] = [
  { id: 1, title: '活动衫', badge: '热卖', imageUrl: recommendCard({ title: '活动衫', bg: '#fafafa', tee: '#1F2937' }) },
  { id: 2, title: '文化衫', imageUrl: recommendCard({ title: '文化衫', bg: '#FFF7ED', tee: '#9A3412' }) },
  { id: 3, title: '班服', imageUrl: recommendCard({ title: '班服', bg: '#DBEAFE', tee: '#1D4ED8' }) },
  { id: 4, title: '亲子装', imageUrl: recommendCard({ title: '亲子装', bg: '#FCE7F3', tee: '#BE185D' }) },
  { id: 5, title: '宠物装', imageUrl: recommendCard({ title: '宠物装', bg: '#FEF3C7', tee: '#92400E' }) },
  { id: 6, title: '潮 T', imageUrl: recommendCard({ title: '潮 T', bg: '#F3E8FF', tee: '#7E22CE' }) },
]
