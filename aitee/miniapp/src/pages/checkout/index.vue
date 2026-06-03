<script setup lang="ts">
import { computed, ref } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import BrandHeader from '../../components/BrandHeader.vue'
import { Address, Cart, Coupon, Order } from '../../api'
import { PLATFORM } from '../../utils/env'
import { mockPay, requestSubscribe, WX_TPL, isWechat } from '../../utils/platform'
import { fmtPrice } from '../../utils/format'

const cartIds = ref<number[]>([])
const directItem = ref<{ sku_id: number; qty: number; name: string; price: number } | null>(null)

const cartItems = ref<any[]>([])
const defaultAddr = ref<any>(null)
const bestCoupon = ref<any>(null)
const couponList = ref<any[]>([])
const showCouponSheet = ref(false)
const submitting = ref(false)
const deliveryType = ref<'pickup' | 'express'>('express')

onLoad(async (opt) => {
  if (opt?.cart_ids) {
    cartIds.value = String(opt.cart_ids).split(',').map(Number).filter(Boolean)
    const all = await Cart.list()
    cartItems.value = all.filter((it: any) => cartIds.value.includes(it.id))
  } else if (opt?.sku_id) {
    directItem.value = {
      sku_id: Number(opt.sku_id),
      qty: Number(opt.qty || 1),
      name: decodeURIComponent(String(opt.pname || '商品')),
      price: Number(opt.price || 0),
    }
  }
  try { defaultAddr.value = await Address.default() } catch {}
  await refreshCoupons()
})

onShow(() => {
  uni.$on('aitee:picked-address', (a: any) => {
    defaultAddr.value = a
  })
})

const totalAmount = computed(() => {
  if (directItem.value) return Number((directItem.value.price * directItem.value.qty).toFixed(2))
  let n = 0
  cartItems.value.forEach((it) => { n += (Number(it.sku?.price) || 0) * (it.qty || 1) })
  return Number(n.toFixed(2))
})

const discount = computed(() => {
  const c = bestCoupon.value?.coupon
  if (!c) return 0
  if (totalAmount.value < Number(c.threshold)) return 0
  if (c.type === 'cash') return Number(c.value)
  return Math.max(0, totalAmount.value * (1 - Number(c.value)))
})

const payAmount = computed(() => Number((totalAmount.value - discount.value).toFixed(2)))

async function refreshCoupons() {
  if (totalAmount.value > 0) {
    try {
      bestCoupon.value = await Coupon.best(totalAmount.value)
    } catch {}
    try {
      couponList.value = await Coupon.mine('unused')
    } catch {}
  }
}

function chooseCoupon(c: any) {
  bestCoupon.value = c
  showCouponSheet.value = false
}

function goAddress() {
  uni.navigateTo({ url: '/pages/addresses/index?picker=1' })
}

async function submit() {
  if (deliveryType.value === 'express' && !defaultAddr.value) {
    uni.showToast({ title: '请添加地址', icon: 'none' })
    return
  }
  if (submitting.value) return
  submitting.value = true
  uni.showLoading({ title: '提交订单…', mask: true })
  try {
    const payload: any = {
      delivery_type: deliveryType.value,
      channel: PLATFORM === 'mp-toutiao' ? 'dy_app' : PLATFORM === 'h5' ? 'h5' : 'wx_app',
      user_coupon_id: bestCoupon.value?.id || undefined,
      address_id: defaultAddr.value?.id,
    }
    if (directItem.value) {
      payload.items = [{ sku_id: directItem.value.sku_id, qty: directItem.value.qty }]
    } else {
      payload.cart_item_ids = cartIds.value
    }
    const order: any = await Order.create(payload)
    if (isWechat) {
      await requestSubscribe([WX_TPL.order_paid, WX_TPL.order_shipped, WX_TPL.print_ready])
    }
    uni.hideLoading()
    uni.showLoading({ title: '支付中…', mask: true })
    const ok = await mockPay(order.order_no || `ORD${order.id}`)
    uni.hideLoading()
    if (!ok) {
      uni.showToast({ title: '支付失败', icon: 'none' })
      uni.redirectTo({ url: `/pages/order-detail/index?id=${order.id}` })
      return
    }
    uni.showToast({ title: '支付成功', icon: 'success' })
    setTimeout(() => {
      uni.redirectTo({ url: `/pages/order-detail/index?id=${order.id}` })
    }, 500)
  } catch (e) {
    uni.hideLoading()
    uni.showToast({ title: '提交失败，请重试', icon: 'none' })
  } finally { submitting.value = false }
}
</script>

<template>
  <view class="checkout">
    <BrandHeader title="确认订单" show-back :show-logo="false" />

    <!-- 配送方式 -->
    <view class="row row--seg">
      <text class="row__label">配送方式</text>
      <view class="seg">
        <view class="seg__opt" :class="{ on: deliveryType === 'express' }" @click="deliveryType = 'express'">快递配送</view>
        <view class="seg__opt" :class="{ on: deliveryType === 'pickup' }" @click="deliveryType = 'pickup'">门店自提</view>
      </view>
    </view>

    <!-- 地址 -->
    <view v-if="deliveryType === 'express'" class="addr" @click="goAddress">
      <text class="addr__icon">📍</text>
      <view v-if="defaultAddr" class="addr__body">
        <view class="addr__line1">
          <text class="addr__name">{{ defaultAddr.receiver }}</text>
          <text class="addr__phone">{{ defaultAddr.phone }}</text>
          <text v-if="defaultAddr.is_default" class="addr__tag">默认</text>
        </view>
        <text class="addr__line2">{{ defaultAddr.province }}{{ defaultAddr.city }}{{ defaultAddr.district }} {{ defaultAddr.detail }}</text>
      </view>
      <text v-else class="addr__placeholder">请选择收货地址</text>
      <text class="addr__arrow">›</text>
    </view>

    <!-- 商品 -->
    <view class="goods">
      <view v-for="i in cartItems" :key="i.id" class="goods__item">
        <image
          v-if="i.snapshot?.preview_url || i.product?.main_image_url"
          :src="i.snapshot?.preview_url || i.product?.main_image_url"
          mode="aspectFill"
          class="goods__img"
        />
        <view v-else class="goods__img goods__img--ph">👕</view>
        <view class="goods__body">
          <text class="goods__name">{{ i.snapshot?.name || i.product?.name }}</text>
          <text class="goods__sku">{{ i.sku?.color }} / {{ i.sku?.size }} · x{{ i.qty }}</text>
        </view>
        <text class="goods__price">¥ {{ fmtPrice((Number(i.sku?.price) || 0) * i.qty) }}</text>
      </view>
      <view v-if="directItem" class="goods__item">
        <view class="goods__img goods__img--ph">👕</view>
        <view class="goods__body">
          <text class="goods__name">{{ directItem.name }}</text>
          <text class="goods__sku">x{{ directItem.qty }}</text>
        </view>
        <text class="goods__price">¥ {{ fmtPrice(directItem.price * directItem.qty) }}</text>
      </view>
    </view>

    <!-- 优惠券 -->
    <view class="row" @click="showCouponSheet = true">
      <text class="row__label">优惠券</text>
      <text v-if="bestCoupon" class="row__value row__value--accent">
        {{ bestCoupon.coupon?.name }}
      </text>
      <text v-else-if="couponList.length" class="row__value">{{ couponList.length }} 张可用</text>
      <text v-else class="row__value">无可用</text>
      <text class="row__arrow">›</text>
    </view>

    <!-- 金额 -->
    <view class="amount-card">
      <view class="amount-card__row">
        <text>商品合计</text>
        <text>¥ {{ fmtPrice(totalAmount) }}</text>
      </view>
      <view class="amount-card__row">
        <text>优惠</text>
        <text class="discount">-¥ {{ fmtPrice(discount) }}</text>
      </view>
      <view class="amount-card__row amount-card__row--total">
        <text>实付</text>
        <text class="total">¥ {{ fmtPrice(payAmount) }}</text>
      </view>
    </view>

    <!-- 提交栏 -->
    <view class="bar">
      <view class="bar__amount">
        <text>合计 </text>
        <text class="bar__price">¥{{ fmtPrice(payAmount) }}</text>
      </view>
      <view class="bar__btn" :class="{ 'bar__btn--dis': submitting }" @click="submit">
        {{ submitting ? '处理中…' : '提交订单' }}
      </view>
    </view>

    <!-- 优惠券选择面板 -->
    <view v-if="showCouponSheet" class="popup" @click="showCouponSheet = false">
      <view class="popup__sheet" @click.stop>
        <text class="popup__title">选择优惠券</text>
        <view class="popup__list">
          <view
            v-for="c in couponList"
            :key="c.id"
            class="coupon-card"
            :class="{
              on: bestCoupon?.id === c.id,
              dis: totalAmount < Number(c.coupon?.threshold || 0)
            }"
            @click="chooseCoupon(c)"
          >
            <view class="coupon-card__left">
              <view class="coupon-card__value">
                <template v-if="c.coupon?.type === 'cash'">
                  <text class="coupon-card__sym">¥</text>
                  <text>{{ c.coupon?.value }}</text>
                </template>
                <template v-else>
                  <text>{{ (Number(c.coupon?.value) * 10).toFixed(1) }}</text>
                  <text class="coupon-card__sym">折</text>
                </template>
              </view>
              <text class="coupon-card__threshold">满 {{ c.coupon?.threshold }} 可用</text>
            </view>
            <view class="coupon-card__right">
              <text class="coupon-card__name">{{ c.coupon?.name }}</text>
              <text class="coupon-card__desc">{{ c.coupon?.description || '' }}</text>
            </view>
          </view>
          <view class="coupon-card coupon-card--none" @click="chooseCoupon(null)">不使用优惠券</view>
        </view>
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.checkout { min-height: 100vh; background: $color-bg-page; padding-bottom: 80px; }

.row {
  background: #fff;
  margin: 12px;
  border-radius: 12px;
  padding: 14px 12px;
  display: flex; align-items: center;
  font-size: 14px;
  &__label { flex: 1; }
  &__value { color: $color-text-secondary; margin-right: 4px; font-size: 13px;
    &--accent { color: $color-primary; font-weight: 600; }
  }
  &__arrow { font-size: 18px; color: $color-text-placeholder; }
  &--seg { padding: 12px; }
}
.seg {
  display: flex; gap: 4px;
  background: $color-bg-tag;
  border-radius: 999px;
  padding: 2px;
  &__opt {
    padding: 5px 14px;
    border-radius: 999px;
    font-size: 12px;
    color: $color-text-secondary;
    &.on { background: $color-primary; color: #fff; font-weight: 700; }
  }
}

.addr {
  background: #fff;
  margin: 0 12px 12px;
  border-radius: 12px;
  padding: 14px 12px;
  display: flex; align-items: center; gap: 8px;
  &__icon { font-size: 22px; color: $color-primary; }
  &__body { flex: 1; min-width: 0; }
  &__line1 { display: flex; gap: 12px; align-items: center; font-size: 14px; margin-bottom: 4px; }
  &__name { font-weight: 700; }
  &__phone { color: $color-text-secondary; font-size: 13px; }
  &__tag { background: $color-primary; color: #fff; font-size: 10px; padding: 2px 6px; border-radius: 4px; }
  &__line2 { font-size: 12px; color: $color-text-secondary; }
  &__placeholder { flex: 1; color: $color-text-secondary; font-size: 13px; }
  &__arrow { font-size: 22px; color: $color-text-placeholder; }
}

.goods {
  background: #fff;
  margin: 0 12px 12px;
  border-radius: 12px;
  padding: 0 12px;
  &__item {
    display: flex; align-items: center; gap: 12px;
    padding: 12px 0;
    border-bottom: 1px solid $color-divider;
    &:last-child { border-bottom: 0; }
  }
  &__img { width: 64px; height: 64px; border-radius: 6px; background: $color-bg-tag; }
  &__img--ph { text-align: center; line-height: 64px; font-size: 28px; }
  &__body { flex: 1; min-width: 0; }
  &__name { display: block; font-size: 14px; font-weight: 600; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
  &__sku { display: block; font-size: 11px; color: $color-text-secondary; margin-top: 4px; }
  &__price { color: $color-primary; font-weight: 700; font-size: 14px; }
}

.amount-card {
  background: #fff;
  margin: 0 12px;
  border-radius: 12px;
  padding: 12px;
  &__row { display: flex; justify-content: space-between; padding: 4px 0; font-size: 13px; color: $color-text-secondary;
    &--total { border-top: 1px dashed $color-divider; margin-top: 8px; padding-top: 12px; font-size: 14px; color: $color-text-primary; font-weight: 600; }
  }
  .discount { color: $color-primary; }
  .total { color: $color-primary; font-size: 18px; font-weight: 800; }
}

.bar {
  position: fixed; bottom: 0; left: 0; right: 0;
  height: 60px;
  background: #fff;
  border-top: 1px solid $color-divider;
  display: flex; align-items: center;
  padding: 0 16px;
  z-index: 9;
  &__amount { flex: 1; text-align: right; margin-right: 12px; font-size: 13px; color: $color-text-secondary; }
  &__price { color: $color-primary; font-weight: 800; font-size: 20px; margin-left: 4px; }
  &__btn {
    height: 40px; padding: 0 28px; line-height: 40px;
    border-radius: 999px;
    background: linear-gradient(135deg, #ff7a2a, #ff4d4f);
    color: #fff; font-weight: 700; font-size: 14px;
    &--dis { opacity: .6; }
  }
}

.popup {
  position: fixed; inset: 0;
  background: rgba(0,0,0,.4);
  z-index: 100;
  display: flex; align-items: flex-end;
  &__sheet {
    width: 100%;
    background: #fff;
    border-radius: 16px 16px 0 0;
    padding: 20px;
    max-height: 70vh;
  }
  &__title { display: block; font-size: 16px; font-weight: 700; text-align: center; margin-bottom: 16px; }
  &__list { display: flex; flex-direction: column; gap: 10px; }
}

.coupon-card {
  display: flex;
  background: linear-gradient(90deg, #fff 0%, #fff8f8 100%);
  border-radius: 12px;
  border: 1px solid $color-divider;
  overflow: hidden;
  &.on { border-color: $color-primary; }
  &.dis { opacity: .5; }
  &--none { justify-content: center; padding: 14px 0; color: $color-text-secondary; font-size: 13px; }
  &__left {
    width: 110px;
    padding: 14px;
    background: rgba(255,77,79,.06);
    text-align: center;
    border-right: 1px dashed $color-divider;
  }
  &__value {
    color: $color-primary;
    font-size: 22px; font-weight: 800; line-height: 1.2;
  }
  &__sym { font-size: 12px; }
  &__threshold { display: block; font-size: 11px; color: $color-text-secondary; margin-top: 4px; }
  &__right { flex: 1; padding: 14px 12px; }
  &__name { display: block; font-size: 14px; font-weight: 700; }
  &__desc { display: block; font-size: 11px; color: $color-text-secondary; margin-top: 4px; }
}
</style>
