export function fmtPrice(n: number | string): string {
  return Number(n || 0).toFixed(2)
}

export function fmtTime(ts: number | string | Date): string {
  const d = new Date(ts)
  const pad = (n: number) => n.toString().padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

export function fmtCountdown(ms: number): { h: string; m: string; s: string } {
  const total = Math.max(0, Math.floor(ms / 1000))
  const h = Math.floor(total / 3600)
  const m = Math.floor((total % 3600) / 60)
  const s = total % 60
  const pad = (n: number) => n.toString().padStart(2, '0')
  return { h: pad(h), m: pad(m), s: pad(s) }
}

export function maskPhone(phone?: string): string {
  if (!phone || phone.length < 7) return phone || ''
  return phone.slice(0, 3) + '****' + phone.slice(-4)
}

export const ORDER_STATUS_TEXT: Record<string, string> = {
  pending_pay: '待付款',
  pending_print: '待打印',
  printing: '打印中',
  printed: '待取件',
  pending_pickup: '待取件',
  completed: '已完成',
  done: '已完成',
  canceled: '已取消',
  cancelled: '已取消',
  refunded: '已退款',
}

export const ORDER_STATUS_COLOR: Record<string, string> = {
  pending_pay: '#F59E0B',
  pending_print: '#3B82F6',
  printing: '#8B5CF6',
  printed: '#10B981',
  pending_pickup: '#10B981',
  completed: '#6B7280',
  done: '#6B7280',
  canceled: '#9CA3AF',
  cancelled: '#9CA3AF',
  refunded: '#9CA3AF',
}
