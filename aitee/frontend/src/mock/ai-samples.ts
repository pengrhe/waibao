import type { AiSample } from '@/types'
import { patternImage } from '@/utils/placeholder'

interface Seed {
  prompt: string
  style: string
  text: string
  bg: string
  fg: string
}

const seeds: Seed[] = [
  { prompt: '夕阳下的猫咪', style: '卡通', text: 'CAT', bg: '#FEF3C7', fg: '#C2410C' },
  { prompt: '夕阳下的猫咪', style: '水彩', text: 'CAT', bg: '#FECACA', fg: '#9A3412' },
  { prompt: '夕阳下的猫咪', style: '国潮', text: '猫', bg: '#1F2937', fg: '#FACC15' },
  { prompt: '夕阳下的猫咪', style: '极简', text: '✦', bg: '#F3F4F6', fg: '#1F2937' },
  { prompt: '宇宙星辰', style: '写实', text: 'STAR', bg: '#1E1B4B', fg: '#FACC15' },
  { prompt: '宇宙星辰', style: '卡通', text: '✦', bg: '#E0E7FF', fg: '#4338CA' },
  { prompt: '森林精灵', style: '水彩', text: 'TREE', bg: '#DCFCE7', fg: '#166534' },
  { prompt: '城市夜景', style: '国潮', text: 'CITY', bg: '#1F2937', fg: '#F472B6' },
]

export const aiSamples: AiSample[] = seeds.map((s, i) => ({
  id: i + 1,
  prompt: s.prompt,
  style: s.style,
  imageUrl: patternImage({ text: s.text, bg: s.bg, fg: s.fg, width: 320, height: 320 }),
}))

export const aiStyles = ['卡通', '写实', '水彩', '国潮', '极简', '复古']
