<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast } from 'vant'
import NavBar from '@/components/NavBar.vue'
import { fetchCityHints, fetchCityIp, fetchPopularCities, regenCityIp } from '@/api/city'
import type { CityIp, CityIpCategory } from '@/types'

const route = useRoute()
const router = useRouter()

const popular = ref<string[]>([])
const hints = ref<Record<string, string>>({})
const cityInput = ref('')
const currentCity = ref('')
const data = ref<CityIp | null>(null)
const loading = ref(false)
const regenLoading = ref(false)
const regenTip = ref('')

const tabs: { key: CityIpCategory | 'all'; label: string }[] = [
  { key: 'all', label: '全部' },
  { key: 'landmark', label: '地标类' },
  { key: 'folk', label: '民俗类' },
  { key: 'symbol', label: '符号类' },
]
const activeCategory = ref<'all' | CityIpCategory>('all')

const filteredItems = computed(() => {
  if (!data.value) return []
  if (activeCategory.value === 'all') return data.value.items
  return data.value.items.filter((it) => it.category === activeCategory.value)
})

const categoryCount = computed(() => {
  if (!data.value) return { landmark: 0, folk: 0, symbol: 0 }
  return data.value.items.reduce(
    (acc, it) => {
      acc[it.category]++
      return acc
    },
    { landmark: 0, folk: 0, symbol: 0 } as Record<CityIpCategory, number>,
  )
})

async function loadCity(city: string) {
  loading.value = true
  currentCity.value = city
  cityInput.value = city
  try {
    data.value = await fetchCityIp(city)
  } finally {
    loading.value = false
  }
}

async function onRegen() {
  if (!currentCity.value || !data.value) return
  regenLoading.value = true
  regenTip.value = '正在分析本地用户偏好…'
  setTimeout(() => (regenTip.value = '匹配文化元素中…'), 600)
  setTimeout(() => (regenTip.value = '生成中… 已完成 320 / 500'), 1200)
  try {
    data.value = await regenCityIp(currentCity.value, data.value.elements)
    showToast({ type: 'success', message: '已重新生成' })
  } finally {
    regenLoading.value = false
    regenTip.value = ''
  }
}

const newElement = ref('')
function addElement() {
  if (!data.value) return
  const v = newElement.value.trim()
  if (!v) return
  if (data.value.elements.includes(v)) {
    showToast('已存在')
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

function useToEditor(itemId: string) {
  if (!data.value) return
  const item = data.value.items.find((i) => i.id === itemId)
  if (!item) return
  router.push({ path: '/editor', query: { aiUrl: item.imageUrl } })
}

onMounted(async () => {
  const [pop, hin] = await Promise.all([fetchPopularCities(), fetchCityHints()])
  popular.value = pop
  hints.value = hin
  const initCity = (route.query.city as string) || pop[0] || '深圳'
  loadCity(initCity)
})

function onSwitchCity(city: string) {
  if (city === currentCity.value) return
  loadCity(city)
}

function onSearch() {
  const v = cityInput.value.trim()
  if (!v) return showToast('请输入城市名称')
  loadCity(v)
}
</script>

<template>
  <div class="city">
    <NavBar title="AI 城市文化底座" />

    <!-- 城市选择 -->
    <section class="search">
      <div class="search__box">
        <svg class="search__icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
          <path d="M11 2a9 9 0 015.7 16l5 5-1.4 1.4-5-5A9 9 0 1111 2zm0 2a7 7 0 100 14 7 7 0 000-14z"/>
        </svg>
        <input
          v-model="cityInput"
          class="search__input"
          placeholder="输入城市名称，如：深圳 / 佛山 / 厦门"
          @keyup.enter="onSearch"
        />
        <button class="search__btn" @click="onSearch">
          <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path d="M12 1.5l2.4 7.7 7.7 2.4-7.7 2.4-2.4 7.7-2.4-7.7-7.7-2.4 7.7-2.4z"/>
          </svg>
          生成
        </button>
      </div>
      <div class="search__hot">
        <span class="search__hot-label">热门：</span>
        <button
          v-for="c in popular"
          :key="c"
          class="search__chip"
          :class="{ 'search__chip--active': currentCity === c }"
          @click="onSwitchCity(c)"
        >
          {{ c }}
        </button>
      </div>
    </section>

    <!-- 加载占位 -->
    <section v-if="loading" class="loading">
      <div class="loading__bubble">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 1.5l2.4 7.7 7.7 2.4-7.7 2.4-2.4 7.7-2.4-7.7-7.7-2.4 7.7-2.4z"/>
        </svg>
      </div>
      <div class="loading__text">AI 正在抓取「{{ cityInput }}」的城市文化…</div>
    </section>

    <!-- 头图 + 总览 -->
    <template v-else-if="data">
      <section class="hero">
        <div class="hero__row">
          <h1 class="hero__city">{{ data.city }}</h1>
          <span class="hero__hint">{{ hints[data.city] ?? '本地化文化图库' }}</span>
        </div>
        <div class="hero__stat">
          已为你生成 <b>{{ data.totalCount }}</b> 张适配 T 恤的本地化印花图库
        </div>
      </section>

      <!-- 风格权重（本地化适配可视化） -->
      <section class="weights">
        <div class="weights__head">
          <span class="weights__title">本地用户偏好</span>
          <span class="weights__sub">基于历史订单 · 自动调权</span>
        </div>
        <div class="weights__bar">
          <div
            v-for="w in data.styleWeights"
            :key="w.style"
            class="weights__seg"
            :style="{ flex: w.ratio }"
            :data-style="w.style"
          />
        </div>
        <div class="weights__legend">
          <span v-for="w in data.styleWeights" :key="w.style" class="weights__item">
            <span class="weights__dot" :data-style="w.style" />
            {{ w.style }} {{ Math.round(w.ratio * 100) }}%
          </span>
        </div>
      </section>

      <!-- 文化元素增删 -->
      <section class="elements">
        <div class="elements__head">
          <span class="elements__title">文化元素 · {{ data.elements.length }}</span>
          <span class="elements__sub">点击删除 · 下方可添加自定义</span>
        </div>
        <div class="elements__list">
          <button
            v-for="e in data.elements"
            :key="e"
            class="el-chip"
            @click="removeElement(e)"
          >
            {{ e }}
            <svg class="el-chip__close" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            </svg>
          </button>
        </div>
        <div class="elements__add">
          <input
            v-model="newElement"
            class="elements__input"
            placeholder="添加自定义元素，如「春茧体育馆」"
            maxlength="12"
            @keyup.enter="addElement"
          />
          <button class="elements__add-btn" @click="addElement">+ 添加</button>
        </div>
      </section>

      <!-- 重新生成 CTA -->
      <section class="regen">
        <button class="regen__btn" :disabled="regenLoading" @click="onRegen">
          <template v-if="!regenLoading">
            <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
              <path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46A7.93 7.93 0 0020 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74A7.93 7.93 0 004 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z"/>
            </svg>
            根据当前元素重新生成
          </template>
          <template v-else>
            <span class="regen__spinner" />
            {{ regenTip }}
          </template>
        </button>
      </section>

      <!-- 三类 tab + 网格 -->
      <section class="library">
        <nav class="library__tabs">
          <button
            v-for="t in tabs"
            :key="t.key"
            class="library__tab"
            :class="{ 'library__tab--active': activeCategory === t.key }"
            @click="activeCategory = t.key"
          >
            {{ t.label }}
            <span v-if="t.key !== 'all'" class="library__count">{{ categoryCount[t.key as CityIpCategory] }}</span>
            <span v-else class="library__count">{{ data.items.length }}</span>
          </button>
        </nav>
        <div class="library__grid">
          <button
            v-for="it in filteredItems"
            :key="it.id"
            class="card"
            @click="useToEditor(it.id)"
          >
            <img :src="it.imageUrl" :alt="it.title" />
            <div class="card__meta">
              <span class="card__title text-ellipsis">{{ it.title }}</span>
              <span class="card__cat" :data-cat="it.category">
                {{ it.category === 'landmark' ? '地标' : it.category === 'folk' ? '民俗' : '符号' }}
              </span>
            </div>
            <div class="card__use">
              用此图
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M4 11v2h12l-5.5 5.5L12 20l8-8-8-8-1.5 1.5L16 11z"/></svg>
            </div>
          </button>
        </div>
      </section>

      <div class="footer-tip">仅展示 {{ data.items.length }} 张代表，正式版可查看全部 {{ data.totalCount }} 张</div>
    </template>
  </div>
</template>

<style lang="scss" scoped>
.city {
  min-height: 100vh;
  background: $color-bg-page;
  padding-bottom: 32px;

  svg {
    width: 1em;
    height: 1em;
    display: inline-block;
    flex-shrink: 0;
  }
}

/* ============== 搜索 ============== */
.search {
  background: linear-gradient(135deg, #5b6cff 0%, #8a52ff 50%, #ff4d8d 100%);
  padding: 16px 12px 14px;
  color: #fff;

  &__box {
    background: rgba(255, 255, 255, 0.96);
    border-radius: 12px;
    height: 44px;
    display: flex;
    align-items: center;
    padding: 0 4px 0 12px;
    box-shadow: 0 6px 18px rgba(78, 38, 184, 0.25);
  }

  &__icon {
    color: $color-text-secondary;
    font-size: 18px;
    margin-right: 6px;
  }

  &__input {
    flex: 1;
    border: none;
    outline: none;
    background: transparent;
    font-size: 14px;
    color: #1f2937;
    min-width: 0;
  }

  &__btn {
    height: 36px;
    padding: 0 14px;
    background: linear-gradient(135deg, #ff8a3a, #ff4d4f);
    color: #fff;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    flex-shrink: 0;

    svg { font-size: 13px; }
  }

  &__hot {
    margin-top: 12px;
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    align-items: center;
  }

  &__hot-label {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.85);
  }

  &__chip {
    padding: 5px 10px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.18);
    color: #fff;
    font-size: 12px;
    font-weight: 600;

    &--active {
      background: #fff;
      color: #5b6cff;
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
    }
  }
}

/* ============== Loading ============== */
.loading {
  text-align: center;
  padding: 60px 24px;

  &__bubble {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    background: linear-gradient(135deg, #5b6cff, #ff4d8d);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 28px;
    box-shadow: 0 8px 24px rgba(91, 108, 255, 0.32);
    animation: cityPulse 1.4s ease-in-out infinite;
  }

  &__text {
    margin-top: 14px;
    color: $color-text-regular;
    font-size: 13px;
  }
}

@keyframes cityPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

/* ============== Hero ============== */
.hero {
  margin: 12px 12px 0;
  padding: 14px 16px;
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);

  &__row {
    display: flex;
    align-items: baseline;
    gap: 10px;
    flex-wrap: wrap;
  }

  &__city {
    margin: 0;
    font-size: 22px;
    font-weight: 900;
    color: #111;
    letter-spacing: -0.5px;
  }

  &__hint {
    font-size: 12px;
    color: $color-text-secondary;
    background: $color-bg-tag;
    padding: 2px 8px;
    border-radius: 999px;
  }

  &__stat {
    margin-top: 6px;
    font-size: 12px;
    color: $color-text-regular;

    b {
      color: $color-primary;
      font-size: 16px;
      font-weight: 800;
      margin: 0 2px;
    }
  }
}

/* ============== 权重 ============== */
.weights {
  margin: 12px 12px 0;
  padding: 14px 16px;
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);

  &__head {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 10px;
  }

  &__title {
    font-size: 14px;
    font-weight: 800;
    color: #111;
  }

  &__sub {
    font-size: 11px;
    color: $color-text-placeholder;
  }

  &__bar {
    display: flex;
    height: 12px;
    border-radius: 6px;
    overflow: hidden;
    background: $color-bg-tag;
  }

  &__seg {
    height: 100%;

    &[data-style='国潮'] { background: linear-gradient(90deg, #ff4d4f, #ff8a3a); }
    &[data-style='复古'] { background: linear-gradient(90deg, #92400e, #c2410c); }
    &[data-style='极简'] { background: linear-gradient(90deg, #4b5563, #1f2937); }
    &[data-style='卡通'] { background: linear-gradient(90deg, #ff8a3a, #f59e0b); }
    &[data-style='科技未来'] { background: linear-gradient(90deg, #3b82f6, #6366f1); }
    &[data-style='街潮'] { background: linear-gradient(90deg, #db2777, #be185d); }
  }

  &__legend {
    margin-top: 10px;
    display: flex;
    flex-wrap: wrap;
    gap: 10px 14px;
    font-size: 11px;
    color: $color-text-regular;
  }

  &__item {
    display: inline-flex;
    align-items: center;
    gap: 4px;
  }

  &__dot {
    width: 8px;
    height: 8px;
    border-radius: 2px;

    &[data-style='国潮'] { background: #ff4d4f; }
    &[data-style='复古'] { background: #92400e; }
    &[data-style='极简'] { background: #4b5563; }
    &[data-style='卡通'] { background: #ff8a3a; }
    &[data-style='科技未来'] { background: #3b82f6; }
    &[data-style='街潮'] { background: #db2777; }
  }
}

/* ============== 文化元素 ============== */
.elements {
  margin: 12px 12px 0;
  padding: 14px 16px;
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);

  &__head {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 10px;
  }

  &__title {
    font-size: 14px;
    font-weight: 800;
    color: #111;
  }

  &__sub {
    font-size: 11px;
    color: $color-text-placeholder;
  }

  &__list {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }

  &__add {
    margin-top: 12px;
    display: flex;
    gap: 8px;
  }

  &__input {
    flex: 1;
    height: 36px;
    padding: 0 12px;
    border-radius: 999px;
    border: 1px solid $color-divider;
    background: $color-bg-tag;
    font-size: 13px;
    outline: none;

    &:focus {
      background: #fff;
      border-color: $color-primary;
    }
  }

  &__add-btn {
    height: 36px;
    padding: 0 14px;
    border-radius: 999px;
    background: $color-primary;
    color: #fff;
    font-size: 12px;
    font-weight: 700;
    flex-shrink: 0;
  }
}

.el-chip {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 5px 8px 5px 10px;
  background: $color-bg-tag;
  border-radius: 999px;
  font-size: 12px;
  color: #1f2937;
  transition: background 0.15s;

  &__close {
    color: $color-text-placeholder;
    font-size: 12px;
  }

  &:active {
    background: #fee2e2;
    color: $color-primary;

    .el-chip__close { color: $color-primary; }
  }
}

/* ============== 重新生成 ============== */
.regen {
  margin: 12px 12px 0;

  &__btn {
    width: 100%;
    height: 48px;
    background: linear-gradient(135deg, #1f2937, #111);
    color: #fff;
    border-radius: 12px;
    font-size: 14px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    box-shadow: 0 4px 14px rgba(31, 41, 55, 0.25);

    svg { font-size: 16px; }

    &:disabled {
      opacity: 0.85;
    }
  }

  &__spinner {
    width: 14px;
    height: 14px;
    border: 2px solid rgba(255, 255, 255, 0.4);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ============== 图库 tab + 网格 ============== */
.library {
  margin: 16px 0 0;

  &__tabs {
    display: flex;
    gap: 6px;
    overflow-x: auto;
    padding: 0 12px;
    scrollbar-width: none;
    &::-webkit-scrollbar { display: none; }
  }

  &__tab {
    flex-shrink: 0;
    padding: 8px 14px;
    border-radius: 999px;
    background: #fff;
    border: 1px solid $color-divider;
    color: $color-text-regular;
    font-size: 13px;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 4px;

    &--active {
      background: #1f2937;
      color: #fff;
      border-color: transparent;
    }
  }

  &__count {
    font-size: 11px;
    opacity: 0.8;
  }

  &__grid {
    margin-top: 12px;
    padding: 0 12px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }
}

.card {
  position: relative;
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  padding: 0;
  text-align: left;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);

  img {
    width: 100%;
    aspect-ratio: 1;
    object-fit: cover;
    display: block;
  }

  &__meta {
    padding: 8px 10px 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 6px;
  }

  &__title {
    font-size: 12px;
    font-weight: 700;
    color: #1f2937;
    flex: 1;
    min-width: 0;
  }

  &__cat {
    font-size: 10px;
    padding: 2px 5px;
    border-radius: 4px;
    flex-shrink: 0;

    &[data-cat='landmark'] { background: #dbeafe; color: #1e40af; }
    &[data-cat='folk'] { background: #fef3c7; color: #92400e; }
    &[data-cat='symbol'] { background: #fee2e2; color: #991b1b; }
  }

  &__use {
    position: absolute;
    top: 8px;
    right: 8px;
    background: rgba(31, 41, 55, 0.85);
    color: #fff;
    font-size: 10px;
    font-weight: 700;
    padding: 4px 8px;
    border-radius: 999px;
    display: inline-flex;
    align-items: center;
    gap: 2px;
    backdrop-filter: blur(4px);
    opacity: 0;
    transition: opacity 0.2s;

    svg { font-size: 11px; }
  }

  &:active &__use {
    opacity: 1;
  }

  @media (hover: hover) {
    &:hover &__use { opacity: 1; }
  }
}

.footer-tip {
  margin-top: 24px;
  text-align: center;
  font-size: 11px;
  color: $color-text-placeholder;
}

.text-ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
