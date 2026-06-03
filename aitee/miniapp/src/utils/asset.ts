/**
 * 静态资源路径工具。
 *
 * 为什么需要这个：
 * - uniapp 编译 mp-weixin/mp-toutiao 时会把 src/static 全部打包进小程序，
 *   而我们的 UI 图（hero/entry/patterns 共 19 张）有 ~30MB，
 *   远超微信主包 2MB / 整体 20MB 限制。
 * - 因此把这批图集中放到 <repo>/aitee/cdn-assets/，由 backend 通过 /cdn/* 暴露，
 *   生产再换成真 CDN 域名。
 *
 * 使用：
 *   <image :src="cdnImg('home/hero.png')" />
 *   <image :src="cdnImg('patterns/' + p.image)" />
 *
 * 平台差异：
 * - H5 dev：返回 `/cdn/...`，走 vite proxy 到 backend 8200
 * - H5 生产：替换 CDN_BASE 为真 CDN
 * - 小程序：用绝对 URL，请将 CDN_BASE 域名加入小程序后台「downloadFile 合法域名」
 */

// #ifdef H5
const CDN_BASE = '/cdn'
// #endif
// #ifndef H5
const CDN_BASE = 'http://127.0.0.1:8200/cdn'
// #endif

export function cdnUrl(path: string): string {
  if (!path) return ''
  // 已经是完整 URL（http/https/blob/data），直接返回
  if (/^(https?:|blob:|data:)/.test(path)) return path
  const p = path.startsWith('/') ? path.slice(1) : path
  return `${CDN_BASE}/${p}`
}

export function cdnImg(name: string): string {
  return cdnUrl(`img/${name}`)
}
