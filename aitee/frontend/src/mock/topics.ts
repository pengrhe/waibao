import type { TopicSection } from '@/types'
import { topicCard } from '@/utils/placeholder'

export const topics: TopicSection[] = [
  {
    id: 'switch',
    title: '"衣"键切换上下班状态',
    items: [
      { id: 1, title: '搬砖打工人', imageUrl: topicCard({ title: '上班人', bg: '#1F2937', fg: '#FACC15' }) },
      { id: 2, title: '下班吃喝玩乐', imageUrl: topicCard({ title: '下班', bg: '#FEE2E2', fg: '#DC2626' }) },
    ],
  },
  {
    id: 'kid',
    title: '给小朋友的画加个框',
    items: [
      { id: 1, title: '小恐龙', imageUrl: topicCard({ title: '咕咕鸡', bg: '#FEF3C7', fg: '#92400E' }) },
      { id: 2, title: '小汽车', imageUrl: topicCard({ title: '小汽车', bg: '#DCFCE7', fg: '#15803D' }) },
      { id: 3, title: '彩虹', imageUrl: topicCard({ title: '彩虹', bg: '#FCE7F3', fg: '#BE185D' }) },
    ],
  },
  {
    id: 'lucky',
    title: '求人还是求己？求佛吧',
    items: [
      { id: 1, title: '好运来', imageUrl: topicCard({ title: '好运来', bg: '#1F2937', fg: '#FACC15' }) },
      { id: 2, title: '情绪稳定', imageUrl: topicCard({ title: '稳定', bg: '#FFFFFF', fg: '#1F2937' }) },
      { id: 3, title: '财源滚滚', imageUrl: topicCard({ title: '财气', bg: '#FEE2E2', fg: '#DC2626' }) },
    ],
  },
  {
    id: 'cool',
    title: '潮男潮女都在用',
    items: [
      { id: 1, title: '复古印花', imageUrl: topicCard({ title: 'NEVER STOP', bg: '#1F2937', fg: '#FACC15' }) },
      { id: 2, title: '街头风格', imageUrl: topicCard({ title: 'STREET', bg: '#F3F4F6', fg: '#1F2937' }) },
      { id: 3, title: '极简风', imageUrl: topicCard({ title: 'MINIMAL', bg: '#FFFFFF', fg: '#1F2937' }) },
    ],
  },
  {
    id: 'tote',
    title: '热门帆布包印花',
    items: [
      { id: 1, title: '蓝色款', imageUrl: topicCard({ title: 'LOOK AT ME', bg: '#3B82F6', fg: '#FFFFFF' }) },
      { id: 2, title: '粉色款', imageUrl: topicCard({ title: 'LOOK AT ME', bg: '#FBCFE8', fg: '#9D174D' }) },
      { id: 3, title: '黄色款', imageUrl: topicCard({ title: 'LOOK AT ME', bg: '#FDE68A', fg: '#92400E' }) },
    ],
  },
]
