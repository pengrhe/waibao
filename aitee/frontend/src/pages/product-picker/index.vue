<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import NavBar from '@/components/NavBar.vue'
import { fetchProducts } from '@/api/product'
import { useEditorStore } from '@/store/editor'
import type { Product, ProductType } from '@/types'

const router = useRouter()
const editor = useEditorStore()

const products = ref<Product[]>([])
const loading = ref(false)
const activeFilter = ref<'all' | ProductType>('all')
const colorPick = ref<Record<number, string>>({})

const filters: { id: 'all' | ProductType; label: string }[] = [
  { id: 'all', label: '全部' },
  { id: 'tshirt', label: '短袖 T 恤' },
  { id: 'tote', label: '帆布包' },
  { id: 'hoodie', label: '卫衣' },
  { id: 'parent-child', label: '亲子装' },
  { id: 'pet', label: '宠物' },
]

const filtered = computed(() => {
  if (activeFilter.value === 'all') return products.value
  return products.value.filter((p) => p.type === activeFilter.value)
})

onMounted(async () => {
  loading.value = true
  try {
    products.value = await fetchProducts()
    products.value.forEach((p) => {
      colorPick.value[p.id] = p.colors[0]
    })
  } finally {
    loading.value = false
  }
})

function pick(p: Product) {
  editor.setProduct(p.id)
  if (colorPick.value[p.id]) editor.setColor(colorPick.value[p.id])
  showToast({ type: 'success', message: '已切换款式' })
  router.back()
}
</script>

<template>
  <div class="picker">
    <NavBar title="款式选择" />

    <div class="filters">
      <button
        v-for="f in filters"
        :key="f.id"
        class="filters__item"
        :class="{ 'filters__item--active': activeFilter === f.id }"
        @click="activeFilter = f.id"
      >
        {{ f.label }}
      </button>
    </div>

    <div v-if="loading" class="loading">加载中…</div>
    <div v-else class="list">
      <div
        v-for="p in filtered"
        :key="p.id"
        class="card"
        :class="{ 'card--current': p.id === editor.productId }"
      >
        <div class="card__head">
          <span v-if="p.id === editor.productId" class="card__badge">当前选中</span>
          <span class="card__type">{{ filters.find((f) => f.id === p.type)?.label || p.type }}</span>
        </div>
        <div class="card__body">
          <div class="card__visual" :style="{ background: colorPick[p.id] || p.colors[0] }">
            <div class="card__visual-tee" />
          </div>
          <div class="card__info">
            <div class="card__name text-ellipsis">{{ p.name }}</div>
            <div class="card__tags">
              <span v-for="t in p.tags.slice(0, 4)" :key="t" class="card__tag">{{ t }}</span>
            </div>
            <div class="card__color-row">
              <span class="card__color-label">颜色选择</span>
              <span class="card__colors">
                <button
                  v-for="c in p.colors"
                  :key="c"
                  class="card__color"
                  :class="{
                    'card__color--white': c.toUpperCase() === '#FFFFFF',
                    'card__color--active': colorPick[p.id] === c,
                  }"
                  :style="{ background: c }"
                  @click="colorPick[p.id] = c"
                />
              </span>
            </div>
            <div class="card__footer">
              <span class="card__price">¥ {{ p.basePrice }}</span>
              <button class="card__cta" @click="pick(p)">使用此款式</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.picker {
  min-height: 100vh;
  background: $color-bg-page;
  padding-bottom: 24px;
}

.filters {
  display: flex;
  gap: 8px;
  padding: 12px;
  overflow-x: auto;
  background: #fff;
  &::-webkit-scrollbar {
    display: none;
  }

  &__item {
    flex-shrink: 0;
    padding: 6px 14px;
    border-radius: $radius-pill;
    background: $color-bg-tag;
    font-size: 13px;
    color: $color-text-secondary;

    &--active {
      background: $color-primary;
      color: #fff;
      font-weight: 700;
    }
  }
}

.list {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  position: relative;

  &--current {
    border: 1px solid $color-primary;
  }

  &__head {
    display: flex;
    justify-content: space-between;
    padding: 8px 12px 0;
  }

  &__badge {
    font-size: 11px;
    color: $color-primary;
    font-weight: 700;
    background: rgba(255, 77, 79, 0.1);
    padding: 2px 8px;
    border-radius: 999px;
  }

  &__type {
    font-size: 11px;
    color: $color-text-secondary;
    margin-left: auto;
  }

  &__body {
    display: flex;
    gap: 12px;
    padding: 12px;
  }

  &__visual {
    width: 100px;
    height: 120px;
    border-radius: 8px;
    flex-shrink: 0;
    border: 1px solid $color-divider;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
  }

  &__visual-tee {
    width: 70%;
    height: 70%;
    background: rgba(0, 0, 0, 0.06);
    border-radius: 6px;
    clip-path: polygon(20% 8%, 32% 0, 68% 0, 80% 8%, 100% 22%, 90% 36%, 80% 32%, 80% 100%, 20% 100%, 20% 32%, 10% 36%, 0% 22%);
  }

  &__info {
    flex: 1;
    min-width: 0;
  }

  &__name {
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 4px;
  }

  &__tags {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-bottom: 6px;
  }

  &__tag {
    font-size: 10px;
    padding: 2px 6px;
    background: $color-bg-tag;
    color: $color-text-secondary;
    border-radius: 4px;
  }

  &__color-row {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-top: 6px;
  }

  &__color-label {
    font-size: 11px;
    color: $color-text-secondary;
  }

  &__colors {
    display: inline-flex;
    gap: 6px;
    flex-wrap: wrap;
  }

  &__color {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    border: 1px solid rgba(0, 0, 0, 0.1);

    &--white {
      border: 1px solid $color-border;
    }

    &--active {
      box-shadow: 0 0 0 2px #fff, 0 0 0 4px $color-primary;
    }
  }

  &__footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 10px;
  }

  &__price {
    color: $color-primary;
    font-weight: 800;
    font-size: 16px;
  }

  &__cta {
    background: $color-primary;
    color: #fff;
    font-size: 12px;
    font-weight: 700;
    padding: 6px 14px;
    border-radius: $radius-pill;
  }
}

.loading {
  text-align: center;
  color: $color-text-secondary;
  padding: 60px 0;
}
</style>
