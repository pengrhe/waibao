<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { showDialog, showToast } from 'vant'
import NavBar from '@/components/NavBar.vue'
import { deleteDesign, listDesigns } from '@/api/design'
import { products } from '@/mock/products'
import { tshirtMockup, toteMockup } from '@/utils/placeholder'
import { fmtTime } from '@/utils/format'
import type { Design } from '@/types'

const router = useRouter()
const list = ref<Design[]>([])

function previewOf(d: Design) {
  if (d.previewUrl) return d.previewUrl
  const p = products.find((x) => x.id === d.productId)
  if (p?.type === 'tote') return toteMockup(d.color)
  return tshirtMockup(d.color)
}

function productName(id: number) {
  return products.find((p) => p.id === id)?.name ?? '已下架款式'
}

async function load() {
  list.value = await listDesigns()
}

onMounted(load)

function open(d: Design) {
  router.push(`/editor?designId=${d.id}`)
}

function remove(d: Design, e: Event) {
  e.stopPropagation()
  showDialog({ title: '删除设计？', message: '该操作不可恢复', showCancelButton: true })
    .then(async () => {
      await deleteDesign(d.id)
      load()
      showToast('已删除')
    })
    .catch(() => {})
}

function newDesign() {
  router.push('/editor')
}
</script>

<template>
  <div class="dl">
    <NavBar title="我的设计" />

    <div v-if="!list.length" class="empty">
      <span class="i-material-symbols:design-services-outline-rounded empty__icon" />
      <p>还没有设计稿，去做一个吧</p>
      <button class="btn-primary" @click="newDesign">去设计</button>
    </div>

    <div v-else class="grid">
      <div v-for="d in list" :key="d.id" class="card" @click="open(d)">
        <div class="card__pic">
          <img :src="previewOf(d)" alt="" />
          <span class="card__layers">{{ d.layers.length }} 个图层</span>
        </div>
        <div class="card__name text-ellipsis">{{ productName(d.productId) }}</div>
        <div class="card__meta">
          <span>{{ fmtTime(d.updatedAt) }}</span>
          <button class="card__del" @click="remove(d, $event)">
            <span class="i-material-symbols:delete-outline-rounded" />
          </button>
        </div>
      </div>
    </div>

    <div v-if="list.length" class="bar">
      <button class="btn-primary" @click="newDesign">+ 新建设计</button>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.dl {
  min-height: 100vh;
  background: $color-bg-page;
  padding-bottom: 80px;
}

.empty {
  text-align: center;
  padding: 80px 24px;
  color: $color-text-secondary;
  &__icon {
    font-size: 64px;
    color: $color-text-placeholder;
    display: block;
    margin: 0 auto 12px;
  }
  p {
    margin: 0 0 16px;
  }
}

.grid {
  padding: 12px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);

  &__pic {
    position: relative;
    aspect-ratio: 1;
    background: $color-bg-tag;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }

  &__layers {
    position: absolute;
    top: 6px;
    right: 6px;
    background: rgba(0, 0, 0, 0.5);
    color: #fff;
    font-size: 10px;
    padding: 2px 6px;
    border-radius: 999px;
  }

  &__name {
    padding: 8px 10px 0;
    font-size: 13px;
    font-weight: 600;
  }

  &__meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 4px 10px 8px;
    font-size: 11px;
    color: $color-text-secondary;
  }

  &__del {
    color: $color-text-placeholder;
    font-size: 16px;
  }
}

.bar {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 480px;
  background: #fff;
  padding: 12px 16px;
  border-top: 1px solid $color-divider;
  z-index: 9;

  .btn-primary {
    width: 100%;
    height: 44px;
  }
}
</style>
