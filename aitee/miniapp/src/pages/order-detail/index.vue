<script setup lang="ts">
import { computed, onMounted, ref, onBeforeUnmount } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import BrandHeader from '../../components/BrandHeader.vue'
import { Order, Address } from '../../api'
import { fmtPrice, fmtTime, ORDER_STATUS_TEXT, ORDER_STATUS_COLOR } from '../../utils/format'
import { mockPay } from '../../utils/platform'

const order = ref<any | null>(null)
const addr = ref<any | null>(null)
const loading = ref(true)
const orderId = ref<number>(0)

const timeline = computed(() => {
  if (!order.value) return []
  const all = [
    { key: 'pending_pay', label: '提交订单', done: false, current: false },
    { key: 'pending_print', label: '已支付', done: false, current: false },
    { key: 'printing', label: '打印中', done: false, current: false },
    { key: 'printed', label: '可取件', done: false, current: false },
    { key: 'completed', label: '已完成', done: false, current: false },
  ]
  const map: Record<string, number> = {
    pending_pay: 0, paid: 1, pending_print: 1,
    printing: 2, printed: 3, pending_pickup: 3,
    completed: 4, done: 4, canceled: -1, cancelled: -1, refunded: -1,
  }
  const idx = map[order.value.status] ?? -1
  if (idx === -1) {
    return [{ key: 'canceled', label: '订单已取消', done: true, current: true }]
  }
  for (let i = 0; i <= idx; i++) all[i].done = true
  if (idx >= 0 && idx < all.length) all[idx].current = true
  return all
})

let pollTimer: any = null

async function load() {
  loading.value = true
  try {
    order.value = await Order.detail(orderId.value)
    if (order.value?.address_id) {
      try {
        const list = await Address.list()
        addr.value = list.find((a: any) => a.id === order.value.address_id) || null
      } catch {}
    }
  } finally { loading.value = false }
}

onLoad((opt) => {
  orderId.value = Number(opt?.id || 0)
})

onMounted(() => {
  load()
  pollTimer = setInterval(load, 4000)
})

onBeforeUnmount(() => {
  if (pollTimer) clearInterval(pollTimer)
})

async function onPay() {
  if (!order.value) return
  uni.showLoading({ title: '正在支付...', mask: true })
  const ok = await mockPay(order.value.order_no || `ORD${order.value.id}`)
  uni.hideLoading()
  if (ok) {
    uni.showToast({ title: '支付成功', icon: 'success' })
    load()
  } else {
    uni.showToast({ title: '支付失败', icon: 'none' })
  }
}

async function onCancel() {
  if (!order.value) return
  uni.showModal({
    title: '取消订单？',
    content: '取消后退款将原路返回',
    success: async (r) => {
      if (r.confirm) {
        await Order.cancel(order.value!.id)
        uni.showToast({ title: '已取消', icon: 'success' })
        load()
      }
    }
  })
}

async function onPickup() {
  if (!order.value) return
  await Order.pickup(order.value.id)
  uni.showToast({ title: '已确认收货', icon: 'success' })
  load()
}

function onReorder() {
  if (!order.value) return
  const pid = order.value.items?.[0]?.product_id
  uni.navigateTo({ url: `/pages/editor/index${pid ? `?product_id=${pid}` : ''}` })
}

function gotoOrders() {
  uni.redirectTo({ url: '/pages/orders/index' })
}

function discountAmount(o: any) {
  return Number(o.amount_discount || 0)
}
</script>

<template>
  <view class="od">
    <BrandHeader title="订单详情" show-back :show-logo="false" />

    <view v-if="loading" class="loading">加载中…</view>
    <template v-else-if="order">
      <!-- 状态横幅 -->
      <view class="banner" :style="{ background: (ORDER_STATUS_COLOR[order.status] || '#FF4D4F') + '15' }">
        <text class="banner__title" :style="{ color: ORDER_STATUS_COLOR[order.status] || '#FF4D4F' }">
          {{ ORDER_STATUS_TEXT[order.status] || order.status }}
        </text>
        <text class="banner__sub">
          <template v-if="order.status === 'pending_pay'">请尽快完成支付</template>
          <template v-else-if="order.status === 'pending_print' || order.status === 'paid'">支付成功，正在转入车间</template>
          <template v-else-if="order.status === 'printing'">您的设计正在打印</template>
          <template v-else-if="order.status === 'printed' || order.status === 'pending_pickup'">已完成打印，可到店取件</template>
          <template v-else-if="order.status === 'completed' || order.status === 'done'">订单已完成，欢迎再次定制</template>
          <template v-else-if="order.status === 'canceled' || order.status === 'cancelled'">订单已取消</template>
        </text>
      </view>

      <!-- 时间线 -->
      <view v-if="order.status !== 'canceled' && order.status !== 'cancelled'" class="timeline">
        <view v-for="(s, i) in timeline" :key="s.key" class="timeline__item">
          <view
            class="timeline__dot"
            :class="{
              'timeline__dot--done': s.done,
              'timeline__dot--current': s.current
            }"
          />
          <text class="timeline__label" :class="{ 'timeline__label--done': s.done }">{{ s.label }}</text>
          <view
            v-if="i < timeline.length - 1"
            class="timeline__line"
            :class="{ 'timeline__line--done': timeline[i + 1].done }"
          />
        </view>
      </view>

      <!-- 地址 -->
      <view v-if="addr" class="addr-card">
        <text class="addr-card__icon">📍</text>
        <view class="addr-card__body">
          <view class="addr-card__line1">
            <text class="addr-card__name">{{ addr.receiver }}</text>
            <text class="addr-card__phone">{{ addr.phone }}</text>
          </view>
          <text class="addr-card__line2">{{ addr.province }}{{ addr.city }}{{ addr.district }} {{ addr.detail }}</text>
        </view>
      </view>

      <!-- 商品 -->
      <view class="goods">
        <view v-for="(it, i) in order.items" :key="i" class="goods__item">
          <image
            v-if="it.preview_url"
            :src="it.preview_url"
            mode="aspectFill"
            class="goods__img"
          />
          <view v-else class="goods__img goods__img--ph">👕</view>
          <view class="goods__body">
            <text class="goods__name">{{ it.name_snapshot }}</text>
            <view class="goods__sku">
              <text>{{ it.size_snapshot || '' }}</text>
              <text v-if="it.color_snapshot"> · {{ it.color_snapshot }}</text>
            </view>
            <view class="goods__row">
              <text class="goods__price">¥ {{ fmtPrice(it.unit_price) }}</text>
              <text class="goods__qty">x{{ it.qty }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 金额 -->
      <view class="amount">
        <view class="amount__row">
          <text>商品合计</text>
          <text>¥ {{ fmtPrice(order.amount_goods) }}</text>
        </view>
        <view class="amount__row" v-if="Number(order.amount_shipping) > 0">
          <text>运费</text>
          <text>¥ {{ fmtPrice(order.amount_shipping) }}</text>
        </view>
        <view class="amount__row">
          <text>优惠</text>
          <text class="discount">-¥ {{ fmtPrice(discountAmount(order)) }}</text>
        </view>
        <view class="amount__row amount__row--total">
          <text>实付</text>
          <text class="total">¥ {{ fmtPrice(order.amount_total) }}</text>
        </view>
      </view>

      <!-- 订单信息 -->
      <view class="info">
        <view class="info__row"><text>订单编号</text><text>{{ order.order_no }}</text></view>
        <view class="info__row"><text>下单时间</text><text>{{ fmtTime(order.created_at) }}</text></view>
        <view v-if="order.paid_at" class="info__row"><text>支付时间</text><text>{{ fmtTime(order.paid_at) }}</text></view>
        <view v-if="order.delivery_type" class="info__row"><text>配送方式</text><text>{{ order.delivery_type === 'express' ? '快递配送' : '门店自提' }}</text></view>
      </view>

      <!-- 操作栏 -->
      <view class="bar">
        <template v-if="order.status === 'pending_pay'">
          <view class="bar__ghost" @click="onCancel">取消订单</view>
          <view class="bar__primary" @click="onPay">立即支付</view>
        </template>
        <template v-else-if="order.status === 'pending_print' || order.status === 'paid' || order.status === 'printing'">
          <view class="bar__ghost" :class="{ 'bar__ghost--dis': order.status === 'printing' }" @click="order.status !== 'printing' && onCancel()">
            {{ order.status === 'printing' ? '打印中无法取消' : '取消订单' }}
          </view>
          <view class="bar__primary bar__primary--dis">等待打印</view>
        </template>
        <template v-else-if="order.status === 'printed' || order.status === 'pending_pickup'">
          <view class="bar__primary" @click="onPickup">确认收货</view>
        </template>
        <template v-else>
          <view class="bar__ghost" @click="gotoOrders">查看更多</view>
          <view class="bar__primary" @click="onReorder">再来一单</view>
        </template>
      </view>
    </template>
  </view>
</template>

<style lang="scss" scoped>
.od { min-height: 100vh; background: $color-bg-page; padding-bottom: 80px; }
.loading { text-align: center; padding: 80px 0; color: $color-text-secondary; }

.banner {
  margin: 12px;
  padding: 18px 20px;
  border-radius: 12px;
  &__title { display: block; font-size: 18px; font-weight: 800; }
  &__sub { display: block; font-size: 12px; color: $color-text-secondary; margin-top: 4px; }
}

.timeline {
  display: flex;
  margin: 0 12px 12px;
  background: #fff;
  border-radius: 12px;
  padding: 14px 12px;
  &__item {
    flex: 1;
    display: flex; flex-direction: column; align-items: center;
    position: relative;
    padding: 0 8px;
  }
  &__dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    background: $color-bg-tag;
    border: 2px solid $color-bg-tag;
    margin-bottom: 6px;
    z-index: 1;
    &--done { background: $color-primary; border-color: $color-primary; }
    &--current {
      width: 14px; height: 14px;
      background: #fff;
      border: 3px solid $color-primary;
      box-shadow: 0 0 0 4px rgba(255,77,79,.15);
    }
  }
  &__label { font-size: 11px; color: $color-text-secondary; text-align: center;
    &--done { color: $color-text-primary; font-weight: 600; }
  }
  &__line {
    position: absolute;
    top: 5px;
    left: 50%;
    width: 100%;
    height: 2px;
    background: $color-bg-tag;
    z-index: 0;
    &--done { background: $color-primary; }
  }
}

.addr-card, .goods, .amount, .info {
  background: #fff;
  margin: 12px;
  border-radius: 12px;
  padding: 12px 14px;
}

.addr-card { display: flex; align-items: center; gap: 8px;
  &__icon { color: $color-primary; font-size: 22px; }
  &__body { flex: 1; min-width: 0; }
  &__line1 { font-size: 14px; display: flex; gap: 12px; align-items: center; }
  &__name { font-weight: 700; }
  &__phone { color: $color-text-secondary; font-size: 13px; }
  &__line2 { display: block; font-size: 12px; color: $color-text-secondary; margin-top: 4px; }
}

.goods {
  &__item {
    display: flex; gap: 10px;
    padding: 8px 0;
    border-bottom: 1px solid $color-divider;
    align-items: center;
    &:last-child { border-bottom: 0; }
  }
  &__img { width: 64px; height: 64px; border-radius: 6px; background: $color-bg-tag; }
  &__img--ph { text-align: center; line-height: 64px; font-size: 28px; }
  &__body { flex: 1; min-width: 0; }
  &__name { display: block; font-size: 14px; font-weight: 600; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
  &__sku { display: block; font-size: 11px; color: $color-text-secondary; margin: 4px 0; }
  &__row { display: flex; justify-content: space-between; font-size: 12px; color: $color-text-secondary; }
  &__price { color: $color-primary; font-weight: 700; font-size: 14px; }
}

.amount {
  &__row { display: flex; justify-content: space-between; padding: 4px 0; font-size: 13px; color: $color-text-secondary;
    &--total { border-top: 1px dashed $color-divider; padding-top: 12px; margin-top: 8px; font-size: 14px; color: $color-text-primary; font-weight: 600; }
  }
  .discount { color: $color-primary; }
  .total { color: $color-primary; font-size: 18px; font-weight: 800; }
}

.info__row { display: flex; justify-content: space-between; padding: 4px 0; font-size: 12px; color: $color-text-secondary; }

.bar {
  position: fixed; bottom: 0; left: 0; right: 0;
  background: #fff;
  height: 60px;
  border-top: 1px solid $color-divider;
  display: flex; align-items: center; justify-content: flex-end; gap: 10px;
  padding: 0 16px;
  z-index: 9;
  &__ghost {
    height: 36px; padding: 0 18px; line-height: 36px;
    border-radius: 999px;
    background: $color-bg-tag;
    color: $color-text-primary;
    font-size: 13px; font-weight: 600;
    &--dis { opacity: .5; }
  }
  &__primary {
    height: 36px; padding: 0 22px; line-height: 36px;
    border-radius: 999px;
    background: linear-gradient(135deg, #ff7a2a, #ff4d4f);
    color: #fff;
    font-size: 13px; font-weight: 700;
    box-shadow: 0 4px 12px rgba(255,77,79,.3);
    &--dis { background: $color-text-placeholder; box-shadow: none; }
  }
}
</style>
