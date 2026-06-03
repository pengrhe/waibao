<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import NavBar from '@/components/NavBar.vue'
import { listOrders } from '@/api/order'
import { fmtPrice, ORDER_STATUS_TEXT, fmtTime } from '@/utils/format'
import type { Order, OrderStatus } from '@/types'

const route = useRoute()
const router = useRouter()

type FilterKey = 'all' | OrderStatus
const tabs: { key: FilterKey; label: string }[] = [
  { key: 'all', label: '全部' },
  { key: 'pending_pay', label: '待付款' },
  { key: 'pending_print', label: '待打印' },
  { key: 'printing', label: '打印中' },
  { key: 'done', label: '已完成' },
]

const active = ref<FilterKey>('all')
const orders = ref<Order[]>([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    orders.value = await listOrders(active.value)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  const s = route.query.status as FilterKey | undefined
  if (s && tabs.find((t) => t.key === s)) active.value = s
  load()
})

watch(active, load)

function go(o: Order) {
  router.push(`/order/${o.id}`)
}

const computeFirstItemImage = (o: Order) => o.items[0]?.previewUrl
</script>

<template>
  <div class="ol">
    <NavBar title="我的订单" />

    <nav class="tabs">
      <button
        v-for="t in tabs"
        :key="t.key"
        class="tabs__item"
        :class="{ 'tabs__item--active': active === t.key }"
        @click="active = t.key"
      >
        {{ t.label }}
      </button>
    </nav>

    <div v-if="loading" class="loading">加载中…</div>
    <div v-else-if="!orders.length" class="empty">
      <span class="i-material-symbols:receipt-long-outline-rounded empty__icon" />
      <p>暂无订单</p>
      <button class="btn-primary" @click="router.push('/')">去首页选购</button>
    </div>

    <ul v-else class="list">
      <li v-for="o in orders" :key="o.id" class="card" @click="go(o)">
        <div class="card__head">
          <span class="card__no">订单号：{{ o.no }}</span>
          <span class="card__status">{{ ORDER_STATUS_TEXT[o.status] }}</span>
        </div>
        <div class="card__items">
          <img v-for="(it, i) in o.items.slice(0, 3)" :key="i" :src="it.previewUrl" />
          <span v-if="o.items.length > 3" class="card__more">+{{ o.items.length - 3 }}</span>
        </div>
        <div class="card__bottom">
          <span class="card__time">{{ fmtTime(o.createdAt) }}</span>
          <span class="card__price">实付 ¥ {{ fmtPrice(o.payAmount) }}</span>
        </div>
      </li>
    </ul>
  </div>
</template>

<style lang="scss" scoped>
.ol {
  min-height: 100vh;
  background: $color-bg-page;
}

.tabs {
  background: #fff;
  display: flex;
  gap: 4px;
  padding: 8px 12px 12px;

  &__item {
    flex: 1;
    height: 32px;
    border-radius: $radius-pill;
    background: $color-bg-tag;
    font-size: 12px;
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
  padding: 12px 14px;

  &__head {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  &__no {
    font-size: 12px;
    color: $color-text-secondary;
  }

  &__status {
    font-size: 12px;
    color: $color-primary;
    font-weight: 700;
  }

  &__items {
    margin: 10px 0;
    display: flex;
    gap: 8px;
    align-items: center;
  }

  img {
    width: 56px;
    height: 56px;
    border-radius: 6px;
    object-fit: cover;
    background: $color-bg-tag;
  }

  &__more {
    font-size: 12px;
    color: $color-text-secondary;
  }

  &__bottom {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;
    color: $color-text-secondary;
  }

  &__price {
    color: $color-primary;
    font-weight: 700;
    font-size: 14px;
  }
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

.loading {
  text-align: center;
  padding: 60px 0;
  color: $color-text-secondary;
}
</style>
