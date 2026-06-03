/**
 * 平台特性 mock 封装：把微信/抖音/H5 的差异收敛到这里。
 *
 * M2 阶段全部 mock：登录返 fake code、支付直接命中后端 mock notify、
 * 服务通知/订阅消息只在控制台打印模板编号 + 参数。
 */
import { PLATFORM } from './env'
import { Payments } from '../api'

export const isWechat = PLATFORM === 'mp-weixin'
export const isDouyin = PLATFORM === 'mp-toutiao'
export const isH5 = PLATFORM === 'h5'

// ----------------- 登录 -----------------
export async function getPlatformLoginCode(): Promise<string> {
  return new Promise((resolve) => {
    try {
      uni.login({
        provider: isDouyin ? 'toutiao' : 'weixin',
        success: (r: any) => resolve(r?.code || `mock_${Date.now()}`),
        fail: () => resolve(`mock_${Date.now()}`),
      })
    } catch {
      resolve(`mock_${Date.now()}`)
    }
  })
}

// ----------------- 分享（仅微信）-----------------
export interface ShareInfo {
  title: string
  path?: string
  imageUrl?: string
}

let _share: ShareInfo | null = null
export function setShareInfo(info: ShareInfo) {
  _share = info
  console.log('[aitee:share] set', info)
}
export function getShareInfo(): ShareInfo | null {
  return _share
}

// ----------------- 订阅消息 / 服务通知 -----------------
export const WX_TPL = {
  order_paid: 'tpl_order_paid_001',
  order_shipped: 'tpl_order_shipped_002',
  print_ready: 'tpl_print_ready_003',
  partner_payout: 'tpl_partner_payout_004',
}

export async function requestSubscribe(tmplIds: string[]) {
  if (!isWechat) return
  return new Promise((resolve) => {
    try {
      // @ts-ignore
      (uni as any).requestSubscribeMessage({
        tmplIds,
        success: (r: any) => {
          console.log('[aitee:subscribe] success', r)
          resolve(r)
        },
        fail: (e: any) => {
          console.warn('[aitee:subscribe] fail (M2 mock 忽略)', e)
          resolve(null)
        },
      })
    } catch (e) {
      console.warn('[aitee:subscribe] not supported', e)
      resolve(null)
    }
  })
}

// ----------------- 支付（mock）-----------------
/**
 * 统一 mock 支付：
 * - WX/DY/H5 都走后端 /payments/mock/notify
 * - 真支付集成在 M3
 */
export async function mockPay(orderNo: string): Promise<boolean> {
  const method = isWechat ? 'wechat' : isDouyin ? 'douyin' : 'mock'
  console.log(`[aitee:pay] mock ${method} pay for`, orderNo)
  // 模拟支付收银台耗时
  await new Promise((r) => setTimeout(r, 600))
  try {
    await Payments.mockNotify(orderNo, true, method)
    return true
  } catch (e) {
    console.error('[aitee:pay] mockNotify failed', e)
    return false
  }
}

// ----------------- 抖音游客模式 -----------------
/**
 * 抖音小雪花：未登录也允许浏览，下单时再触发登录。
 */
export function allowGuestBrowse(): boolean {
  return isDouyin || isH5
}
