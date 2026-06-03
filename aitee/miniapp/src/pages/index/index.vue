<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import BrandHeader from '../../components/BrandHeader.vue'
import Countdown from '../../components/Countdown.vue'
import SectionHead from '../../components/SectionHead.vue'
import CustomTabBar from '../../components/CustomTabBar.vue'
import { onShow } from '@dcloudio/uni-app'
import { Home, Messages, Coupon } from '../../api'
import { useAuthStore } from '../../store/auth'
import { cdnImg } from '../../utils/asset'

const auth = useAuthStore()
const heroBanner = ref<any>(null)
const topics = ref<any[]>([])
const newcomerCoupon = ref<any>(null)
const unread = ref(0)

interface BentoEntry {
  id: string
  label: string
  sub?: string
  image?: string
  to: string
  variant: 'hero' | 'city' | 'small'
  switchTab?: boolean
}

const bento: BentoEntry[] = [
  { id: 'personal', label: '个人定制', sub: '从一件白 T 开始', image: cdnImg('entry/personalize.png'), to: '/pages/editor/index', variant: 'hero' },
  { id: 'city-ip', label: 'AI 城市 IP', sub: '本地化生成', to: '/pages/city-ip/index', variant: 'city' },
  { id: 'gallery', label: '印花库', image: cdnImg('entry/gallery.png'), to: '/pages/gallery/index', variant: 'small', switchTab: true },
  { id: 'pet', label: '宠物模板', image: cdnImg('entry/pet.png'), to: '/pages/gallery/index?cat=5', variant: 'small', switchTab: true },
  { id: 'extract', label: '来图定制', image: cdnImg('entry/extract.png'), to: '/pages/ai-create/index?mode=i2i', variant: 'small' },
]

// 打字机 prompt
const samplePrompts = [
  '橘猫戴墨镜冲浪',
  '宇宙星辰，复古胶片',
  '我家狗子在做梦',
  '夏日柠檬，极简插画',
  '深圳天际线，赛博朋克',
]
const typedPrompt = ref('')
let promptIdx = 0
let charIdx = 0
let mode: 'typing' | 'pause' | 'deleting' = 'typing'
let timer: any = null

function tick() {
  const cur = samplePrompts[promptIdx]
  if (mode === 'typing') {
    if (charIdx < cur.length) {
      charIdx++
      typedPrompt.value = cur.slice(0, charIdx)
      timer = setTimeout(tick, 110)
    } else {
      mode = 'pause'
      timer = setTimeout(tick, 1500)
    }
  } else if (mode === 'pause') {
    mode = 'deleting'
    timer = setTimeout(tick, 60)
  } else {
    if (charIdx > 0) {
      charIdx--
      typedPrompt.value = cur.slice(0, charIdx)
      timer = setTimeout(tick, 35)
    } else {
      promptIdx = (promptIdx + 1) % samplePrompts.length
      mode = 'typing'
      timer = setTimeout(tick, 250)
    }
  }
}

const couponEndAt = computed(() => {
  const e = newcomerCoupon.value?.expire_at
  if (!e) return Date.now() + 72 * 3600 * 1000
  return new Date(e).getTime()
})
const couponDiscount = computed(() => {
  const c = newcomerCoupon.value?.coupon
  if (!c) return '7.8'
  if (c.type === 'discount') return `${(Number(c.value) * 10).toFixed(1)}`.replace('.0', '')
  return `${c.value}`
})
const couponUnit = computed(() => (newcomerCoupon.value?.coupon?.type === 'cash' ? '元' : '折'))

// mock 推荐 feed（避免在没数据时空白）
const recommend = ref<any[]>([
  { id: 1, title: '活动衫', image: cdnImg('patterns/hot01.png') },
  { id: 2, title: '文化衫', image: cdnImg('patterns/hot02.png') },
  { id: 3, title: '班服', image: cdnImg('patterns/hot03.png') },
  { id: 4, title: '亲子装', image: cdnImg('patterns/new01.png') },
  { id: 5, title: '宠物装', image: cdnImg('patterns/pet01.png') },
  { id: 6, title: '潮 T', image: cdnImg('patterns/new02.png') },
])

async function load() {
  try {
    const bs = await Home.banners('home_top')
    heroBanner.value = bs[0] ?? null
  } catch {}
  try {
    topics.value = await Home.topics()
  } catch {}
  if (auth.isAuthed) {
    try {
      const r = await Messages.unreadCount()
      unread.value = r.count
    } catch {}
    try {
      const list = await Coupon.mine('unused')
      newcomerCoupon.value = list[0] ?? null
    } catch {}
  }
}

onMounted(() => {
  load()
  tick()
})

onShow(() => {
  try { uni.hideTabBar({ animation: false }) } catch {}
})

onBeforeUnmount(() => {
  if (timer) clearTimeout(timer)
})

function go(to?: string, switchTab = false) {
  if (!to) return
  if (switchTab) uni.switchTab({ url: to }).catch(() => uni.navigateTo({ url: to }))
  else uni.navigateTo({ url: to })
}

function onCouponClick() {
  if (!auth.isAuthed) {
    uni.navigateTo({ url: '/pages/login/index' })
    return
  }
  uni.navigateTo({ url: '/pages/coupons/index' })
}

function onPromptClick() {
  uni.navigateTo({ url: '/pages/ai-create/index' })
}

function openMsg() {
  if (!auth.isAuthed) { uni.navigateTo({ url: '/pages/login/index' }); return }
  uni.navigateTo({ url: '/pages/messages/index' })
}
</script>

<template>
  <view class="home">
    <BrandHeader :right-text="unread > 0 ? `🔔 ${unread}` : '🔔'" @right-click="openMsg" />

    <!-- Hero -->
    <view class="hero">
      <image
        class="hero__pic"
        :src="cdnImg('home/hero.png')"
        mode="aspectFill"
      />
      <view class="hero__mask" />
      <view class="hero__body">
        <view class="hero__eyebrow">
          <view class="hero__dot" />
          <text>AI 驱动 · 创意定制</text>
        </view>
        <view class="hero__title">
          <text class="hero__line">把灵感</text>
          <text class="hero__line hero__line--accent">穿上身</text>
        </view>
        <text class="hero__desc">输一句话，2 秒生成你的专属图案</text>
      </view>
    </view>

    <!-- Prompt CTA：打字机 -->
    <view class="prompt-cta" @click="onPromptClick">
      <view class="prompt-cta__icon"><text>✦</text></view>
      <view class="prompt-cta__text">
        <text class="prompt-cta__placeholder">试试：</text>
        <text class="prompt-cta__typed">{{ typedPrompt }}</text>
        <text class="prompt-cta__caret">|</text>
      </view>
      <view class="prompt-cta__send"><text>→</text></view>
    </view>

    <!-- Bento Grid -->
    <view class="bento">
      <view class="bento__head">
        <text class="bento__title">开始定制</text>
        <text class="bento__count">5 种创意路径</text>
      </view>
      <view class="bento__grid">
        <view
          v-for="b in bento"
          :key="b.id"
          class="bento-card"
          :class="`bento-card--${b.variant}`"
          @click="go(b.to, b.switchTab)"
        >
          <template v-if="b.variant === 'hero'">
            <image class="bento-card__pic" :src="b.image!" mode="aspectFill" />
            <view class="bento-card__overlay">
              <text class="bento-card__label">{{ b.label }}</text>
              <text class="bento-card__sub">{{ b.sub }}</text>
              <view class="bento-card__cta">
                <text>立即开始</text>
                <text class="bento-card__cta-arrow">→</text>
              </view>
            </view>
          </template>
          <template v-else-if="b.variant === 'city'">
            <!-- 用纯样式画的城市天际线 -->
            <view class="bento-card__city-sky">
              <view v-for="n in 7" :key="n" class="bento-card__city-bldg" :style="{ height: (12 + ((n * 17) % 32)) + 'px', left: ((n - 1) * 14) + '%' }" />
            </view>
            <view class="bento-card__city-pin"><text>📍</text></view>
            <view class="bento-card__city-body">
              <view class="bento-card__city-row">
                <text class="bento-card__city-label">AI 城市 IP</text>
                <text class="bento-card__city-chip">NEW</text>
              </view>
              <text class="bento-card__city-sub">{{ b.sub }}</text>
            </view>
          </template>
          <template v-else>
            <image class="bento-card__pic-sm" :src="b.image!" mode="aspectFill" />
            <text class="bento-card__label-sm">{{ b.label }}</text>
          </template>
        </view>
      </view>
    </view>

    <!-- 新人券 -->
    <view class="coupon" @click="onCouponClick">
      <view class="coupon__num">
        <text class="coupon__num-val">{{ couponDiscount }}</text>
        <text class="coupon__num-unit">{{ couponUnit }}</text>
      </view>
      <view class="coupon__divider" />
      <view class="coupon__info">
        <view class="coupon__tag">
          <text class="coupon__tag-icon">🎁</text>
          <text class="coupon__tag-text">新人专享</text>
        </view>
        <view class="coupon__count">
          <Countdown :end-time="couponEndAt" size="sm" />
          <text class="coupon__count-suffix">后失效</text>
        </view>
      </view>
      <view class="coupon__btn">领取</view>
    </view>

    <!-- 案例 feed -->
    <view class="section">
      <SectionHead title="看看大家怎么定制的" more="/pages/gallery/index" more-text="全部" />
      <view class="recommend-grid">
        <view v-for="(r, i) in recommend" :key="r.id" class="recommend-card" @click="go('/pages/gallery/index', true)">
          <image :src="r.image" class="recommend-card__img" mode="aspectFill" />
          <view class="recommend-card__meta">
            <text class="recommend-card__author">@设计师{{ ((i * 37) % 99) + 10 }}</text>
            <text class="recommend-card__use">❤ {{ ((i * 113) % 800) + 99 }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 内容专区 -->
    <view v-for="t in topics" :key="t.id" class="section">
      <SectionHead :title="t.title" more="/pages/gallery/index" more-text="更多" />
      <scroll-view scroll-x class="topic-scroll">
        <view v-for="it in (t.items || [])" :key="it.id" class="topic-card" @click="go('/pages/gallery/index', true)">
          <image :src="it.image_url || it.imageUrl" class="topic-card__img" mode="aspectFill" />
        </view>
        <view v-if="!t.items || !t.items.length" class="topic-card topic-card--ph"><text>暂无</text></view>
      </scroll-view>
    </view>

    <view class="footer-tip">已经到底啦 · aitee</view>

    <CustomTabBar current="home" />
  </view>
</template>

<style lang="scss" scoped>
.home {
  min-height: 100vh;
  padding-bottom: calc(#{$tabbar-height} + 16px);
  background:
    radial-gradient(120% 60% at 50% 0%, #ffe1e3 0%, transparent 60%),
    linear-gradient(180deg, #fff7f6 0%, #f6f7fb 280px, #f6f7fb 100%);
}

/* ============== Hero ============== */
.hero {
  position: relative;
  margin: 0 12px;
  height: 240px;
  border-radius: 20px;
  overflow: hidden;

  &__pic {
    position: absolute; inset: 0; width: 100%; height: 100%;
  }
  &__mask {
    position: absolute; inset: 0;
    background: linear-gradient(110deg, rgba(255,255,255,.7) 0%, rgba(255,255,255,.2) 50%, rgba(255,255,255,0) 100%);
  }
  &__body {
    position: relative; z-index: 3;
    padding: 28px 20px 0;
  }
  &__eyebrow {
    display: inline-flex; align-items: center; gap: 6px;
    font-size: 11px; font-weight: 600;
    color: $color-primary;
    background: rgba(255,255,255,.72);
    padding: 4px 10px; border-radius: 999px;
  }
  &__dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: $color-primary;
    box-shadow: 0 0 0 3px rgba(255,77,79,.18);
    animation: heroDotPulse 1.6s ease-in-out infinite;
  }
  &__title { margin: 14px 0 6px; line-height: 1.1; }
  &__line {
    display: block;
    font-size: 30px; font-weight: 900; letter-spacing: -0.5px;
    color: #111;
    &--accent {
      background: linear-gradient(120deg, #ff4d4f 20%, #ff8a3a 90%);
      -webkit-background-clip: text;
      background-clip: text;
      color: transparent;
    }
  }
  &__desc { font-size: 12px; color: #4b5563; font-weight: 500; }
}

@keyframes heroDotPulse {
  0%, 100% { box-shadow: 0 0 0 3px rgba(255,77,79,.18); }
  50% { box-shadow: 0 0 0 6px rgba(255,77,79,.05); }
}

/* ============== Prompt CTA ============== */
.prompt-cta {
  margin: -22px 20px 0;
  position: relative; z-index: 4;
  display: flex; align-items: center;
  height: 52px;
  background: #fff;
  border-radius: 14px;
  padding: 0 6px 0 14px;
  box-shadow: 0 12px 32px rgba(31,31,31,.12);

  &__icon {
    width: 28px; height: 28px; border-radius: 8px;
    background: linear-gradient(135deg, #ff8a3a, #ff4d4f);
    display: flex; align-items: center; justify-content: center;
    margin-right: 8px;
    text { color: #fff; font-size: 14px; font-weight: 800; line-height: 1; }
  }
  &__text { flex: 1; min-width: 0; font-size: 13px; color: #1f2937; overflow: hidden; }
  &__placeholder { color: #9ca3af; font-weight: 500; }
  &__typed { color: #1f2937; font-weight: 600; }
  &__caret {
    color: $color-primary; margin-left: 1px;
    animation: caretBlink .9s steps(1, end) infinite;
  }
  &__send {
    width: 40px; height: 40px; border-radius: 12px;
    background: linear-gradient(135deg, #ff8a3a, #ff4d4f);
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 4px 10px rgba(255,77,79,.35);
    text { color: #fff; font-size: 18px; font-weight: 800; line-height: 1; }
  }
}

@keyframes caretBlink { 0%, 50% { opacity: 1; } 50.01%, 100% { opacity: 0; } }

/* ============== Bento Grid ============== */
.bento {
  margin: 24px 12px 0;

  &__head {
    display: flex; align-items: baseline; justify-content: space-between;
    padding: 0 4px; margin-bottom: 10px;
  }
  &__title { font-size: 18px; font-weight: 800; color: #111; letter-spacing: -0.3px; }
  &__count { font-size: 11px; color: $color-text-secondary; }
  &__grid {
    display: grid;
    grid-template-columns: 1.35fr 1fr;
    grid-template-rows: 100px 100px 100px;
    gap: 10px;
  }
}

.bento-card {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  background: #fff;
  border: 1px solid rgba(0,0,0,.04);
  box-shadow: 0 2px 8px rgba(0,0,0,.03);

  &--hero {
    grid-column: 1; grid-row: 1 / span 2;
  }
  &--city {
    background:
      radial-gradient(80% 100% at 100% 0%, rgba(255,217,230,.7) 0%, transparent 60%),
      radial-gradient(80% 80% at 0% 100%, rgba(255,222,198,.7) 0%, transparent 60%),
      linear-gradient(135deg, #fff7ef 0%, #fff0e2 55%, #ffe5ec 100%);
    border: 1px solid rgba(255,138,58,.16);
  }
  &__city-sky {
    position: absolute; left: 0; right: 0; bottom: 0; height: 56px;
  }
  &__city-bldg {
    position: absolute; bottom: 0; width: 14px;
    background: linear-gradient(180deg, rgba(255,77,110,.22) 0%, rgba(200,75,255,.18) 100%);
    border-radius: 2px 2px 0 0;
  }
  &__city-pin {
    position: absolute; top: 12px; right: 12px;
    width: 22px; height: 22px; border-radius: 50%;
    background: linear-gradient(135deg, #ff8a3a 0%, #ff4d6e 100%);
    box-shadow: 0 0 0 3px rgba(255,138,58,.18), 0 4px 10px rgba(255,77,110,.35);
    display: flex; align-items: center; justify-content: center;
    z-index: 2;
    text { font-size: 12px; line-height: 1; }
  }
  &__city-body {
    position: absolute; left: 12px; right: 12px; bottom: 10px; z-index: 3;
  }
  &__city-row { display: flex; align-items: center; gap: 6px; }
  &__city-label {
    font-size: 14px; font-weight: 800; letter-spacing: -0.2px;
    background: linear-gradient(135deg, #ff7a2a 0%, #ff4d6e 60%, #c84bff 100%);
    -webkit-background-clip: text; background-clip: text; color: transparent;
  }
  &__city-chip {
    background: linear-gradient(135deg, #ff8a3a, #ff4d4f);
    color: #fff; font-size: 9px; font-weight: 800;
    padding: 2px 6px; border-radius: 4px; letter-spacing: 0.5px;
    box-shadow: 0 2px 5px rgba(255,77,79,.4);
  }
  &__city-sub { margin-top: 2px; font-size: 10px; color: rgba(50,30,40,.55); line-height: 1.3; }

  &--small {
    background: #fff;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    gap: 6px;
  }
  &__pic { position: absolute; inset: 0; width: 100%; height: 100%; }
  &__overlay {
    position: absolute; inset: 0;
    padding: 16px;
    display: flex; flex-direction: column; justify-content: flex-end; align-items: flex-start;
    background: linear-gradient(180deg, rgba(0,0,0,0) 50%, rgba(0,0,0,.55) 100%);
  }
  &__label { font-size: 16px; font-weight: 800; color: #fff; }
  &__label-sm { font-size: 12px; font-weight: 700; color: #1f2937; }
  &__sub { font-size: 11px; margin-top: 2px; color: rgba(255,255,255,.85); font-weight: 500; }
  &__cta {
    margin-top: 10px;
    display: inline-flex; align-items: center; gap: 4px;
    padding: 6px 12px;
    background: rgba(255,255,255,.96);
    color: #111; font-size: 11px; font-weight: 700;
    border-radius: 999px;
  }
  &__cta-arrow { font-weight: 800; }
  &__pic-sm { width: 60px; height: 60px; border-radius: 14px; }
}

/* ============== Coupon ============== */
.coupon {
  margin: 16px 12px 0;
  height: 78px;
  display: flex; align-items: center;
  padding: 0 16px 0 12px;
  background: linear-gradient(95deg, #fff5f1 0%, #fff8f3 60%, #fff 100%);
  border-radius: 16px;
  position: relative; overflow: hidden;
  box-shadow: 0 4px 16px rgba(255,77,79,.08);

  &__num {
    width: 60px; height: 60px; border-radius: 50%; flex-shrink: 0;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    background: radial-gradient(80% 80% at 30% 30%, #ff8a3a 0%, #ff4d4f 100%);
    color: #fff;
    box-shadow: 0 6px 14px rgba(255,77,79,.4);
    line-height: 1;
  }
  &__num-val { font-size: 22px; font-weight: 900; line-height: 1.05; letter-spacing: -0.5px; }
  &__num-unit { font-size: 10px; font-weight: 700; line-height: 1; margin-top: 1px; opacity: .95; }
  &__divider {
    width: 1px; height: 40px;
    background: repeating-linear-gradient(to bottom, rgba(0,0,0,.12) 0, rgba(0,0,0,.12) 3px, transparent 3px, transparent 6px);
    margin: 0 14px; flex-shrink: 0;
  }
  &__info { flex: 1; min-width: 0; }
  &__tag { display: inline-flex; align-items: center; gap: 4px; }
  &__tag-icon { font-size: 14px; }
  &__tag-text { font-size: 13px; font-weight: 800; color: #1f2937; }
  &__count { margin-top: 4px; font-size: 11px; color: $color-text-secondary; display: flex; align-items: center; gap: 4px; }
  &__count-suffix { color: $color-text-secondary; }
  &__btn {
    flex-shrink: 0;
    padding: 8px 16px;
    background: #1f2937; color: #fff;
    font-size: 12px; font-weight: 700;
    border-radius: 999px;
  }
}

/* ============== Sections ============== */
.section { margin: 24px 12px 0; }

.recommend-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.recommend-card {
  background: #fff; border-radius: 14px; overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,.04);
  &__img { width: 100%; aspect-ratio: 1; }
  &__meta {
    padding: 8px 10px; display: flex; align-items: center; justify-content: space-between;
    font-size: 11px; color: $color-text-secondary;
  }
  &__author { color: #374151; font-weight: 600; }
  &__use { color: $color-primary; font-weight: 600; }
}

.topic-scroll { white-space: nowrap; }
.topic-card {
  display: inline-block;
  width: 130px; vertical-align: top;
  margin-right: 10px;
  border-radius: 12px; overflow: hidden;
  background: #fff;
  box-shadow: 0 2px 6px rgba(0,0,0,.04);
  &__img { width: 130px; height: 162px; }
  &--ph { width: 130px; height: 162px; line-height: 162px; text-align: center; color: $color-text-placeholder; font-size: 12px; }
}

.footer-tip { text-align: center; font-size: 11px; color: $color-text-placeholder; padding: 32px 0 16px; }
</style>
