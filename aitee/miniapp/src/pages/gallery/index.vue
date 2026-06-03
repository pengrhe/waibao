<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import BrandHeader from '../../components/BrandHeader.vue'
import CustomTabBar from '../../components/CustomTabBar.vue'
import { Pattern } from '../../api'

const FAV_TAB_ID = 0

interface Cat { id: number; name: string; sort?: number }
interface PatternItem { id: number; title?: string; name?: string; image_url: string }

const tabs = ref<Cat[]>([{ id: FAV_TAB_ID, name: '收藏' }])
const active = ref<number>(FAV_TAB_ID)
const list = ref<PatternItem[]>([])
const favIds = ref<number[]>([])
const loading = ref(false)

const FAV_STORAGE = 'aitee_pattern_favs'

function readFavs() {
  try {
    const raw = uni.getStorageSync(FAV_STORAGE)
    favIds.value = Array.isArray(raw) ? raw : (raw ? JSON.parse(raw) : [])
  } catch { favIds.value = [] }
}
function writeFavs() {
  try { uni.setStorageSync(FAV_STORAGE, favIds.value) } catch {}
}

async function loadCategories() {
  try {
    const cats: Cat[] = await Pattern.categories()
    tabs.value = [{ id: FAV_TAB_ID, name: '收藏' }, ...cats]
  } catch {}
}

async function loadList(catId: number) {
  loading.value = true
  try {
    if (catId === FAV_TAB_ID) {
      if (!favIds.value.length) { list.value = []; return }
      const all: PatternItem[] = await Pattern.list()
      list.value = all.filter((p) => favIds.value.includes(p.id))
    } else {
      list.value = await Pattern.list(catId)
    }
  } finally { loading.value = false }
}

async function onTabChange(id: number) {
  if (active.value === id) return
  active.value = id
  await loadList(id)
}

function onToggleFav(p: PatternItem, e: any) {
  e?.stopPropagation?.()
  const i = favIds.value.indexOf(p.id)
  if (i >= 0) favIds.value.splice(i, 1)
  else favIds.value.push(p.id)
  writeFavs()
  uni.showToast({ title: i >= 0 ? '已取消收藏' : '已收藏', icon: 'success' })
  if (active.value === FAV_TAB_ID) loadList(FAV_TAB_ID)
}

function onPick(p: PatternItem) {
  uni.navigateTo({
    url: `/pages/editor/index?pattern_id=${p.id}&pattern_url=${encodeURIComponent(p.image_url)}`,
  })
}

// 两列瀑布流
const columns = computed(() => {
  const cols: PatternItem[][] = [[], []]
  list.value.forEach((p, i) => cols[i % 2].push(p))
  return cols
})

onLoad((opt) => {
  if (opt?.cat) {
    const cid = Number(opt.cat)
    if (!Number.isNaN(cid)) active.value = cid
  }
})

onMounted(async () => {
  readFavs()
  await loadCategories()
  // 若 url 指定了 cat 且后端有，使用它，否则默认走第一个非收藏 tab
  if (active.value === FAV_TAB_ID) {
    const first = tabs.value.find((t) => t.id !== FAV_TAB_ID)
    if (first) active.value = first.id
  }
  await loadList(active.value)
})

onShow(() => {
  readFavs()
  try { uni.hideTabBar({ animation: false }) } catch {}
})
</script>

<template>
  <view class="gallery">
    <BrandHeader title="印花库" />

    <!-- 顶部分类 tab -->
    <scroll-view scroll-x class="tabs">
      <view
        v-for="t in tabs"
        :key="t.id"
        class="tabs__item"
        :class="{ on: active === t.id }"
        @click="onTabChange(t.id)"
      >
        <text>{{ t.name }}</text>
        <view v-if="active === t.id" class="tabs__indicator" />
      </view>
    </scroll-view>

    <!-- 瀑布流 -->
    <view v-if="loading" class="loading">加载中…</view>
    <view v-else-if="!list.length" class="empty">
      <text class="empty__icon">🖼️</text>
      <text class="empty__text">{{ active === FAV_TAB_ID ? '还没收藏的印花~' : '该分类暂无内容' }}</text>
    </view>
    <view v-else class="waterfall">
      <view v-for="(col, ci) in columns" :key="ci" class="waterfall__col">
        <view
          v-for="p in col"
          :key="p.id"
          class="pattern-card"
          @click="onPick(p)"
        >
          <image :src="p.image_url" class="pattern-card__img" mode="aspectFill" />
          <view class="pattern-card__footer">
            <text class="pattern-card__title">{{ p.title || p.name }}</text>
            <view
              class="pattern-card__fav"
              :class="{ on: favIds.includes(p.id) }"
              @click.stop="onToggleFav(p, $event)"
            >
              <text>{{ favIds.includes(p.id) ? '♥' : '♡' }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <CustomTabBar current="gallery" />
  </view>
</template>

<style lang="scss" scoped>
.gallery {
  min-height: 100vh;
  padding-bottom: calc(#{$tabbar-height} + 16px);
  background: $color-bg-page;
}

.tabs {
  white-space: nowrap;
  padding: 8px 12px 12px;
  background: #fff;
  border-bottom: 1px solid $color-divider;
}
.tabs__item {
  display: inline-block;
  position: relative;
  color: $color-text-secondary;
  font-size: 14px;
  padding: 6px 4px;
  margin-right: 16px;
  font-weight: 500;
  vertical-align: middle;
  &.on { color: $color-text-primary; font-size: 16px; font-weight: 700; }
}
.tabs__indicator {
  position: absolute;
  bottom: -4px;
  left: 50%;
  margin-left: -12px;
  width: 24px; height: 3px;
  border-radius: 2px;
  background: $color-primary;
}

.waterfall {
  display: flex;
  gap: 8px;
  padding: 12px;
}
.waterfall__col {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.pattern-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 6px rgba(0,0,0,.04);
  &__img { width: 100%; aspect-ratio: 1; }
  &__footer { display: flex; align-items: center; justify-content: space-between; padding: 8px 10px; gap: 6px; }
  &__title { flex: 1; font-size: 12px; color: $color-text-primary; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
  &__fav {
    width: 24px; height: 24px; line-height: 24px; text-align: center;
    color: $color-text-placeholder; font-size: 18px;
    &.on { color: $color-primary; }
  }
}

.loading, .empty {
  padding: 80px 0;
  text-align: center;
  color: $color-text-secondary;
  font-size: 13px;
}
.empty__icon { display: block; font-size: 56px; color: $color-text-placeholder; margin-bottom: 12px; }
.empty__text { display: block; }
</style>
