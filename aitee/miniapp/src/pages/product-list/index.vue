<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import BrandHeader from '../../components/BrandHeader.vue'
import { Product } from '../../api'

interface Sku { id: number; color: string; size: string; price: string | number; stock?: number }
interface ProductItem {
  id: number
  name: string
  subtitle?: string
  base_price: string | number
  main_image_url?: string
  category_id?: number
  category_name?: string
  tags?: string[]
  skus?: Sku[]
}

const products = ref<ProductItem[]>([])
const categories = ref<{ id: number; name: string }[]>([])
const activeFilter = ref<number | 'all'>('all')
const loading = ref(false)
const colorPick = ref<Record<number, string>>({})

async function load() {
  loading.value = true
  try {
    products.value = await Product.list()
    products.value.forEach((p) => {
      const colors = uniqueColors(p)
      if (colors[0]) colorPick.value[p.id] = colors[0]
    })
  } finally { loading.value = false }
}

async function loadCats() {
  try { categories.value = await Product.categories() } catch {}
}

function uniqueColors(p: ProductItem): string[] {
  const set = new Set<string>()
  ;(p.skus || []).forEach((s) => set.add(s.color))
  return Array.from(set)
}

const filtered = computed(() => {
  if (activeFilter.value === 'all') return products.value
  return products.value.filter((p) => p.category_id === activeFilter.value)
})

function colorBg(c: string) {
  if (!c) return '#f5f5f5'
  if (c.startsWith('#')) return c
  const map: Record<string, string> = {
    白: '#ffffff', 白色: '#ffffff',
    黑: '#1f2937', 黑色: '#1f2937',
    灰: '#9ca3af', 灰色: '#9ca3af',
    红: '#ef4444', 红色: '#ef4444',
    粉: '#f9a8d4', 粉色: '#f9a8d4',
    蓝: '#3b82f6', 蓝色: '#3b82f6',
    绿: '#22c55e', 绿色: '#22c55e',
    黄: '#facc15', 黄色: '#facc15',
    橙: '#fb923c', 橙色: '#fb923c',
    紫: '#a855f7', 紫色: '#a855f7',
    棕: '#92400e', 棕色: '#92400e',
    米白: '#f5f1ea', 卡其: '#d4c5a0',
  }
  return map[c] || '#f5f5f5'
}

function isWhiteish(c: string) {
  const bg = colorBg(c).toLowerCase()
  return bg === '#ffffff' || bg === '#fff' || bg === '#f5f1ea'
}

function pick(p: ProductItem) {
  uni.navigateTo({
    url: `/pages/product-detail/index?id=${p.id}${colorPick.value[p.id] ? `&color=${encodeURIComponent(colorPick.value[p.id])}` : ''}`,
  })
}

onMounted(() => {
  load()
  loadCats()
})
</script>

<template>
  <view class="picker">
    <BrandHeader title="款式选择" show-back :show-logo="false" />

    <!-- 分类筛选 -->
    <scroll-view scroll-x class="filters">
      <view
        class="filters__item"
        :class="{ on: activeFilter === 'all' }"
        @click="activeFilter = 'all'"
      >全部</view>
      <view
        v-for="c in categories"
        :key="c.id"
        class="filters__item"
        :class="{ on: activeFilter === c.id }"
        @click="activeFilter = c.id"
      >{{ c.name }}</view>
    </scroll-view>

    <view v-if="loading" class="loading">加载中…</view>
    <view v-else-if="!filtered.length" class="empty">
      <text class="empty__icon">👕</text>
      <text class="empty__text">暂无款式</text>
    </view>
    <view v-else class="list">
      <view v-for="p in filtered" :key="p.id" class="card">
        <view class="card__head">
          <text class="card__type">{{ p.category_name || (categories.find((c) => c.id === p.category_id)?.name) || 'T 恤' }}</text>
        </view>
        <view class="card__body">
          <view class="card__visual" :style="{ background: colorBg(colorPick[p.id]) }">
            <image v-if="p.main_image_url" :src="p.main_image_url" class="card__visual-img" mode="aspectFit" />
            <view v-else class="card__visual-tee" />
          </view>
          <view class="card__info">
            <text class="card__name">{{ p.name }}</text>
            <text v-if="p.subtitle" class="card__sub">{{ p.subtitle }}</text>
            <view v-if="p.tags?.length" class="card__tags">
              <view v-for="t in p.tags.slice(0, 4)" :key="t" class="card__tag">{{ t }}</view>
            </view>
            <view class="card__color-row">
              <text class="card__color-label">颜色</text>
              <view class="card__colors">
                <view
                  v-for="c in uniqueColors(p)"
                  :key="c"
                  class="card__color"
                  :class="{
                    'card__color--white': isWhiteish(c),
                    on: colorPick[p.id] === c,
                  }"
                  :style="{ background: colorBg(c) }"
                  @click.stop="colorPick[p.id] = c"
                />
              </view>
            </view>
            <view class="card__footer">
              <text class="card__price">¥ {{ p.base_price }}</text>
              <view class="card__cta" @click="pick(p)">立即定制</view>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.picker { min-height: 100vh; background: $color-bg-page; padding-bottom: 24px; }

.filters {
  background: #fff;
  padding: 12px;
  white-space: nowrap;
  border-bottom: 1px solid $color-divider;
}
.filters__item {
  display: inline-block;
  padding: 6px 14px;
  border-radius: 999px;
  background: $color-bg-tag;
  font-size: 13px;
  color: $color-text-secondary;
  margin-right: 8px;
  &.on { background: $color-primary; color: #fff; font-weight: 700; }
}

.list { padding: 12px; display: flex; flex-direction: column; gap: 12px; }

.card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,.04);
  &__head { display: flex; justify-content: flex-end; padding: 8px 12px 0; }
  &__type { font-size: 11px; color: $color-text-secondary; }
  &__body { display: flex; gap: 12px; padding: 12px; }
  &__visual {
    width: 100px; height: 120px;
    border-radius: 8px;
    border: 1px solid $color-divider;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    overflow: hidden;
  }
  &__visual-img { width: 90%; height: 90%; }
  &__visual-tee {
    width: 70%; height: 70%;
    background: rgba(0,0,0,.08);
    border-radius: 6px;
  }
  &__info { flex: 1; min-width: 0; }
  &__name { font-size: 14px; font-weight: 600; color: #1f2937; display: block; }
  &__sub { font-size: 11px; color: $color-text-placeholder; display: block; margin-top: 2px; }
  &__tags { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 6px; }
  &__tag { font-size: 10px; padding: 2px 6px; background: $color-bg-tag; color: $color-text-secondary; border-radius: 4px; }
  &__color-row { display: flex; align-items: center; gap: 6px; margin-top: 8px; }
  &__color-label { font-size: 11px; color: $color-text-secondary; }
  &__colors { display: flex; gap: 6px; flex-wrap: wrap; }
  &__color {
    width: 18px; height: 18px; border-radius: 50%;
    border: 1px solid rgba(0,0,0,.1);
    box-sizing: border-box;
    &--white { border-color: $color-border; }
    &.on { box-shadow: 0 0 0 2px #fff, 0 0 0 4px $color-primary; }
  }
  &__footer { display: flex; align-items: center; justify-content: space-between; margin-top: 10px; }
  &__price { color: $color-primary; font-weight: 800; font-size: 16px; }
  &__cta {
    background: $color-primary;
    color: #fff;
    font-size: 12px;
    font-weight: 700;
    padding: 6px 14px;
    border-radius: 999px;
    line-height: 18px;
  }
}

.loading, .empty {
  text-align: center;
  color: $color-text-secondary;
  padding: 60px 0;
}
.empty__icon { display: block; font-size: 56px; margin-bottom: 12px; color: $color-text-placeholder; }
.empty__text { display: block; font-size: 13px; }
</style>
