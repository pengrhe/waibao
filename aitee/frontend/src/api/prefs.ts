/**
 * 用户偏好上报埋点（C 端）。
 *
 * - 只在 VITE_API_MODE=real 且已登录时上报，否则 no-op。
 * - 后端 /api/v1/user/prefs 会累计计数，连续 3 次同值自动标记为 default。
 * - 失败不抛错（不影响主流程）。
 */
import { REAL_API, getToken, rpost } from './http'

export async function reportPref(pref_type: string, value: string | number | null | undefined): Promise<void> {
  if (!REAL_API || !getToken() || value == null || value === '') return
  try {
    await rpost('/user/prefs', { pref_type, value: String(value) })
  } catch {
    /* swallow */
  }
}
