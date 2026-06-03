<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import BrandHeader from '../../components/BrandHeader.vue'
import CustomTabBar from '../../components/CustomTabBar.vue'
import { Cart } from '../../api'
import { useAuthStore } from '../../store/auth'
import { fmtPrice } from '../../utils/format'

const auth = useAuthStore()
const items = ref<any[]>([])
const loading = ref(false)
const selectedIds = ref<Set<number>>(new Set())

async function load() {
  if (!auth.isAuthed) { items.value = []; return }
  loading.value = true
  try {
    items.value = await Cart.list()
    selectedIds.value = new Set(items.value.map((i) => i.id))
  } finally { loading.value = false }
}

onMounted(load)
onShow(() => {
  load()
  try { uni.hideTabBar({ animation: false }) } catch {}
})

const totalCount = computed(() => items.value.reduce((s, i) => s + (i.qty || 0), 0))
const selectedItems = computed(() => items.value.filter((i) => selectedIds.value.has(i.id)))
const selectedAmount = computed(() => selectedItems.value.reduce((s, i) => s + (Number(i.sku?.price) || 0) * (i.qty || 0), 0))
const allSelected = computed(() => items.value.length > 0 && selectedIds.value.size === items.value.length)

function toggle(id: number) {
  if (selectedIds.value.has(id)) selectedIds.value.delete(id)
  else selectedIds.value.add(id)
  selectedIds.value = new Set(selectedIds.value)
}

function toggleAll() {
  if (allSelected.value) selectedIds.value = new Set()
  else selectedIds.value = new Set(items.value.map((i) => i.id))
}

async function inc(it: any) {
  await Cart.update(it.id, { qty: (it.qty || 1) + 1 })
  load()
}

async function dec(it: any) {
  if ((it.qty || 1) <= 1) {
    uni.showModal({ title: '提示', content: '商品已是最少 1 件，要删除吗？', success: async (r) => {
      if (r.confirm) {
        await Cart.remove([it.id])
        load()
      }
    }})
  } else {
    await Cart.update(it.id, { qty: it.qty - 1 })
    load()
  }
}

async function removeItems() {
  if (!selectedIds.value.size) return
  await Cart.remove(Array.from(selectedIds.value))
  load()
}

function checkout() {
  if (!selectedIds.value.size) { uni.showToast({ title: '请先勾选商品', icon: 'none' }); return }
  uni.navigateTo({ url: `/pages/checkout/index?cart_ids=${Array.from(selectedIds.value).join(',')}` })
}

function goLogin() { uni.navigateTo({ url: '/pages/login/index' }) }
function goHome() { uni.switchTab({ url: '/pages/index/index' }) }

function colorBg(c: string) {
  const map: Record<string, string> = {
    白: '#ffffff', 黑: '#1f2937', 灰: '#9ca3af',
    红: '#ef4444', 粉: '#f9a8d4', 蓝: '#3b82f6',
    绿: '#22c55e', 黄: '#facc15', 橙: '#fb923c',
    紫: '#a855f7', 棕: '#92400e', 米白: '#f5f1ea', 卡其: '#d4c5a0',
  }
  if (!c) return '#9ca3af'
  if (c.startsWith('#')) return c
  for (const k of Object.keys(map)) if (c.includes(k)) return map[k]
  return '#9ca3af'
}
</script>

<template>
  <view class="cart">
    <BrandHeader :title="`购物车${totalCount ? '(' + totalCount + ')' : ''}`" />

    <view v-if="!auth.isAuthed" class="empty">
      <text class="empty__icon">🛒</text>
      <text class="empty__text">登录后查看购物车</text>
      <view class="empty__btn" @click="goLogin">去登录</view>
    </view>
    <view v-else-if="loading" class="empty"><text>加载中…</text></view>
    <view v-else-if="!items.length" class="empty">
      <text class="empty__icon">🛒</text>
      <text class="empty__text">购物车空空如也</text>
      <view class="empty__btn" @click="goHome">去逛逛</view>
    </view>

    <view v-else class="list">
      <view v-for="i in items" :key="i.id" class="item">
        <view class="item__check" @click="toggle(i.id)">
          <view class="check" :class="{ on: selectedIds.has(i.id) }">
            <text v-if="selectedIds.has(i.id)">✓</text>
          </view>
        </view>
        <view class="item__pic">
          <image
            v-if="i.snapshot?.preview_url || i.product?.main_image_url"
            :src="i.snapshot?.preview_url || i.product?.main_image_url"
            mode="aspectFill"
            class="item__pic-img"
          />
          <view v-else class="item__pic-ph">👕</view>
        </view>
        <view class="item__body">
          <text class="item__name">{{ i.snapshot?.name || i.product?.name || '商品' }}</text>
          <view class="item__sku">
            <text>{{ i.sku?.size }}</text>
            <text v-if="i.sku?.color"> · 颜色</text>
            <view v-if="i.sku?.color" class="dot" :style="{ background: colorBg(i.sku.color) }" />
          </view>
          <view class="item__bottom">
            <text class="item__price">¥ {{ fmtPrice(i.sku?.price || 0) }}</text>
            <view class="qty">
              <view class="qty__btn" @click="dec(i)">-</view>
              <text class="qty__num">{{ i.qty }}</text>
              <view class="qty__btn" @click="inc(i)">+</view>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 结算栏 -->
    <view v-if="items.length" class="checkout-bar">
      <view class="checkout-bar__all" @click="toggleAll">
        <view class="check" :class="{ on: allSelected }">
          <text v-if="allSelected">✓</text>
        </view>
        <text>全选</text>
      </view>
      <view class="checkout-bar__amount">
        <text>已选</text>
        <text class="checkout-bar__count">{{ selectedItems.length }}</text>
        <text>件 合计</text>
        <text class="checkout-bar__price">¥{{ fmtPrice(selectedAmount) }}</text>
      </view>
      <view v-if="selectedItems.length" class="checkout-bar__del" @click="removeItems">删除</view>
      <view class="checkout-bar__btn" @click="checkout">结算</view>
    </view>

    <CustomTabBar current="cart" />
  </view>
</template>

<style lang="scss" scoped>
.cart {
  min-height: 100vh;
  background: $color-bg-page;
  padding-bottom: calc(#{$tabbar-height} + 60px + #{$safe-area-bottom});
}

.empty {
  padding: 80px 24px;
  text-align: center;
  color: $color-text-secondary;
  &__icon { display: block; font-size: 80px; color: $color-text-placeholder; margin-bottom: 16px; }
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

.list {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.item {
  background: #fff;
  border-radius: 12px;
  padding: 12px;
  display: flex;
  gap: 12px;
  align-items: center;
  &__check { flex-shrink: 0; }
  &__pic {
    width: 84px; height: 84px;
    border-radius: 8px;
    overflow: hidden;
    background: $color-bg-tag;
    flex-shrink: 0;
  }
  &__pic-img { width: 100%; height: 100%; }
  &__pic-ph { width: 100%; height: 100%; text-align: center; line-height: 84px; font-size: 36px; }
  &__body { flex: 1; min-width: 0; }
  &__name { display: block; font-size: 14px; font-weight: 600; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
  &__sku {
    display: flex; align-items: center; gap: 4px;
    font-size: 11px; color: $color-text-secondary; margin: 4px 0 8px;
    .dot { display: inline-block; width: 12px; height: 12px; border-radius: 50%; border: 1px solid $color-border; }
  }
  &__bottom { display: flex; justify-content: space-between; align-items: center; }
  &__price { color: $color-primary; font-weight: 800; font-size: 16px; }
}

.qty {
  display: inline-flex; align-items: center;
  background: $color-bg-tag;
  border-radius: 999px;
  &__btn { width: 28px; height: 26px; line-height: 26px; text-align: center; font-size: 14px; color: $color-text-primary; }
  &__num { min-width: 24px; text-align: center; font-size: 13px; font-weight: 600; }
}

.check {
  width: 18px; height: 18px; border-radius: 50%;
  border: 1px solid $color-border;
  display: flex; align-items: center; justify-content: center;
  color: transparent; font-size: 12px;
  background: #fff;
  &.on { background: $color-primary; border-color: $color-primary; color: #fff; }
}

.checkout-bar {
  position: fixed;
  left: 0; right: 0;
  bottom: calc(56px + env(safe-area-inset-bottom, 0px));
  height: 60px;
  background: #fff;
  border-top: 1px solid $color-divider;
  display: flex;
  align-items: center;
  padding: 0 16px;
  gap: 6px;
  z-index: 9;
  &__all {
    display: inline-flex; align-items: center; gap: 6px;
    font-size: 13px; color: $color-text-regular;
  }
  &__amount {
    flex: 1; text-align: right;
    font-size: 12px; color: $color-text-secondary;
    margin-right: 4px;
  }
  &__count { color: $color-primary; font-weight: 700; margin: 0 2px; }
  &__price { color: $color-primary; font-weight: 800; font-size: 18px; margin-left: 4px; }
  &__del {
    height: 36px; padding: 0 14px; line-height: 36px;
    background: $color-bg-tag; color: $color-text-regular;
    border-radius: 999px; font-size: 13px;
  }
  &__btn {
    height: 38px; padding: 0 24px; line-height: 38px;
    border-radius: 999px;
    background: linear-gradient(135deg, #ff7a2a, #ff4d4f);
    color: #fff; font-weight: 700; font-size: 14px;
  }
}
</style>
