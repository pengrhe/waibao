import { aiSamples, aiStyles } from '@/mock/ai-samples'
import { mockCall } from './request'
import type { AiSample } from '@/types'
import { REAL_API, rget, rpost } from './http'
import { reportPref } from './prefs'

export async function fetchAiStyles(): Promise<string[]> {
  if (REAL_API) {
    try {
      const styles: any = await rget('/ai/styles')
      return styles?.length ? styles : aiStyles
    } catch {
      return aiStyles
    }
  }
  return mockCall(() => aiStyles, 80, 160)
}

/** 文生图 / 图生图 / 图+文：REAL 模式调真后端，失败 fallback 到 mock */
export async function generateAiImages(opts: {
  prompt?: string
  style?: string
  count?: number
}): Promise<AiSample[]> {
  const { count = 4, style, prompt = '' } = opts

  // 偏好埋点：记录用户选择的风格
  if (style) reportPref('ai_style', style)

  if (REAL_API) {
    try {
      const resp: any = await rpost('/ai/generate', {
        type: 't2i',
        prompt,
        style,
        n: count,
      })
      const samples = (resp?.samples || []) as Array<{
        id: number
        image_url: string
        prompt?: string
        style?: string
      }>
      if (samples.length) {
        return samples.map((s) => ({
          id: s.id,
          prompt: s.prompt || prompt,
          style: s.style || style || '',
          imageUrl: s.image_url,
        }))
      }
    } catch (e) {
      console.warn('AI real api failed, fallback to mock', e)
    }
  }

  return mockCall(
    () => {
      const pool = aiSamples.slice()
      const picks: AiSample[] = []
      for (let i = 0; i < count; i++) {
        const idx = Math.floor(Math.random() * pool.length)
        const sample = pool[idx]
        picks.push({
          ...sample,
          id: Date.now() + i,
          prompt: prompt || sample.prompt,
          style: style || sample.style,
        })
      }
      return picks
    },
    1800,
    2800,
  )
}
