<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import BrandHeader from '../../components/BrandHeader.vue'
import { CityIp } from '../../api'

interface CityItem {
  id: number
  title: string
  image_url: string
  category: string
}
interface CityData {
  city: string
  description?: string
  items: CityItem[]
  elements: string[]
  total_count: number
}

const popular = ref<string[]>(['深圳', '北京', '上海', '成都', '广州', '杭州', '西安', '厦门'])
const hints = ref<Record<string, string>>({})
const cityInput = ref('深圳')
const currentCity = ref('')
const data = ref<CityData | null>(null)
const loading = ref(false)
const regenLoading = ref(false)
const regenTip = ref('')
const newElement = ref('')

const tabs: { key: string; label: string }[] = [
  { key: 'all', label: '全部' },
  { key: 'landmark', label: '地标类' },
  { key: 'folk', label: '民俗类' },
  { key: 'symbol', label: '符号类' },
]
const activeCategory = ref('all')

const filteredItems = computed(() => {
  if (!data.value) return []
  if (activeCategory.value === 'all') return data.value.items
  return data.value.items.filter((it) => it.category === activeCategory.value)
})

const categoryCount = computed(() => {
  const r: Record<string, number> = { landmark: 0, folk: 0, symbol: 0 }
  ;(data.value?.items || []).forEach((it) => {
    if (r[it.category] !== undefined) r[it.category]++
  })
  return r
})

// 客户端模拟风格权重（M2 mock，M3 由后端 prefs 接口返回）
const styleWeightsMock = computed(() => {
  if (!data.value) return []
  const c = data.value.city
  const code = (c.charCodeAt(0) + (c.charCodeAt(1) || 0)) % 100
  return [
    { style: '国潮', ratio: 0.28 + (code % 7) * 0.01, color: '#ff4d4f' },
    { style: '复古', ratio: 0.22 + (code % 5) * 0.01, color: '#92400e' },
    { style: '极简', ratio: 0.18 + (code % 3) * 0.01, color: '#4b5563' },
    { style: '卡通', ratio: 0.16, color: '#ff8a3a' },
    { style: '科技未来', ratio: 0.10, color: '#3b82f6' },
    { style: '街潮', ratio: 0.06, color: '#db2777' },
  ]
})

async function loadCity(city: string) {
  loading.value = true
  currentCity.value = city
  cityInput.value = city
  try {
    data.value = await CityIp.detail(city)
  } catch {
    uni.showToast({ title: `暂无 ${city} 数据，请联系后台`, icon: 'none' })
    data.value = null
  } finally {
    loading.value = false
  }
}

async function onRegen() {
  if (!currentCity.value || !data.value) return
  regenLoading.value = true
  regenTip.value = '正在分析本地用户偏好…'
  setTimeout(() => { if (regenLoading.value) regenTip.value = '匹配文化元素中…' }, 600)
  setTimeout(() => { if (regenLoading.value) regenTip.value = '生成中… 已完成 320 / 500' }, 1200)
  try {
    data.value = await CityIp.regen(currentCity.value, data.value.elements)
    uni.showToast({ title: '已重新生成', icon: 'success' })
  } finally {
    regenLoading.value = false
    regenTip.value = ''
  }
}

function addElement() {
  if (!data.value) return
  const v = newElement.value.trim()
  if (!v) return
  if (data.value.elements.includes(v)) {
    uni.showToast({ title: '已存在', icon: 'none' })
    return
  }
  data.value.elements.push(v)
  newElement.value = ''
}

function removeElement(name: string) {
  if (!data.value) return
  const i = data.value.elements.indexOf(name)
  if (i >= 0) data.value.elements.splice(i, 1)
}

function useToEditor(it: CityItem) {
  uni.navigateTo({ url: `/pages/editor/index?pattern_url=${encodeURIComponent(it.image_url)}` })
}

function onSwitchCity(city: string) {
  if (city === currentCity.value) return
  loadCity(city)
}

function onSearch() {
  const v = cityInput.value.trim()
  if (!v) { uni.showToast({ title: '请输入城市名称', icon: 'none' }); return }
  loadCity(v)
}

onLoad((opt) => {
  if (opt?.city) {
    loadCity(decodeURIComponent(String(opt.city)))
  } else {
    loadCity('深圳')
  }
})

onMounted(async () => {
  try {
    const p = await CityIp.popular()
    if (p?.length) popular.value = p
  } catch {}
  try { hints.value = await CityIp.hints() } catch {}
})

function catLabel(cat: string) {
  if (cat === 'landmark') return '地标'
  if (cat === 'folk') return '民俗'
  return '符号'
}
</script>

<template>
  <view class="city">
    <BrandHeader title="AI 城市文化底座" show-back :show-logo="false" />

    <!-- 紫色渐变搜索区 -->
    <view class="search">
      <view class="search__box">
        <text class="search__icon">🔍</text>
        <input
          v-model="cityInput"
          class="search__input"
          placeholder="输入城市名称，如：深圳 / 佛山 / 厦门"
          confirm-type="search"
          @confirm="onSearch"
        />
        <view class="search__btn" @click="onSearch">
          <text>✦ 生成</text>
        </view>
      </view>
      <view class="search__hot">
        <text class="search__hot-label">热门：</text>
        <view
          v-for="c in popular"
          :key="c"
          class="search__chip"
          :class="{ on: currentCity === c }"
          @click="onSwitchCity(c)"
        >{{ c }}</view>
      </view>
    </view>

    <!-- 加载 -->
    <view v-if="loading" class="loading">
      <view class="loading__bubble"><text>✦</text></view>
      <text class="loading__text">AI 正在抓取「{{ cityInput }}」的城市文化…</text>
    </view>

    <template v-else-if="data">
      <!-- Hero 卡片 -->
      <view class="hero">
        <view class="hero__row">
          <text class="hero__city">{{ data.city }}</text>
          <text class="hero__hint">{{ hints[data.city] || data.description || '本地化文化图库' }}</text>
        </view>
        <view class="hero__stat">
          <text>已为你生成 </text>
          <text class="hero__stat-num">{{ data.total_count || data.items.length }}</text>
          <text> 张适配 T 恤的本地化印花图库</text>
        </view>
      </view>

      <!-- 风格权重 -->
      <view class="weights">
        <view class="weights__head">
          <text class="weights__title">本地用户偏好</text>
          <text class="weights__sub">基于历史订单 · 自动调权</text>
        </view>
        <view class="weights__bar">
          <view
            v-for="w in styleWeightsMock"
            :key="w.style"
            class="weights__seg"
            :style="{ flex: w.ratio, background: w.color }"
          />
        </view>
        <view class="weights__legend">
          <view v-for="w in styleWeightsMock" :key="w.style" class="weights__item">
            <view class="weights__dot" :style="{ background: w.color }" />
            <text>{{ w.style }} {{ Math.round(w.ratio * 100) }}%</text>
          </view>
        </view>
      </view>

      <!-- 文化元素 chip -->
      <view class="elements">
        <view class="elements__head">
          <text class="elements__title">文化元素 · {{ data.elements.length }}</text>
          <text class="elements__sub">点击删除 · 下方可添加自定义</text>
        </view>
        <view class="elements__list">
          <view
            v-for="e in data.elements"
            :key="e"
            class="el-chip"
            @click="removeElement(e)"
          >
            <text>{{ e }}</text>
            <text class="el-chip__close">✕</text>
          </view>
        </view>
        <view class="elements__add">
          <input
            v-model="newElement"
            class="elements__input"
            placeholder="添加自定义元素，如「春茧体育馆」"
            maxlength="12"
            @confirm="addElement"
          />
          <view class="elements__add-btn" @click="addElement">+ 添加</view>
        </view>
      </view>

      <!-- 重新生成 CTA -->
      <view class="regen">
        <view class="regen__btn" :class="{ 'regen__btn--loading': regenLoading }" @click="!regenLoading && onRegen()">
          <template v-if="!regenLoading">
            <text class="regen__icon">↻</text>
            <text>根据当前元素重新生成</text>
          </template>
          <template v-else>
            <view class="regen__spinner" />
            <text>{{ regenTip }}</text>
          </template>
        </view>
      </view>

      <!-- 三类 tab + 网格 -->
      <view class="library">
        <scroll-view scroll-x class="library__tabs">
          <view
            v-for="t in tabs"
            :key="t.key"
            class="library__tab"
            :class="{ on: activeCategory === t.key }"
            @click="activeCategory = t.key"
          >
            <text>{{ t.label }}</text>
            <text class="library__count">{{ t.key === 'all' ? data.items.length : (categoryCount[t.key] || 0) }}</text>
          </view>
        </scroll-view>
        <view class="library__grid">
          <view v-for="it in filteredItems" :key="it.id" class="ip-card" @click="useToEditor(it)">
            <image :src="it.image_url" class="ip-card__img" mode="aspectFill" />
            <view class="ip-card__meta">
              <text class="ip-card__title">{{ it.title }}</text>
              <text class="ip-card__cat" :class="`ip-card__cat--${it.category}`">{{ catLabel(it.category) }}</text>
            </view>
            <view class="ip-card__use">
              <text>用此图 →</text>
            </view>
          </view>
        </view>
      </view>

      <view class="footer-tip">仅展示 {{ data.items.length }} 张代表，正式版可查看全部 {{ data.total_count || data.items.length }} 张</view>
    </template>
  </view>
</template>

<style lang="scss" scoped>
.city { min-height: 100vh; background: $color-bg-page; padding-bottom: 32px; }

/* ============== 搜索 ============== */
.search {
  background: linear-gradient(135deg, #5b6cff 0%, #8a52ff 50%, #ff4d8d 100%);
  padding: 16px 12px 14px;
  &__box {
    background: rgba(255,255,255,.96);
    border-radius: 12px;
    height: 44px;
    display: flex; align-items: center;
    padding: 0 4px 0 12px;
    box-shadow: 0 6px 18px rgba(78,38,184,.25);
  }
  &__icon { color: $color-text-secondary; font-size: 16px; margin-right: 6px; }
  &__input {
    flex: 1; background: transparent; font-size: 14px; color: #1f2937; min-width: 0; padding: 0; border: 0;
  }
  &__btn {
    height: 36px; padding: 0 14px;
    background: linear-gradient(135deg, #ff8a3a, #ff4d4f);
    color: #fff; border-radius: 999px;
    font-size: 13px; font-weight: 700;
    display: inline-flex; align-items: center; gap: 4px;
    line-height: 36px;
  }
  &__hot {
    margin-top: 12px;
    display: flex; flex-wrap: wrap; gap: 6px; align-items: center;
  }
  &__hot-label { font-size: 12px; color: rgba(255,255,255,.85); }
  &__chip {
    padding: 5px 12px; border-radius: 999px;
    background: rgba(255,255,255,.18); color: #fff;
    font-size: 12px; font-weight: 600;
    &.on { background: #fff; color: #5b6cff; box-shadow: 0 2px 6px rgba(0,0,0,.15); }
  }
}

/* ============== Loading ============== */
.loading {
  text-align: center; padding: 60px 24px;
  &__bubble {
    width: 64px; height: 64px; border-radius: 50%;
    background: linear-gradient(135deg, #5b6cff, #ff4d8d);
    display: inline-flex; align-items: center; justify-content: center;
    box-shadow: 0 8px 24px rgba(91,108,255,.32);
    animation: cityPulse 1.4s ease-in-out infinite;
    text { color: #fff; font-size: 28px; font-weight: 800; line-height: 1; }
  }
  &__text { display: block; margin-top: 14px; color: $color-text-regular; font-size: 13px; }
}
@keyframes cityPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

/* ============== Hero 卡片 ============== */
.hero {
  margin: 12px 12px 0;
  padding: 14px 16px;
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 2px 8px rgba(0,0,0,.04);
  &__row { display: flex; align-items: baseline; flex-wrap: wrap; gap: 10px; }
  &__city { font-size: 22px; font-weight: 900; color: #111; letter-spacing: -0.5px; }
  &__hint { font-size: 11px; color: $color-text-secondary; background: $color-bg-tag; padding: 2px 8px; border-radius: 999px; }
  &__stat { margin-top: 6px; font-size: 12px; color: $color-text-regular; }
  &__stat-num { color: $color-primary; font-size: 16px; font-weight: 800; margin: 0 2px; }
}

/* ============== 权重 ============== */
.weights {
  margin: 12px 12px 0;
  padding: 14px 16px;
  background: #fff; border-radius: 14px;
  box-shadow: 0 2px 8px rgba(0,0,0,.04);
  &__head { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 10px; }
  &__title { font-size: 14px; font-weight: 800; color: #111; }
  &__sub { font-size: 11px; color: $color-text-placeholder; }
  &__bar { display: flex; height: 12px; border-radius: 6px; overflow: hidden; background: $color-bg-tag; }
  &__seg { height: 100%; }
  &__legend { margin-top: 10px; display: flex; flex-wrap: wrap; gap: 10px 14px; font-size: 11px; color: $color-text-regular; }
  &__item { display: inline-flex; align-items: center; gap: 4px; }
  &__dot { width: 8px; height: 8px; border-radius: 2px; }
}

/* ============== 文化元素 ============== */
.elements {
  margin: 12px 12px 0;
  padding: 14px 16px;
  background: #fff; border-radius: 14px;
  box-shadow: 0 2px 8px rgba(0,0,0,.04);
  &__head { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 10px; }
  &__title { font-size: 14px; font-weight: 800; color: #111; }
  &__sub { font-size: 11px; color: $color-text-placeholder; }
  &__list { display: flex; flex-wrap: wrap; gap: 6px; }
  &__add { margin-top: 12px; display: flex; gap: 8px; }
  &__input {
    flex: 1; height: 36px; padding: 0 12px;
    border-radius: 999px;
    border: 1px solid $color-divider;
    background: $color-bg-tag;
    font-size: 13px;
  }
  &__add-btn {
    height: 36px; padding: 0 14px;
    border-radius: 999px;
    background: $color-primary; color: #fff;
    font-size: 12px; font-weight: 700;
    line-height: 36px;
  }
}
.el-chip {
  display: inline-flex; align-items: center; gap: 3px;
  padding: 5px 8px 5px 10px;
  background: $color-bg-tag;
  border-radius: 999px;
  font-size: 12px; color: #1f2937;
  &__close { color: $color-text-placeholder; font-size: 11px; margin-left: 2px; }
}

/* ============== 重新生成 ============== */
.regen { margin: 12px 12px 0; }
.regen__btn {
  height: 48px;
  background: linear-gradient(135deg, #1f2937, #111);
  color: #fff;
  border-radius: 12px;
  font-size: 14px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  gap: 6px;
  box-shadow: 0 4px 14px rgba(31,41,55,.25);
  &--loading { opacity: .9; }
}
.regen__icon { font-size: 16px; line-height: 1; }
.regen__spinner {
  width: 14px; height: 14px;
  border: 2px solid rgba(255,255,255,.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin .8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ============== 图库 ============== */
.library { margin: 16px 0 0; }
.library__tabs { white-space: nowrap; padding: 0 12px; }
.library__tab {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 8px 14px;
  border-radius: 999px;
  background: #fff;
  border: 1px solid $color-divider;
  color: $color-text-regular;
  font-size: 13px; font-weight: 600;
  margin-right: 6px;
  &.on { background: #1f2937; color: #fff; border-color: transparent; }
}
.library__count { font-size: 11px; opacity: .8; }
.library__grid {
  margin-top: 12px; padding: 0 12px;
  display: grid; grid-template-columns: 1fr 1fr; gap: 10px;
}

.ip-card {
  position: relative;
  background: #fff; border-radius: 12px; overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,.04);
  &__img { width: 100%; aspect-ratio: 1; }
  &__meta { padding: 8px 10px 12px; display: flex; align-items: center; justify-content: space-between; gap: 6px; }
  &__title { font-size: 12px; font-weight: 700; color: #1f2937; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  &__cat {
    font-size: 10px; padding: 2px 5px; border-radius: 4px; flex-shrink: 0;
    &--landmark { background: #dbeafe; color: #1e40af; }
    &--folk { background: #fef3c7; color: #92400e; }
    &--symbol { background: #fee2e2; color: #991b1b; }
  }
  &__use {
    position: absolute; top: 8px; right: 8px;
    background: rgba(31,41,55,.85); color: #fff;
    font-size: 10px; font-weight: 700;
    padding: 4px 8px;
    border-radius: 999px;
  }
}

.footer-tip {
  margin-top: 24px;
  text-align: center;
  font-size: 11px;
  color: $color-text-placeholder;
}
</style>
