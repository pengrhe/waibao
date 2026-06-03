<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import BrandHeader from '../../components/BrandHeader.vue'
import { Order } from '../../api'
import { fmtPrice, fmtTime, ORDER_STATUS_TEXT, ORDER_STATUS_COLOR } from '../../utils/format'
import { cdnImg } from '../../utils/asset'

const tabs = [
  { key: '', label: '全部' },
  { key: 'pending_pay', label: '待付款' },
  { key: 'pending_print', label: '待打印' },
  { key: 'printing', label: '打印中' },
  { key: 'completed', label: '已完成' },
]
const active = ref<string>('')
const orders = ref<any[]>([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    orders.value = await Order.list(active.value || undefined)
  } finally { loading.value = false }
}

onLoad((opt) => {
  if (opt?.status) active.value = String(opt.status)
})

onMounted(load)
onShow(load)
watch(active, load)

function go(o: any) {
  uni.navigateTo({ url: `/pages/order-detail/index?id=${o.id}` })
}

function goHome() { uni.switchTab({ url: '/pages/index/index' }) }
</script>

<template>
  <view class="ol">
    <BrandHeader title="我的订单" show-back :show-logo="false" />

    <scroll-view scroll-x class="tabs">
      <view
        v-for="t in tabs"
        :key="t.key || 'all'"
        class="tabs__item"
        :class="{ on: active === t.key }"
        @click="active = t.key"
      >{{ t.label }}</view>
    </scroll-view>

    <view v-if="loading" class="loading"><text>加载中…</text></view>
    <view v-else-if="!orders.length" class="empty">
      <text class="empty__icon">📋</text>
      <text class="empty__text">暂无订单</text>
      <view class="empty__btn" @click="goHome">去首页选购</view>
    </view>

    <view v-else class="list">
      <view v-for="o in orders" :key="o.id" class="card" @click="go(o)">
        <view class="card__head">
          <text class="card__no">订单号：{{ o.order_no }}</text>
          <text class="card__status" :style="{ color: ORDER_STATUS_COLOR[o.status] || '#FF4D4F' }">
            {{ ORDER_STATUS_TEXT[o.status] || o.status }}
          </text>
        </view>
        <view class="card__items">
          <image
            v-for="(it, i) in (o.items || []).slice(0, 3)"
            :key="i"
            :src="it.preview_url || cdnImg('entry/personalize.png')"
            mode="aspectFill"
            class="card__item-img"
          />
          <text v-if="(o.items || []).length > 3" class="card__more">+{{ (o.items || []).length - 3 }}</text>
        </view>
        <view class="card__bottom">
          <text class="card__time">{{ fmtTime(o.created_at) }}</text>
          <text class="card__price">实付 ¥ {{ fmtPrice(o.amount_total) }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.ol { min-height: 100vh; background: $color-bg-page; padding-bottom: 24px; }

.tabs {
  background: #fff;
  padding: 8px 12px 12px;
  white-space: nowrap;
}
.tabs__item {
  display: inline-block;
  height: 32px; line-height: 32px;
  padding: 0 14px;
  border-radius: 999px;
  background: $color-bg-tag;
  font-size: 12px;
  color: $color-text-secondary;
  margin-right: 6px;
  &.on { background: $color-primary; color: #fff; font-weight: 700; }
}

.list {
  padding: 12px;
  display: flex; flex-direction: column; gap: 12px;
}

.card {
  background: #fff;
  border-radius: 12px;
  padding: 12px 14px;
  &__head { display: flex; justify-content: space-between; align-items: center; }
  &__no { font-size: 12px; color: $color-text-secondary; }
  &__status { font-size: 12px; font-weight: 700; }
  &__items { margin: 10px 0; display: flex; gap: 8px; align-items: center; }
  &__item-img { width: 56px; height: 56px; border-radius: 6px; background: $color-bg-tag; }
  &__more { font-size: 12px; color: $color-text-secondary; }
  &__bottom { display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: $color-text-secondary; }
  &__price { color: $color-primary; font-weight: 700; font-size: 14px; }
}

.empty {
  text-align: center;
  padding: 80px 24px;
  color: $color-text-secondary;
  &__icon { display: block; font-size: 64px; color: $color-text-placeholder; margin-bottom: 12px; }
  &__text { display: block; margin-bottom: 16px; }
  &__btn {
    display: inline-block;
    padding: 10px 24px;
    background: $color-primary;
    color: #fff;
    border-radius: 999px;
    font-weight: 700;
  }
}

.loading { text-align: center; padding: 60px 0; color: $color-text-secondary; }
</style>
