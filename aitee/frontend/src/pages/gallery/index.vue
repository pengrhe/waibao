<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast } from 'vant'
import BrandHeader from '@/components/BrandHeader.vue'
import {
  fetchFavoritePatterns,
  fetchPatternCategories,
  fetchPatterns,
  togglePatternFav,
} from '@/api/pattern'
import { lsGet, StorageKeys } from '@/utils/storage'
import type { Pattern, PatternCategory } from '@/types'

const route = useRoute()
const router = useRouter()

const FAV_TAB_ID = 0
const tabs = ref<PatternCategory[]>([{ id: FAV_TAB_ID, name: '收藏', sort: 0 }])
const active = ref<number>(FAV_TAB_ID)
const list = ref<Pattern[]>([])
const favIds = ref<number[]>([])
const loading = ref(false)

async function loadCategories() {
  const cats = await fetchPatternCategories()
  tabs.value = [{ id: FAV_TAB_ID, name: '收藏', sort: 0 }, ...cats]
  const queryCat = Number(route.query.cat)
  if (queryCat && cats.find((c) => c.id === queryCat)) {
    active.value = queryCat
  } else {
    active.value = cats[0]?.id ?? FAV_TAB_ID
  }
}

async function loadPatterns(catId: number) {
  loading.value = true
  try {
    if (catId === FAV_TAB_ID) {
      list.value = await fetchFavoritePatterns()
    } else {
      list.value = await fetchPatterns(catId)
    }
  } finally {
    loading.value = false
  }
}

function refreshFavSet() {
  favIds.value = lsGet<number[]>(StorageKeys.patternFavs, [])
}

async function onTabChange(id: number) {
  active.value = id
  await loadPatterns(id)
}

async function onToggleFav(p: Pattern, e: Event) {
  e.stopPropagation()
  const isFav = await togglePatternFav(p.id)
  refreshFavSet()
  showToast(isFav ? '已收藏' : '已取消收藏')
  if (active.value === FAV_TAB_ID) loadPatterns(FAV_TAB_ID)
}

function onPick(p: Pattern) {
  router.push({ path: '/editor', query: { patternId: p.id } })
}

const columns = computed(() => {
  const cols: Pattern[][] = [[], []]
  list.value.forEach((p, i) => cols[i % 2].push(p))
  return cols
})

onMounted(async () => {
  refreshFavSet()
  await loadCategories()
  await loadPatterns(active.value)
})

watch(
  () => route.query.cat,
  async (v) => {
    const id = Number(v)
    if (id && tabs.value.find((t) => t.id === id) && id !== active.value) {
      onTabChange(id)
    }
  },
)
</script>

<template>
  <div class="gallery">
    <BrandHeader title="印花库" />

    <!-- 顶部分类 tab -->
    <nav class="tabs">
      <button
        v-for="t in tabs"
        :key="t.id"
        class="tabs__item"
        :class="{ 'tabs__item--active': active === t.id }"
        @click="onTabChange(t.id)"
      >
        {{ t.name }}
        <span v-if="active === t.id" class="tabs__indicator" />
      </button>
    </nav>

    <!-- 瀑布流 -->
    <div v-if="loading" class="loading">加载中…</div>
    <div v-else-if="!list.length" class="empty">
      <span class="i-material-symbols:image-search-outline-rounded empty__icon" />
      <p>{{ active === FAV_TAB_ID ? '还没收藏的印花~' : '该分类暂无内容' }}</p>
    </div>
    <div v-else class="waterfall">
      <div v-for="(col, ci) in columns" :key="ci" class="waterfall__col">
        <div
          v-for="p in col"
          :key="p.id"
          class="pattern-card"
          @click="onPick(p)"
        >
          <img :src="p.imageUrl" :alt="p.title" />
          <div class="pattern-card__footer">
            <span class="pattern-card__title text-ellipsis">{{ p.title }}</span>
            <button
              class="pattern-card__fav"
              :class="{ 'pattern-card__fav--on': favIds.includes(p.id) }"
              @click="onToggleFav(p, $event)"
            >
              <span class="i-material-symbols:favorite-outline-rounded" v-if="!favIds.includes(p.id)" />
              <span class="i-material-symbols:favorite-rounded" v-else />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.gallery {
  min-height: 100vh;
  padding-bottom: calc(#{$tabbar-height} + 16px);
  background: $color-bg-page;
}

.tabs {
  display: flex;
  gap: 16px;
  padding: 8px 12px 12px;
  overflow-x: auto;
  background: #fff;
  &::-webkit-scrollbar {
    display: none;
  }

  &__item {
    flex-shrink: 0;
    color: $color-text-secondary;
    font-size: 14px;
    padding: 6px 4px;
    position: relative;
    font-weight: 500;

    &--active {
      color: $color-text-primary;
      font-size: 16px;
      font-weight: 700;
    }
  }

  &__indicator {
    position: absolute;
    bottom: -4px;
    left: 50%;
    transform: translateX(-50%);
    width: 24px;
    height: 3px;
    border-radius: 2px;
    background: $color-primary;
  }
}

.waterfall {
  display: flex;
  gap: 8px;
  padding: 12px;

  &__col {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
}

.pattern-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
  cursor: pointer;
  transition: transform 0.15s;

  &:active {
    transform: scale(0.98);
  }

  img {
    width: 100%;
    aspect-ratio: 1;
    object-fit: cover;
    display: block;
  }

  &__footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 10px;
    gap: 6px;
  }

  &__title {
    flex: 1;
    font-size: 12px;
    color: $color-text-primary;
  }

  &__fav {
    width: 24px;
    height: 24px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: $color-text-placeholder;
    font-size: 18px;

    &--on {
      color: $color-primary;
    }
  }
}

.loading,
.empty {
  padding: 80px 0;
  text-align: center;
  color: $color-text-secondary;
  font-size: 13px;
}

.empty {
  &__icon {
    font-size: 56px;
    color: $color-text-placeholder;
    display: block;
    margin: 0 auto 12px;
  }
}
</style>
