<script setup lang="ts">
import { computed, onMounted, ref, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showDialog, showToast } from 'vant'
import NavBar from '@/components/NavBar.vue'
import { cancelOrder, getOrder, pickupOrder } from '@/api/order'
import { fmtPrice, fmtTime, ORDER_STATUS_TEXT, ORDER_STATUS_COLOR } from '@/utils/format'
import type { Order, OrderStatus } from '@/types'

const route = useRoute()
const router = useRouter()

const order = ref<Order | null>(null)
const loading = ref(true)

const timeline = computed(() => {
  if (!order.value) return []
  const all: { key: OrderStatus; label: string; done: boolean; current: boolean }[] = [
    { key: 'pending_pay', label: '提交订单', done: false, current: false },
    { key: 'pending_print', label: '已支付', done: false, current: false },
    { key: 'printing', label: '打印中', done: false, current: false },
    { key: 'pending_pickup', label: '可取件', done: false, current: false },
    { key: 'done', label: '已完成', done: false, current: false },
  ]
  const order2idx: Record<OrderStatus, number> = {
    pending_pay: 0,
    pending_print: 1,
    printing: 2,
    pending_pickup: 3,
    done: 4,
    cancelled: -1,
  }
  const idx = order2idx[order.value.status]
  if (order.value.status === 'cancelled') {
    return [{ key: 'cancelled' as OrderStatus, label: '订单已取消', done: true, current: true }]
  }
  for (let i = 0; i <= idx; i++) all[i].done = true
  if (idx >= 0 && idx < all.length) all[idx].current = true
  return all
})

let pollTimer: ReturnType<typeof setInterval> | null = null

async function load() {
  loading.value = true
  try {
    order.value = (await getOrder(route.params.id as string)) ?? null
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  load()
  if (route.query.paid) {
    showToast({ type: 'success', message: '支付成功' })
  }
  pollTimer = setInterval(load, 3000)
})

onBeforeUnmount(() => {
  if (pollTimer) clearInterval(pollTimer)
})

async function onCancel() {
  if (!order.value) return
  showDialog({ title: '取消订单？', message: '取消后退款将原路返回', showCancelButton: true })
    .then(async () => {
      await cancelOrder(order.value!.id)
      load()
      showToast('已取消')
    })
    .catch(() => {})
}

async function onPickup() {
  if (!order.value) return
  await pickupOrder(order.value.id)
  load()
  showToast({ type: 'success', message: '已确认收货' })
}

function onReorder() {
  if (!order.value) return
  router.push(`/editor?productId=${order.value.items[0]?.productId ?? 1}`)
}
</script>

<template>
  <div class="od">
    <NavBar title="订单详情" />

    <div v-if="loading" class="loading">加载中…</div>
    <template v-else-if="order">
      <!-- 状态横幅 -->
      <section class="banner" :style="{ background: ORDER_STATUS_COLOR[order.status] + '15' }">
        <div class="banner__title" :style="{ color: ORDER_STATUS_COLOR[order.status] }">
          {{ ORDER_STATUS_TEXT[order.status] }}
        </div>
        <div class="banner__sub">
          <template v-if="order.status === 'pending_pay'">请尽快完成支付</template>
          <template v-else-if="order.status === 'pending_print'">支付成功，正在转入车间</template>
          <template v-else-if="order.status === 'printing'">您的设计正在打印</template>
          <template v-else-if="order.status === 'pending_pickup'">已完成打印，可到店取件</template>
          <template v-else-if="order.status === 'done'">订单已完成，欢迎再次定制</template>
          <template v-else-if="order.status === 'cancelled'">订单已取消</template>
        </div>
      </section>

      <!-- 时间线 -->
      <section v-if="order.status !== 'cancelled'" class="timeline">
        <div v-for="(s, i) in timeline" :key="s.key" class="timeline__item">
          <span
            class="timeline__dot"
            :class="{ 'timeline__dot--done': s.done, 'timeline__dot--current': s.current }"
          />
          <span class="timeline__label" :class="{ 'timeline__label--done': s.done }">{{ s.label }}</span>
          <span v-if="i < timeline.length - 1" class="timeline__line" :class="{ 'timeline__line--done': timeline[i + 1].done }" />
        </div>
      </section>

      <!-- 地址 -->
      <section v-if="order.address" class="addr-card">
        <span class="i-material-symbols:location-on-outline-rounded addr-card__icon" />
        <div class="addr-card__body">
          <div class="addr-card__line1">
            <strong>{{ order.address.name }}</strong>
            <span>{{ order.address.phone }}</span>
          </div>
          <div class="addr-card__line2">{{ order.address.region }} {{ order.address.detail }}</div>
        </div>
      </section>

      <!-- 商品 -->
      <section class="goods">
        <div v-for="(it, i) in order.items" :key="i" class="goods__item">
          <img :src="it.previewUrl" />
          <div class="goods__body">
            <div class="goods__name text-ellipsis">{{ it.productName }}</div>
            <div class="goods__sku">{{ it.size }} · 颜色 <span class="dot" :style="{ background: it.color }" /></div>
            <div class="goods__row">
              <span class="goods__price">¥ {{ fmtPrice(it.price) }}</span>
              <span class="goods__qty">x{{ it.qty }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 金额 -->
      <section class="amount">
        <div class="amount__row">
          <span>商品合计</span><span>¥ {{ fmtPrice(order.total) }}</span>
        </div>
        <div class="amount__row">
          <span>优惠</span>
          <span class="discount">-¥ {{ fmtPrice(order.total - order.payAmount) }}</span>
        </div>
        <div class="amount__row amount__row--total">
          <span>实付</span>
          <span class="total">¥ {{ fmtPrice(order.payAmount) }}</span>
        </div>
      </section>

      <!-- 订单信息 -->
      <section class="info">
        <div class="info__row"><span>订单编号</span><span>{{ order.no }}</span></div>
        <div class="info__row"><span>下单时间</span><span>{{ fmtTime(order.createdAt) }}</span></div>
        <div v-if="order.paidAt" class="info__row"><span>支付时间</span><span>{{ fmtTime(order.paidAt) }}</span></div>
      </section>

      <!-- 操作栏 -->
      <div class="bar">
        <template v-if="order.status === 'pending_pay'">
          <button class="bar__ghost" @click="onCancel">取消订单</button>
          <button class="bar__primary" @click="onCancel">立即支付</button>
        </template>
        <template v-else-if="order.status === 'pending_print' || order.status === 'printing'">
          <button class="bar__ghost" :disabled="order.status === 'printing'" @click="onCancel">
            {{ order.status === 'printing' ? '打印中无法取消' : '取消订单' }}
          </button>
          <button class="bar__primary bar__primary--disabled">等待打印</button>
        </template>
        <template v-else-if="order.status === 'pending_pickup'">
          <button class="bar__primary" @click="onPickup">确认收货</button>
        </template>
        <template v-else>
          <button class="bar__ghost" @click="router.push('/order/list')">查看更多</button>
          <button class="bar__primary" @click="onReorder">再来一单</button>
        </template>
      </div>
    </template>
  </div>
</template>

<style lang="scss" scoped>
.od {
  min-height: 100vh;
  background: $color-bg-page;
  padding-bottom: 80px;
}

.loading {
  text-align: center;
  padding: 80px 0;
  color: $color-text-secondary;
}

.banner {
  margin: 12px;
  padding: 18px 20px;
  border-radius: 12px;

  &__title {
    font-size: 18px;
    font-weight: 800;
  }

  &__sub {
    font-size: 12px;
    color: $color-text-secondary;
    margin-top: 4px;
  }
}

.timeline {
  display: flex;
  align-items: flex-start;
  margin: 0 12px 12px;
  background: #fff;
  border-radius: 12px;
  padding: 14px 12px;
  position: relative;

  &__item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    position: relative;
    padding: 0 8px;
  }

  &__dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: $color-bg-tag;
    border: 2px solid $color-bg-tag;
    margin-bottom: 6px;
    z-index: 1;

    &--done {
      background: $color-primary;
      border-color: $color-primary;
    }
    &--current {
      width: 14px;
      height: 14px;
      background: #fff;
      border: 3px solid $color-primary;
      box-shadow: 0 0 0 4px rgba(255, 77, 79, 0.15);
    }
  }

  &__label {
    font-size: 11px;
    color: $color-text-secondary;
    text-align: center;
    &--done {
      color: $color-text-primary;
      font-weight: 600;
    }
  }

  &__line {
    position: absolute;
    top: 5px;
    left: 50%;
    width: 100%;
    height: 2px;
    background: $color-bg-tag;
    z-index: 0;
    &--done {
      background: $color-primary;
    }
  }
}

.addr-card,
.goods,
.amount,
.info {
  background: #fff;
  margin: 12px;
  border-radius: 12px;
  padding: 12px 14px;
}

.addr-card {
  display: flex;
  align-items: center;
  gap: 8px;

  &__icon {
    color: $color-primary;
    font-size: 22px;
  }

  &__body {
    flex: 1;
    min-width: 0;
  }

  &__line1 {
    font-size: 14px;
    display: flex;
    gap: 12px;
  }

  &__line2 {
    font-size: 12px;
    color: $color-text-secondary;
    margin-top: 4px;
  }
}

.goods {
  &__item {
    display: flex;
    gap: 10px;
    padding: 8px 0;
    border-bottom: 1px solid $color-divider;
    align-items: center;
    &:last-child {
      border-bottom: 0;
    }
  }

  img {
    width: 64px;
    height: 64px;
    border-radius: 6px;
    object-fit: cover;
    background: $color-bg-tag;
  }

  &__body {
    flex: 1;
    min-width: 0;
  }

  &__name {
    font-size: 14px;
    font-weight: 600;
  }

  &__sku {
    font-size: 11px;
    color: $color-text-secondary;
    margin: 4px 0;
    display: flex;
    align-items: center;
    gap: 4px;

    .dot {
      width: 12px;
      height: 12px;
      border-radius: 50%;
      border: 1px solid $color-border;
      display: inline-block;
    }
  }

  &__row {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: $color-text-secondary;
  }

  &__price {
    color: $color-primary;
    font-weight: 700;
    font-size: 14px;
  }
}

.amount {
  &__row {
    display: flex;
    justify-content: space-between;
    padding: 4px 0;
    font-size: 13px;
    color: $color-text-secondary;

    &--total {
      border-top: 1px dashed $color-divider;
      padding-top: 12px;
      margin-top: 8px;
      font-size: 14px;
      color: $color-text-primary;
      font-weight: 600;
    }
  }

  .discount {
    color: $color-primary;
  }

  .total {
    color: $color-primary;
    font-size: 18px;
    font-weight: 800;
  }
}

.info {
  &__row {
    display: flex;
    justify-content: space-between;
    padding: 4px 0;
    font-size: 12px;
    color: $color-text-secondary;
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
  height: 60px;
  border-top: 1px solid $color-divider;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  padding: 0 16px;
  z-index: 9;

  &__ghost {
    height: 36px;
    padding: 0 18px;
    border-radius: $radius-pill;
    background: $color-bg-tag;
    color: $color-text-primary;
    font-size: 13px;
    font-weight: 600;

    &:disabled {
      opacity: 0.5;
    }
  }

  &__primary {
    height: 36px;
    padding: 0 22px;
    border-radius: $radius-pill;
    background: $color-primary;
    color: #fff;
    font-size: 13px;
    font-weight: 700;

    &--disabled {
      background: $color-text-placeholder;
    }
  }
}
</style>
