<script setup lang="ts">
import { onLaunch, onShareAppMessage, onShareTimeline } from '@dcloudio/uni-app'
import { getShareInfo } from './utils/platform'

onLaunch(() => {
  console.log('[aitee] launch on', uni.getSystemInfoSync().uniPlatform)
})

// 全局分享（微信小程序自动生效；其它平台静默忽略）
onShareAppMessage(() => {
  const s = getShareInfo()
  return {
    title: s?.title || 'aitee · 把灵感穿上身',
    path: s?.path || '/pages/index/index',
    imageUrl: s?.imageUrl,
  }
})

onShareTimeline(() => {
  const s = getShareInfo()
  return {
    title: s?.title || 'aitee · 一键 AI 定制你的潮 T 恤',
    imageUrl: s?.imageUrl,
  }
})
</script>

<style lang="scss">
/* 这里用 @import 是有意为之：global.scss 包含全局规则（page、view、button 重置等），
 * @use 只导入符号不会注入 ruleset。
 * sass 的 legacy-import deprecation 警告可以忽略，下一次升级 sass 3.x 再迁移。
 */
@import '@/styles/global.scss';

/* H5 端：原生 tabBar 用 CustomTabBar 完全替代，永久隐藏。
 * 各 tab 页 onShow 还会再调一次 uni.hideTabBar 兜底。 */
/* #ifdef H5 */
.uni-tabbar,
.uni-tabbar--top,
.uni-tabbar-bottom,
uni-tabbar,
.uni-app--showtabbar uni-tabbar {
  display: none !important;
  height: 0 !important;
  visibility: hidden !important;
}
/* #endif */
</style>
