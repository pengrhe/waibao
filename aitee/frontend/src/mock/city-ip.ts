import type { CityIp, CityIpCategory, CityIpItem } from '@/types'
import { patternImage } from '@/utils/placeholder'

export const popularCities = ['深圳', '长沙', '上海', '北京', '成都', '广州', '杭州', '西安']

interface ItemSeed {
  category: CityIpCategory
  title: string
  text: string
  bg: string
  fg: string
  shape?: 'square' | 'circle' | 'tag'
  realImg?: string
}

interface CitySeed {
  city: string
  hint: string
  elements: string[]
  styleWeights: { style: string; ratio: number }[]
  items: ItemSeed[]
}

const seeds: CitySeed[] = [
  {
    city: '深圳',
    hint: '科技 / 海岸 / 速度感',
    elements: ['平安金融中心', '世界之窗', '大梅沙', '红树林', '南头古城', '客家方言', '腌面', '荔枝', '荔枝节', '大鹏所城'],
    styleWeights: [
      { style: '极简', ratio: 0.42 },
      { style: '科技未来', ratio: 0.3 },
      { style: '街潮', ratio: 0.18 },
      { style: '国潮', ratio: 0.1 },
    ],
    items: [
      { category: 'landmark', title: '平安金融中心', text: 'PA TOWER', bg: '#DBEAFE', fg: '#1D4ED8' },
      { category: 'landmark', title: '世界之窗', text: 'WoW', bg: '#FCE7F3', fg: '#BE185D', shape: 'circle' },
      { category: 'landmark', title: '大鹏所城', text: 'OLD TOWN', bg: '#FEF3C7', fg: '#92400E', shape: 'tag' },
      { category: 'landmark', title: '欢乐海岸', text: 'COAST', bg: '#E0F2FE', fg: '#0369A1' },
      { category: 'landmark', title: '红树林', text: '林', bg: '#DCFCE7', fg: '#166534', shape: 'circle' },
      { category: 'folk', title: '客家围屋', text: 'HAKKA', bg: '#FED7AA', fg: '#9A3412' },
      { category: 'folk', title: '南头古城', text: '南头', bg: '#FEF9C3', fg: '#A16207' },
      { category: 'folk', title: '大鹏渔民', text: 'FISH', bg: '#E0F2FE', fg: '#0E7490' },
      { category: 'folk', title: '荔枝节', text: '荔', bg: '#FECACA', fg: '#991B1B', shape: 'circle' },
      { category: 'folk', title: '腌面', text: 'YAN', bg: '#FFE4E6', fg: '#BE123C' },
      { category: 'symbol', title: '深圳速度', text: 'SPD', bg: '#F3F4F6', fg: '#1F2937', shape: 'tag' },
      { category: 'symbol', title: '荔枝纹', text: 'L', bg: '#FCE7F3', fg: '#DB2777', shape: 'circle' },
      { category: 'symbol', title: '海浪轮廓', text: 'WAVE', bg: '#DBEAFE', fg: '#2563EB', realImg: '/assets/img/patterns/hot02.png' },
      { category: 'symbol', title: '科技几何', text: 'SZ', bg: '#E0E7FF', fg: '#4338CA' },
      { category: 'symbol', title: '日落海平线', text: 'SUNSET', bg: '#FFE4D6', fg: '#C2410C' },
    ],
  },
  {
    city: '长沙',
    hint: '国潮 / 美食 / 江景',
    elements: ['橘子洲头', '岳麓山', '湘江夜景', '臭豆腐', '糖油粑粑', '湘绣', '岳麓书院', '马王堆', '茶颜', '辣椒', '槟榔'],
    styleWeights: [
      { style: '国潮', ratio: 0.55 },
      { style: '复古', ratio: 0.22 },
      { style: '卡通', ratio: 0.15 },
      { style: '极简', ratio: 0.08 },
    ],
    items: [
      { category: 'landmark', title: '橘子洲头', text: '橘洲', bg: '#FFE4E6', fg: '#BE123C', realImg: '/assets/img/patterns/city01.png' },
      { category: 'landmark', title: '岳麓山', text: '岳', bg: '#DCFCE7', fg: '#166534', shape: 'circle' },
      { category: 'landmark', title: '湘江夜景', text: 'XIANG', bg: '#1F2937', fg: '#FACC15' },
      { category: 'landmark', title: '岳麓书院', text: '书', bg: '#FEF3C7', fg: '#92400E', shape: 'tag' },
      { category: 'landmark', title: '太平老街', text: '街', bg: '#FED7AA', fg: '#9A3412' },
      { category: 'folk', title: '臭豆腐', text: '臭', bg: '#1F2937', fg: '#84CC16', shape: 'circle' },
      { category: 'folk', title: '糖油粑粑', text: '糖', bg: '#FEF9C3', fg: '#A16207' },
      { category: 'folk', title: '湘绣', text: '绣', bg: '#FCE7F3', fg: '#BE185D' },
      { category: 'folk', title: '马王堆', text: '帛', bg: '#FFEDD5', fg: '#92400E', shape: 'tag' },
      { category: 'folk', title: '茶颜悦色', text: '茶', bg: '#DCFCE7', fg: '#166534', shape: 'circle' },
      { category: 'symbol', title: '辣椒纹样', text: '辣', bg: '#FEE2E2', fg: '#DC2626', shape: 'circle' },
      { category: 'symbol', title: '我爱长沙', text: 'CS', bg: '#FFE4E6', fg: '#BE123C', realImg: '/assets/img/patterns/city01.png' },
      { category: 'symbol', title: '云纹祥瑞', text: '云', bg: '#FEF3C7', fg: '#A16207' },
      { category: 'symbol', title: '湘字篆刻', text: '湘', bg: '#1F2937', fg: '#FACC15', shape: 'tag' },
    ],
  },
  {
    city: '上海',
    hint: '都市 / 海派 / 摩登',
    elements: ['外滩', '东方明珠', '老克勒', '生煎包', '小笼包', '弄堂', '黄包车', '苏州河', '武康大楼', '永康路'],
    styleWeights: [
      { style: '极简', ratio: 0.4 },
      { style: '复古', ratio: 0.32 },
      { style: '街潮', ratio: 0.18 },
      { style: '国潮', ratio: 0.1 },
    ],
    items: [
      { category: 'landmark', title: '外滩', text: 'BUND', bg: '#E0F2FE', fg: '#0369A1', realImg: '/assets/img/patterns/city02.png' },
      { category: 'landmark', title: '东方明珠', text: 'TV', bg: '#DBEAFE', fg: '#1E40AF', shape: 'circle' },
      { category: 'landmark', title: '武康大楼', text: 'WK', bg: '#FFF7ED', fg: '#C2410C' },
      { category: 'landmark', title: '苏州河', text: '河', bg: '#E0E7FF', fg: '#3730A3' },
      { category: 'landmark', title: '上海中心', text: 'SH', bg: '#F3F4F6', fg: '#1F2937', shape: 'tag' },
      { category: 'folk', title: '弄堂', text: '弄', bg: '#FEF3C7', fg: '#92400E', shape: 'tag' },
      { category: 'folk', title: '老克勒', text: 'OLD', bg: '#FCE7F3', fg: '#BE185D' },
      { category: 'folk', title: '生煎', text: '煎', bg: '#FED7AA', fg: '#9A3412', shape: 'circle' },
      { category: 'folk', title: '小笼', text: '笼', bg: '#FEF9C3', fg: '#A16207' },
      { category: 'folk', title: '黄包车', text: 'CAR', bg: '#FFE4E6', fg: '#BE123C' },
      { category: 'symbol', title: '海派旗袍', text: '袍', bg: '#FCE7F3', fg: '#9D174D' },
      { category: 'symbol', title: '上海外滩', text: 'SH', bg: '#E0F2FE', fg: '#0369A1', realImg: '/assets/img/patterns/city02.png' },
      { category: 'symbol', title: '法国梧桐', text: '叶', bg: '#DCFCE7', fg: '#166534', shape: 'circle' },
      { category: 'symbol', title: '复古车票', text: 'TKT', bg: '#FFEDD5', fg: '#92400E', shape: 'tag' },
    ],
  },
  {
    city: '北京',
    hint: '国潮 / 文化 / 厚重',
    elements: ['天坛', '故宫', '长城', '胡同', '炸酱面', '京剧脸谱', '糖葫芦', '颐和园', '鸟巢', '北海'],
    styleWeights: [
      { style: '国潮', ratio: 0.5 },
      { style: '复古', ratio: 0.25 },
      { style: '极简', ratio: 0.15 },
      { style: '卡通', ratio: 0.1 },
    ],
    items: [
      { category: 'landmark', title: '故宫角楼', text: '宫', bg: '#FEE2E2', fg: '#991B1B' },
      { category: 'landmark', title: '天坛', text: '坛', bg: '#FEF9C3', fg: '#A16207', shape: 'circle' },
      { category: 'landmark', title: '长城', text: '长城', bg: '#F3F4F6', fg: '#1F2937', shape: 'tag' },
      { category: 'landmark', title: '颐和园', text: '园', bg: '#DCFCE7', fg: '#166534' },
      { category: 'landmark', title: '鸟巢', text: 'NEST', bg: '#FED7AA', fg: '#9A3412' },
      { category: 'folk', title: '胡同', text: '胡同', bg: '#FEE2E2', fg: '#991B1B', realImg: '/assets/img/patterns/ip01.png' },
      { category: 'folk', title: '炸酱面', text: '面', bg: '#FEF3C7', fg: '#92400E', shape: 'circle' },
      { category: 'folk', title: '糖葫芦', text: '糖', bg: '#FFE4E6', fg: '#BE123C' },
      { category: 'folk', title: '京剧脸谱', text: '脸', bg: '#FCE7F3', fg: '#BE185D' },
      { category: 'folk', title: '北京烤鸭', text: '鸭', bg: '#FED7AA', fg: '#9A3412' },
      { category: 'symbol', title: '福字', text: '福', bg: '#FEE2E2', fg: '#DC2626', shape: 'circle', realImg: '/assets/img/patterns/ip01.png' },
      { category: 'symbol', title: '云龙纹', text: '龙', bg: '#FEF3C7', fg: '#A16207' },
      { category: 'symbol', title: '五星', text: '★', bg: '#FEE2E2', fg: '#DC2626', shape: 'circle' },
      { category: 'symbol', title: '京字篆', text: '京', bg: '#1F2937', fg: '#FACC15', shape: 'tag' },
    ],
  },
  {
    city: '成都',
    hint: '巴适 / 熊猫 / 慢生活',
    elements: ['大熊猫', '宽窄巷子', '锦里', '川剧变脸', '火锅', '麻婆豆腐', '四川话', '都江堰', '春熙路', '茶馆'],
    styleWeights: [
      { style: '卡通', ratio: 0.42 },
      { style: '国潮', ratio: 0.28 },
      { style: '复古', ratio: 0.18 },
      { style: '极简', ratio: 0.12 },
    ],
    items: [
      { category: 'landmark', title: '宽窄巷子', text: '巷', bg: '#FEF3C7', fg: '#92400E' },
      { category: 'landmark', title: '锦里', text: '锦', bg: '#FFE4E6', fg: '#BE123C', shape: 'tag' },
      { category: 'landmark', title: '都江堰', text: '堰', bg: '#E0F2FE', fg: '#0369A1' },
      { category: 'landmark', title: '春熙路', text: '熙', bg: '#FCE7F3', fg: '#BE185D' },
      { category: 'landmark', title: '青城山', text: '青', bg: '#DCFCE7', fg: '#166534', shape: 'circle' },
      { category: 'folk', title: '火锅', text: '锅', bg: '#FEE2E2', fg: '#DC2626', shape: 'circle' },
      { category: 'folk', title: '麻婆豆腐', text: '麻', bg: '#FED7AA', fg: '#9A3412' },
      { category: 'folk', title: '川剧变脸', text: '脸', bg: '#1F2937', fg: '#F87171' },
      { category: 'folk', title: '盖碗茶', text: '茶', bg: '#FEF9C3', fg: '#A16207', shape: 'circle' },
      { category: 'folk', title: '担担面', text: '担', bg: '#FFE4E6', fg: '#BE123C' },
      { category: 'symbol', title: '熊猫', text: 'PANDA', bg: '#F3F4F6', fg: '#1F2937', shape: 'circle' },
      { category: 'symbol', title: '辣椒纹', text: '辣', bg: '#FEE2E2', fg: '#DC2626' },
      { category: 'symbol', title: '蜀字篆', text: '蜀', bg: '#FEF3C7', fg: '#A16207', shape: 'tag' },
      { category: 'symbol', title: '成字标记', text: '成', bg: '#1F2937', fg: '#FACC15' },
    ],
  },
]

function buildItems(city: string, seedItems: ItemSeed[]): CityIpItem[] {
  return seedItems.map((s, i) => ({
    id: `${city}-${i + 1}`,
    category: s.category,
    title: s.title,
    imageUrl: s.realImg ?? patternImage({ text: s.text, bg: s.bg, fg: s.fg, shape: s.shape }),
    tags: [s.category, s.title],
  }))
}

export const cityIpData: Record<string, CityIp> = Object.fromEntries(
  seeds.map((s) => [
    s.city,
    {
      city: s.city,
      totalCount: 500 + Math.floor(Math.random() * 80),
      elements: [...s.elements],
      items: buildItems(s.city, s.items),
      styleWeights: s.styleWeights,
      generatedAt: Date.now(),
    } satisfies CityIp,
  ]),
)

export const cityHints: Record<string, string> = Object.fromEntries(
  seeds.map((s) => [s.city, s.hint]),
)
