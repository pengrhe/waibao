<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import BrandHeader from '@/components/BrandHeader.vue'
import Countdown from '@/components/Countdown.vue'
import { fetchHomeBanners, fetchRecommend, fetchTopics } from '@/api/home'
import { listCoupons } from '@/api/coupon'
import type { Banner, Coupon, RecommendItem, TopicSection } from '@/types'

const router = useRouter()

const heroBanner = ref<Banner | null>(null)
const recommend = ref<RecommendItem[]>([])
const topics = ref<TopicSection[]>([])
const newcomerCoupon = ref<Coupon | null>(null)
const loading = ref(true)

interface BentoEntry {
  id: string
  label: string
  sub?: string
  image?: string
  to: string
  variant: 'hero' | 'city' | 'small'
  icon?: string
}

const bento: BentoEntry[] = [
  {
    id: 'personal',
    label: '个人定制',
    sub: '从一件白 T 开始',
    image: '/assets/img/entry/personalize.png',
    to: '/editor',
    variant: 'hero',
  },
  {
    id: 'city-ip',
    label: 'AI 城市 IP',
    sub: '本地化生成',
    to: '/city-ip',
    variant: 'city',
  },
  {
    id: 'gallery',
    label: '印花库',
    image: '/assets/img/entry/gallery.png',
    to: '/gallery',
    variant: 'small',
  },
  {
    id: 'pet',
    label: '宠物模板',
    image: '/assets/img/entry/pet.png',
    to: '/gallery?cat=5',
    variant: 'small',
  },
  {
    id: 'extract',
    label: '来图定制',
    image: '/assets/img/entry/extract.png',
    to: '/upload-result',
    variant: 'small',
  },
]

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
let timer: ReturnType<typeof setTimeout> | null = null

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

const couponEndAt = computed(() => newcomerCoupon.value?.expireAt ?? Date.now() + 72 * 3600 * 1000)
const couponDiscount = computed(() => {
  const c = newcomerCoupon.value
  if (!c) return '7.8'
  if (c.type === 'discount') return `${(c.value * 10).toFixed(1)}`.replace('.0', '')
  return `${c.value}`
})
const couponUnit = computed(() => (newcomerCoupon.value?.type === 'amount' ? '元' : '折'))

async function load() {
  loading.value = true
  try {
    const [banners, rec, tps, coupons] = await Promise.all([
      fetchHomeBanners('home_top'),
      fetchRecommend(),
      fetchTopics(),
      listCoupons(),
    ])
    heroBanner.value = banners[0] ?? null
    recommend.value = rec
    topics.value = tps
    newcomerCoupon.value = coupons.find((c) => c.status === 'unused') ?? coupons[0] ?? null
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  load()
  tick()
})

onBeforeUnmount(() => {
  if (timer) clearTimeout(timer)
})

function go(to?: string) {
  if (!to) return
  router.push(to)
}

function onCouponClick() {
  router.push('/coupon')
}

function onPromptClick() {
  router.push('/ai-create')
}
</script>

<template>
  <div class="home">
    <BrandHeader />

    <!-- Hero: 满铺插画 + 大字标题，无 xuyu 同款白云气泡 -->
    <section class="hero">
      <div class="hero__pic" :style="heroBanner ? { backgroundImage: `url(${heroBanner.imageUrl})` } : {}" />
      <div class="hero__mask" />
      <div class="hero__body">
        <div class="hero__eyebrow">
          <span class="hero__dot" />
          AI 驱动 · 创意定制
        </div>
        <h1 class="hero__title">
          <span class="hero__line">把灵感</span>
          <span class="hero__line hero__line--accent">穿上身</span>
        </h1>
        <div class="hero__desc">输一句话，2 秒生成你的专属图案</div>
      </div>
    </section>

    <!-- 浮动 AI 提示词 CTA：覆盖在 hero 底部，打字机效果 -->
    <section class="prompt-cta" @click="onPromptClick">
      <span class="prompt-cta__icon">
        <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
          <path d="M12 1.5l2.4 7.7 7.7 2.4-7.7 2.4-2.4 7.7-2.4-7.7-7.7-2.4 7.7-2.4z"/>
        </svg>
      </span>
      <span class="prompt-cta__text">
        <span class="prompt-cta__placeholder">试试：</span>
        <span class="prompt-cta__typed">{{ typedPrompt }}</span>
        <span class="prompt-cta__caret" />
      </span>
      <span class="prompt-cta__send">
        <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
          <path d="M4 11v2h12l-5.5 5.5L12 20l8-8-8-8-1.5 1.5L16 11z"/>
        </svg>
      </span>
    </section>

    <!-- Bento Grid：错落式入口 -->
    <section class="bento">
      <div class="bento__head">
        <span class="bento__title">开始定制</span>
        <span class="bento__count">5 种创意路径</span>
      </div>
      <div class="bento__grid">
        <button
          v-for="b in bento"
          :key="b.id"
          class="bento-card"
          :class="`bento-card--${b.variant}`"
          @click="go(b.to)"
        >
          <template v-if="b.variant === 'hero'">
            <div class="bento-card__pic" :style="{ backgroundImage: `url(${b.image})` }" />
            <div class="bento-card__overlay">
              <div class="bento-card__label">{{ b.label }}</div>
              <div class="bento-card__sub">{{ b.sub }}</div>
              <div class="bento-card__cta">
                立即开始
                <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                  <path d="M4 11v2h12l-5.5 5.5L12 20l8-8-8-8-1.5 1.5L16 11z"/>
                </svg>
              </div>
            </div>
          </template>
          <template v-else-if="b.variant === 'city'">
            <svg class="bento-card__city-skyline" viewBox="0 0 200 60" preserveAspectRatio="none" aria-hidden="true">
              <defs>
                <linearGradient id="skylineGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stop-color="#ff8a3a" stop-opacity="0.22"/>
                  <stop offset="55%" stop-color="#ff4d6e" stop-opacity="0.22"/>
                  <stop offset="100%" stop-color="#c84bff" stop-opacity="0.22"/>
                </linearGradient>
              </defs>
              <path d="M0 60 L0 38 L8 38 L8 28 L20 28 L20 40 L32 40 L32 18 L44 18 L44 10 L52 10 L52 18 L62 18 L62 32 L74 32 L74 24 L86 24 L86 14 L96 14 L96 24 L108 24 L108 36 L120 36 L120 26 L132 26 L132 38 L144 38 L144 30 L156 30 L156 20 L168 20 L168 32 L180 32 L180 24 L192 24 L192 40 L200 40 L200 60 Z" fill="url(#skylineGrad)"/>
              <circle cx="12" cy="32" r="0.9" fill="#ff4d6e" opacity="0.6"/>
              <circle cx="38" cy="22" r="0.9" fill="#ff8a3a" opacity="0.7"/>
              <circle cx="78" cy="28" r="0.9" fill="#c84bff" opacity="0.6"/>
              <circle cx="100" cy="20" r="0.9" fill="#ff4d6e" opacity="0.6"/>
              <circle cx="138" cy="32" r="0.9" fill="#ff8a3a" opacity="0.7"/>
              <circle cx="172" cy="26" r="0.9" fill="#c84bff" opacity="0.6"/>
            </svg>
            <span class="bento-card__city-pin" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5a2.5 2.5 0 110-5 2.5 2.5 0 010 5z"/>
              </svg>
            </span>
            <div class="bento-card__city-body">
              <div class="bento-card__city-row">
                <span class="bento-card__city-label">AI 城市 IP</span>
                <span class="bento-card__city-chip">NEW</span>
              </div>
              <div class="bento-card__city-sub">{{ b.sub }}</div>
            </div>
          </template>
          <template v-else>
            <img class="bento-card__pic-sm" :src="b.image" :alt="b.label" />
            <div class="bento-card__label bento-card__label--sm">{{ b.label }}</div>
          </template>
        </button>
      </div>
    </section>

    <!-- 新人券：左圆数字 + 右倒计时，新视觉 -->
    <section v-if="newcomerCoupon" class="coupon" @click="onCouponClick">
      <div class="coupon__num">
        <span class="coupon__num-val">{{ couponDiscount }}</span>
        <span class="coupon__num-unit">{{ couponUnit }}</span>
      </div>
      <div class="coupon__divider" />
      <div class="coupon__info">
        <div class="coupon__tag">
          <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path d="M20 6h-2.18c.11-.31.18-.65.18-1 0-1.66-1.34-3-3-3-1.05 0-1.96.54-2.5 1.35l-.5.67-.5-.68C10.96 2.54 10.05 2 9 2 7.34 2 6 3.34 6 5c0 .35.07.69.18 1H4c-1.11 0-1.99.89-1.99 2L2 19c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2zm-5-2c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zM9 4c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm11 15H4v-2h16v2zm0-5H4V8h5.08L7 10.83 8.62 12 11 8.76l1-1.36 1 1.36L15.38 12 17 10.83 14.92 8H20v6z"/>
          </svg>
          新人专享
        </div>
        <div class="coupon__count">
          <Countdown :end-time="couponEndAt" size="sm" />
          <span class="coupon__count-suffix">后失效</span>
        </div>
      </div>
      <div class="coupon__btn">领取</div>
    </section>

    <!-- 用户案例 feed -->
    <section class="section">
      <div class="section__head">
        <h2 class="section__title">看看大家怎么定制的</h2>
        <button class="section__more" @click="go('/gallery')">
          全部
          <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path d="M9.29 6.71c-.39.39-.39 1.02 0 1.41L13.17 12l-3.88 3.88c-.39.39-.39 1.02 0 1.41.39.39 1.02.39 1.41 0l4.59-4.59c.39-.39.39-1.02 0-1.41L10.7 6.7c-.38-.38-1.02-.38-1.41.01z"/>
          </svg>
        </button>
      </div>
      <div class="recommend-grid">
        <button
          v-for="(r, i) in recommend"
          :key="r.id"
          class="recommend-card"
          @click="go('/gallery')"
        >
          <img :src="r.imageUrl" :alt="r.title" />
          <div class="recommend-card__meta">
            <span class="recommend-card__author">@设计师{{ ((i * 37) % 99) + 10 }}</span>
            <span class="recommend-card__use">
              <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
              </svg>
              {{ ((i * 113) % 800) + 99 }}
            </span>
          </div>
        </button>
      </div>
    </section>

    <!-- 内容专区 -->
    <section v-for="t in topics" :key="t.id" class="section">
      <div class="section__head">
        <h2 class="section__title">{{ t.title }}</h2>
        <button class="section__more" @click="go('/gallery')">
          更多
          <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path d="M9.29 6.71c-.39.39-.39 1.02 0 1.41L13.17 12l-3.88 3.88c-.39.39-.39 1.02 0 1.41.39.39 1.02.39 1.41 0l4.59-4.59c.39-.39.39-1.02 0-1.41L10.7 6.7c-.38-.38-1.02-.38-1.41.01z"/>
          </svg>
        </button>
      </div>
      <div class="topic-scroll">
        <button v-for="it in t.items" :key="it.id" class="topic-card" @click="go('/gallery')">
          <img :src="it.imageUrl" :alt="it.title" />
        </button>
      </div>
    </section>

    <div class="footer-tip">已经到底啦 · aitee Demo</div>
  </div>
</template>

<style lang="scss" scoped>
.home {
  min-height: 100vh;
  padding-bottom: calc(#{$tabbar-height} + 16px);
  background:
    radial-gradient(120% 60% at 50% 0%, #ffe1e3 0%, transparent 60%),
    linear-gradient(180deg, #fff7f6 0%, #f6f7fb 280px, #f6f7fb 100%);

  svg {
    width: 1em;
    height: 1em;
    display: inline-block;
    flex-shrink: 0;
  }
}

/* ============== Hero ============== */
.hero {
  position: relative;
  margin: 0 12px;
  height: 240px;
  border-radius: 20px;
  overflow: hidden;
  isolation: isolate;

  &__pic {
    position: absolute;
    inset: 0;
    background-size: cover;
    background-position: center;
    z-index: 1;
  }

  &__mask {
    position: absolute;
    inset: 0;
    background: linear-gradient(110deg, rgba(255, 255, 255, 0.7) 0%, rgba(255, 255, 255, 0.2) 50%, rgba(255, 255, 255, 0) 100%);
    z-index: 2;
  }

  &__body {
    position: relative;
    z-index: 3;
    padding: 28px 20px 0;
    color: #1a1a1a;
  }

  &__eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    font-weight: 600;
    color: $color-primary;
    background: rgba(255, 255, 255, 0.72);
    padding: 4px 10px;
    border-radius: 999px;
    backdrop-filter: blur(6px);
    border: 1px solid rgba(255, 255, 255, 0.8);
  }

  &__dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: $color-primary;
    box-shadow: 0 0 0 3px rgba(255, 77, 79, 0.18);
    animation: heroDotPulse 1.6s ease-in-out infinite;
  }

  &__title {
    margin: 14px 0 6px;
    font-size: 30px;
    font-weight: 900;
    line-height: 1.1;
    letter-spacing: -0.5px;
    color: #111;
  }

  &__line {
    display: block;

    &--accent {
      background: linear-gradient(120deg, #ff4d4f 20%, #ff8a3a 90%);
      -webkit-background-clip: text;
      background-clip: text;
      color: transparent;
    }
  }

  &__desc {
    font-size: 12px;
    color: #4b5563;
    font-weight: 500;
  }
}

@keyframes heroDotPulse {
  0%, 100% { box-shadow: 0 0 0 3px rgba(255, 77, 79, 0.18); }
  50% { box-shadow: 0 0 0 6px rgba(255, 77, 79, 0.05); }
}

/* ============== Prompt CTA ============== */
.prompt-cta {
  margin: -22px 20px 0;
  position: relative;
  z-index: 4;
  display: flex;
  align-items: center;
  height: 52px;
  background: #fff;
  border-radius: 14px;
  padding: 0 6px 0 14px;
  box-shadow: 0 12px 32px rgba(31, 31, 31, 0.12);
  cursor: pointer;
  transition: transform 0.15s ease;

  &:active {
    transform: scale(0.99);
  }

  &__icon {
    width: 28px;
    height: 28px;
    border-radius: 8px;
    background: linear-gradient(135deg, #ff8a3a, #ff4d4f);
    color: #fff;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    flex-shrink: 0;
    margin-right: 8px;
  }

  &__text {
    flex: 1;
    min-width: 0;
    font-size: 13px;
    color: #1f2937;
    overflow: hidden;
    white-space: nowrap;
  }

  &__placeholder {
    color: #9ca3af;
    font-weight: 500;
  }

  &__typed {
    color: #1f2937;
    font-weight: 600;
  }

  &__caret {
    display: inline-block;
    width: 1.5px;
    height: 14px;
    background: $color-primary;
    margin-left: 1px;
    vertical-align: middle;
    transform: translateY(-1px);
    animation: caretBlink 0.9s steps(1, end) infinite;
  }

  &__send {
    width: 40px;
    height: 40px;
    border-radius: 12px;
    background: linear-gradient(135deg, #ff8a3a, #ff4d4f);
    color: #fff;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    flex-shrink: 0;
    box-shadow: 0 4px 10px rgba(255, 77, 79, 0.35);
  }
}

@keyframes caretBlink {
  0%, 50% { opacity: 1; }
  50.01%, 100% { opacity: 0; }
}

/* ============== Bento Grid ============== */
.bento {
  margin: 24px 12px 0;

  &__head {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    padding: 0 4px;
    margin-bottom: 10px;
  }

  &__title {
    font-size: 18px;
    font-weight: 800;
    letter-spacing: -0.3px;
    color: #111;
  }

  &__count {
    font-size: 11px;
    color: $color-text-secondary;
  }

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
  padding: 0;
  background: #fff;
  border: 1px solid rgba(0, 0, 0, 0.04);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
  transition: transform 0.15s ease;

  &:active {
    transform: scale(0.98);
  }

  &--hero {
    grid-column: 1;
    grid-row: 1 / span 2;
  }

  &--city {
    background:
      radial-gradient(80% 100% at 100% 0%, rgba(255, 217, 230, 0.7) 0%, transparent 60%),
      radial-gradient(80% 80% at 0% 100%, rgba(255, 222, 198, 0.7) 0%, transparent 60%),
      linear-gradient(135deg, #fff7ef 0%, #fff0e2 55%, #ffe5ec 100%);
    border: 1px solid rgba(255, 138, 58, 0.16);
  }

  &__city-skyline {
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    width: 100%;
    height: 56px;
    z-index: 1;
    pointer-events: none;
  }

  &__city-pin {
    position: absolute;
    top: 12px;
    right: 12px;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: linear-gradient(135deg, #ff8a3a 0%, #ff4d6e 100%);
    box-shadow:
      0 0 0 3px rgba(255, 138, 58, 0.18),
      0 4px 10px rgba(255, 77, 110, 0.35);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    z-index: 2;

    svg {
      width: 12px;
      height: 12px;
      color: #fff;
    }
  }

  &__city-body {
    position: absolute;
    left: 12px;
    right: 12px;
    bottom: 10px;
    z-index: 3;
    max-width: calc(100% - 24px);
  }

  &__city-row {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: nowrap;
  }

  &__city-label {
    font-size: 14px;
    font-weight: 800;
    line-height: 1.15;
    letter-spacing: -0.2px;
    background: linear-gradient(135deg, #ff7a2a 0%, #ff4d6e 60%, #c84bff 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    -webkit-text-fill-color: transparent;
  }

  &__city-chip {
    flex-shrink: 0;
    background: linear-gradient(135deg, #ff8a3a, #ff4d4f);
    color: #fff;
    font-size: 9px;
    font-weight: 800;
    padding: 2px 6px;
    border-radius: 4px;
    letter-spacing: 0.5px;
    line-height: 1.3;
    box-shadow: 0 2px 5px rgba(255, 77, 79, 0.4);
  }

  &__city-sub {
    margin-top: 2px;
    font-size: 10px;
    color: rgba(50, 30, 40, 0.55);
    line-height: 1.3;
    font-weight: 500;
  }

  &--small {
    background: #fff;
  }

  &__pic {
    position: absolute;
    inset: 0;
    background-size: cover;
    background-position: center;
  }

  &__overlay {
    position: absolute;
    inset: 0;
    padding: 16px;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    align-items: flex-start;
    background: linear-gradient(180deg, rgba(0, 0, 0, 0) 50%, rgba(0, 0, 0, 0.55) 100%);
    color: #fff;
  }

  &__label {
    font-size: 16px;
    font-weight: 800;
    color: #fff;

    &--sm {
      font-size: 12px;
      font-weight: 700;
      color: #1f2937;
      text-align: center;
    }
  }

  &__sub {
    font-size: 11px;
    margin-top: 2px;
    color: rgba(255, 255, 255, 0.85);
    font-weight: 500;
  }

  &__cta {
    margin-top: 10px;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 6px 12px;
    background: rgba(255, 255, 255, 0.96);
    color: #111;
    font-size: 11px;
    font-weight: 700;
    border-radius: 999px;

    svg {
      width: 14px;
      height: 14px;
    }
  }

  &__chip {
    flex-shrink: 0;
    background: linear-gradient(135deg, #ff8a3a, #ff4d4f);
    color: #fff;
    font-size: 9px;
    font-weight: 800;
    padding: 2px 6px;
    border-radius: 4px;
    letter-spacing: 0.5px;
    line-height: 1.3;
    box-shadow: 0 2px 5px rgba(255, 77, 79, 0.4);
  }

  &__pic-sm {
    width: 60px;
    height: 60px;
    object-fit: cover;
    border-radius: 14px;
    display: block;
  }

  &--small {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 0;
    gap: 6px;
  }
}

/* ============== Coupon ============== */
.coupon {
  margin: 16px 12px 0;
  height: 78px;
  display: flex;
  align-items: center;
  padding: 0 16px 0 12px;
  background:
    linear-gradient(95deg, #fff5f1 0%, #fff8f3 60%, #fff 100%),
    #fff;
  border-radius: 16px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(255, 77, 79, 0.08);
  cursor: pointer;

  &::before {
    content: '';
    position: absolute;
    top: -30px;
    right: -30px;
    width: 110px;
    height: 110px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(255, 138, 58, 0.18) 0%, transparent 70%);
  }

  &__num {
    width: 60px;
    height: 60px;
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background:
      radial-gradient(80% 80% at 30% 30%, #ff8a3a 0%, #ff4d4f 100%);
    border-radius: 50%;
    color: #fff;
    box-shadow: 0 6px 14px rgba(255, 77, 79, 0.4);
    line-height: 1;
  }

  &__num-val {
    font-size: 22px;
    font-weight: 900;
    line-height: 1.05;
    letter-spacing: -0.5px;
  }

  &__num-unit {
    margin-top: 1px;
    font-size: 10px;
    font-weight: 700;
    line-height: 1;
    opacity: 0.95;
  }

  &__divider {
    width: 1px;
    height: 40px;
    background: repeating-linear-gradient(
      to bottom,
      rgba(0, 0, 0, 0.12) 0,
      rgba(0, 0, 0, 0.12) 3px,
      transparent 3px,
      transparent 6px
    );
    margin: 0 14px;
    flex-shrink: 0;
  }

  &__info {
    flex: 1;
    min-width: 0;
  }

  &__tag {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 13px;
    font-weight: 800;
    color: #1f2937;

    svg {
      width: 14px;
      height: 14px;
      color: $color-primary;
    }
  }

  &__count {
    margin-top: 4px;
    font-size: 11px;
    color: $color-text-secondary;
    display: flex;
    align-items: center;
    gap: 4px;
  }

  &__count-suffix {
    color: $color-text-secondary;
  }

  &__btn {
    flex-shrink: 0;
    padding: 8px 16px;
    background: #1f2937;
    color: #fff;
    font-size: 12px;
    font-weight: 700;
    border-radius: 999px;
  }
}

/* ============== Section ============== */
.section {
  margin: 24px 12px 0;

  &__head {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    padding: 0 4px;
    margin-bottom: 12px;
  }

  &__title {
    font-size: 18px;
    font-weight: 800;
    letter-spacing: -0.3px;
    color: #111;
  }

  &__more {
    font-size: 12px;
    color: $color-text-secondary;
    display: inline-flex;
    align-items: center;
    gap: 1px;
  }
}

.recommend-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.recommend-card {
  background: #fff;
  border-radius: 14px;
  overflow: hidden;
  padding: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  text-align: left;

  img {
    width: 100%;
    aspect-ratio: 1;
    object-fit: cover;
    display: block;
  }

  &__meta {
    padding: 8px 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 11px;
    color: $color-text-secondary;
  }

  &__author {
    color: #374151;
    font-weight: 600;
  }

  &__use {
    display: inline-flex;
    align-items: center;
    gap: 2px;
    color: $color-primary;
    font-weight: 600;
  }
}

.topic-scroll {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding: 0 4px 4px;
  scrollbar-width: none;

  &::-webkit-scrollbar {
    display: none;
  }
}

.topic-card {
  flex-shrink: 0;
  width: 130px;
  border-radius: 12px;
  overflow: hidden;
  padding: 0;
  background: #fff;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);

  img {
    width: 100%;
    aspect-ratio: 4 / 5;
    object-fit: cover;
    display: block;
  }
}

.footer-tip {
  text-align: center;
  font-size: 11px;
  color: $color-text-placeholder;
  padding: 32px 0 16px;
}
</style>
