import type { Pattern, PatternCategory } from '@/types'
import { patternImage } from '@/utils/placeholder'

export const patternCategories: PatternCategory[] = [
  { id: 1, name: '最热', sort: 1 },
  { id: 2, name: '新品', sort: 2 },
  { id: 3, name: '文化衫', sort: 3 },
  { id: 4, name: 'IP 系列', sort: 4 },
  { id: 5, name: '宠物', sort: 5 },
  { id: 6, name: '用户案例', sort: 6 },
]

interface Seed {
  category: number
  title: string
  text: string
  bg: string
  fg: string
  shape?: 'square' | 'circle' | 'tag'
  tags: string[]
  hot?: boolean
  realImg?: string
}

const seeds: Seed[] = [
  // 最热
  { category: 1, title: '心电图', text: 'BEAT', bg: '#FEE2E2', fg: '#FF4D4F', tags: ['潮流', '简约'], hot: true, realImg: '/assets/img/patterns/hot01.png' },
  { category: 1, title: '海浪轮廓', text: 'WAVE', bg: '#DBEAFE', fg: '#2563EB', tags: ['自然'], hot: true, realImg: '/assets/img/patterns/hot02.png' },
  { category: 1, title: '复古标签', text: 'AITEE', bg: '#FDE68A', fg: '#92400E', shape: 'tag', tags: ['复古'], hot: true },
  { category: 1, title: '抽象笑脸', text: ':)', bg: '#FCE7F3', fg: '#DB2777', shape: 'circle', tags: ['可爱'], hot: true, realImg: '/assets/img/patterns/hot03.png' },
  { category: 1, title: '极简标语', text: 'BE FREE', bg: '#F3F4F6', fg: '#1F2937', tags: ['极简'], hot: true },
  // 新品
  { category: 2, title: '夏日柠檬', text: 'LEMON', bg: '#FEF9C3', fg: '#A16207', tags: ['夏日'], realImg: '/assets/img/patterns/new01.png' },
  { category: 2, title: '夜空星辰', text: 'STAR', bg: '#1F2937', fg: '#FACC15', tags: ['宇宙'], realImg: '/assets/img/patterns/new02.png' },
  { category: 2, title: '青草地', text: 'GREEN', bg: '#DCFCE7', fg: '#15803D', tags: ['自然'] },
  { category: 2, title: '糖果色', text: 'POP', bg: '#F5D0FE', fg: '#7E22CE', tags: ['糖果'] },
  { category: 2, title: '渐变云朵', text: 'CLOUD', bg: '#E0E7FF', fg: '#4338CA', shape: 'circle', tags: ['梦幻'], realImg: '/assets/img/patterns/new03.png' },
  // 文化衫
  { category: 3, title: '我爱长沙', text: 'CS', bg: '#FFE4E6', fg: '#BE123C', tags: ['城市'], realImg: '/assets/img/patterns/city01.png' },
  { category: 3, title: '北京胡同', text: 'BJ', bg: '#FEE2E2', fg: '#991B1B', tags: ['城市'] },
  { category: 3, title: '上海外滩', text: 'SH', bg: '#E0F2FE', fg: '#0369A1', tags: ['城市'], realImg: '/assets/img/patterns/city02.png' },
  { category: 3, title: '成都熊猫', text: 'CD', bg: '#DCFCE7', fg: '#15803D', tags: ['城市'] },
  { category: 3, title: '广州早茶', text: 'GZ', bg: '#FEF3C7', fg: '#92400E', tags: ['城市'] },
  // IP 系列
  { category: 4, title: '好运', text: '福', bg: '#FEE2E2', fg: '#DC2626', shape: 'circle', tags: ['吉祥'], realImg: '/assets/img/patterns/ip01.png' },
  { category: 4, title: '招财', text: '财', bg: '#FEF3C7', fg: '#A16207', tags: ['吉祥'], realImg: '/assets/img/patterns/ip02.png' },
  { category: 4, title: '稳定', text: '稳', bg: '#E0E7FF', fg: '#3730A3', tags: ['情绪'] },
  { category: 4, title: '快乐', text: '乐', bg: '#DCFCE7', fg: '#166534', tags: ['情绪'] },
  { category: 4, title: '自由', text: '由', bg: '#F3E8FF', fg: '#7E22CE', tags: ['态度'] },
  // 宠物
  { category: 5, title: '柴犬头像', text: 'WOOF', bg: '#FED7AA', fg: '#9A3412', shape: 'circle', tags: ['狗狗'], realImg: '/assets/img/patterns/pet01.png' },
  { category: 5, title: '橘猫脸', text: 'MEOW', bg: '#FECACA', fg: '#991B1B', shape: 'circle', tags: ['猫咪'], realImg: '/assets/img/patterns/pet02.png' },
  { category: 5, title: '小狗肉垫', text: 'PAW', bg: '#FBCFE8', fg: '#9D174D', tags: ['宠物'] },
  { category: 5, title: '我家爱宠', text: 'PET', bg: '#E9D5FF', fg: '#6B21A8', tags: ['宠物'] },
  { category: 5, title: '撸狗使者', text: 'DOG', bg: '#FEF3C7', fg: '#92400E', tags: ['狗狗'] },
  // 用户案例
  { category: 6, title: '小朋友画作', text: 'KID', bg: '#FFF7ED', fg: '#C2410C', tags: ['UGC'] },
  { category: 6, title: '班服印花', text: '2026', bg: '#DBEAFE', fg: '#1D4ED8', tags: ['班服'] },
  { category: 6, title: '婚礼定制', text: 'WED', bg: '#FCE7F3', fg: '#BE185D', shape: 'circle', tags: ['情侣'] },
  { category: 6, title: '马拉松', text: '42.195', bg: '#DCFCE7', fg: '#166534', tags: ['运动'] },
  { category: 6, title: '宠物纪念', text: 'FOREVER', bg: '#E0E7FF', fg: '#3730A3', tags: ['宠物'] },
]

export const patterns: Pattern[] = seeds.map((s, i) => ({
  id: i + 1,
  categoryId: s.category,
  title: s.title,
  imageUrl: s.realImg ?? patternImage({ text: s.text, bg: s.bg, fg: s.fg, shape: s.shape }),
  tags: s.tags,
  isHot: !!s.hot,
  sort: i + 1,
}))
