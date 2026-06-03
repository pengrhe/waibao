const BEIJING_OFFSET_MS = 8 * 60 * 60 * 1000

function pad2(n: number): string {
  return n < 10 ? `0${n}` : `${n}`
}

/**
 * 将后端返回的时间统一格式化为北京时间 (UTC+8)。
 *
 * - 输入支持 ISO 字符串、Date、毫秒时间戳。
 * - 不带时区后缀的字符串（如 "2026-05-27T04:10:41"）按 UTC 解析。
 * - 输入为空 / 非法时返回 "-"。
 */
export function formatBJT(
  input: string | number | Date | null | undefined,
  withSeconds = true,
): string {
  if (input === null || input === undefined || input === '') return '-'

  let date: Date
  if (input instanceof Date) {
    date = input
  } else if (typeof input === 'number') {
    date = new Date(input)
  } else {
    let s = String(input).trim()
    const hasTz = /([zZ]|[+-]\d{2}:?\d{2})$/.test(s)
    if (!hasTz) {
      s = s.replace(' ', 'T') + 'Z'
    }
    date = new Date(s)
  }

  if (Number.isNaN(date.getTime())) return '-'

  const bj = new Date(date.getTime() + BEIJING_OFFSET_MS)
  const y = bj.getUTCFullYear()
  const m = pad2(bj.getUTCMonth() + 1)
  const d = pad2(bj.getUTCDate())
  const hh = pad2(bj.getUTCHours())
  const mm = pad2(bj.getUTCMinutes())
  if (!withSeconds) return `${y}-${m}-${d} ${hh}:${mm}`
  const ss = pad2(bj.getUTCSeconds())
  return `${y}-${m}-${d} ${hh}:${mm}:${ss}`
}
