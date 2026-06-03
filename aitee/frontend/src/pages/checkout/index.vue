<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { showLoadingToast, showToast } from 'vant'
import { storeToRefs } from 'pinia'
import NavBar from '@/components/NavBar.vue'
import { defaultAddress, listAddresses } from '@/api/address'
import { bestCouponForAmount, listCoupons, consumeCoupon } from '@/api/coupon'
import { createOrder, payOrder } from '@/api/order'
import { useCartStore } from '@/store/cart'
import { fmtPrice } from '@/utils/format'
import type { Address, Coupon } from '@/types'

const router = useRouter()
const cart = useCartStore()
const { selectedItems } = storeToRefs(cart)

const address = ref<Address | null>(null)
const coupon = ref<Coupon | null>(null)
const couponList = ref<Coupon[]>([])
const showCouponSheet = ref(false)
const submitting = ref(false)

const totalAmount = computed(() => selectedItems.value.reduce((s, i) => s + i.price * i.qty, 0))
const discount = computed(() => {
  const c = coupon.value
  if (!c || c.status !== 'unused') return 0
  if (totalAmount.value < c.threshold) return 0
  if (c.type === 'amount') return c.value
  return Math.max(0, totalAmount.value * (1 - c.value))
})
const payAmount = computed(() => +(totalAmount.value - discount.value).toFixed(2))

onMounted(async () => {
  const [a, list, best] = await Promise.all([
    listAddresses(),
    listCoupons('unused'),
    bestCouponForAmount(totalAmount.value),
  ])
  address.value = a.find((x) => x.isDefault) || a[0] || (await defaultAddress()) || null
  couponList.value = list
  coupon.value = best ?? null

  // 确保选中商品存在
  if (!selectedItems.value.length) {
    showToast('请先在购物车选择商品')
    router.replace('/cart')
  }
})

function chooseCoupon(c: Coupon | null) {
  coupon.value = c
  showCouponSheet.value = false
}

async function submit() {
  if (!address.value) {
    showToast('请先选择收货地址')
    return
  }
  if (submitting.value) return
  submitting.value = true
  const t = showLoadingToast({ message: '提交订单…', duration: 0, forbidClick: true })
  try {
    const order = await createOrder({
      items: selectedItems.value,
      address: address.value,
      coupon: coupon.value ?? undefined,
    })
    // 模拟支付
    t.message = '支付中…'
    await payOrder(order.id)
    if (coupon.value && coupon.value.status === 'unused') {
      await consumeCoupon(coupon.value.id)
    }
    // 移除购物车里已结算的项
    await cart.remove(selectedItems.value.map((i) => i.id))
    t.close()
    showToast({ type: 'success', message: '支付成功' })
    router.replace(`/order/${order.id}?paid=1`)
  } catch {
    t.close()
    showToast({ type: 'fail', message: '提交失败，请重试' })
  } finally {
    submitting.value = false
  }
}

function goAddress() {
  router.push('/address/list?picker=1')
}
</script>

<template>
  <div class="checkout">
    <NavBar title="确认订单" />

    <!-- 地址 -->
    <div class="addr" @click="goAddress">
      <span class="addr__icon i-material-symbols:location-on-outline-rounded" />
      <div v-if="address" class="addr__body">
        <div class="addr__line1">
          <strong>{{ address.name }}</strong>
          <span>{{ address.phone }}</span>
        </div>
        <div class="addr__line2">{{ address.region }} {{ address.detail }}</div>
      </div>
      <div v-else class="addr__placeholder">请选择收货地址</div>
      <span class="addr__arrow i-material-symbols:chevron-right-rounded" />
    </div>

    <!-- 商品 -->
    <div class="goods">
      <div v-for="i in selectedItems" :key="i.id" class="goods__item">
        <img :src="i.previewUrl" />
        <div class="goods__body">
          <div class="goods__name text-ellipsis">{{ i.productName }}</div>
          <div class="goods__sku">{{ i.size }} · x{{ i.qty }}</div>
        </div>
        <span class="goods__price">¥ {{ fmtPrice(i.price * i.qty) }}</span>
      </div>
    </div>

    <!-- 优惠券 -->
    <div class="row" @click="showCouponSheet = true">
      <span class="row__label">优惠券</span>
      <span v-if="coupon" class="row__value row__value--accent">{{ coupon.title }}</span>
      <span v-else-if="couponList.length" class="row__value">{{ couponList.length }} 张可用</span>
      <span v-else class="row__value">无可用</span>
      <span class="row__arrow i-material-symbols:chevron-right-rounded" />
    </div>

    <!-- 价格 -->
    <div class="amount-card">
      <div class="amount-card__row">
        <span>商品合计</span>
        <span>¥ {{ fmtPrice(totalAmount) }}</span>
      </div>
      <div class="amount-card__row">
        <span>优惠</span>
        <span class="discount">-¥ {{ fmtPrice(discount) }}</span>
      </div>
      <div class="amount-card__row amount-card__row--total">
        <span>实付</span>
        <span class="total">¥ {{ fmtPrice(payAmount) }}</span>
      </div>
    </div>

    <!-- 提交栏 -->
    <div class="bar">
      <div class="bar__amount">
        合计 <span class="bar__price">¥{{ fmtPrice(payAmount) }}</span>
      </div>
      <button class="bar__btn" :disabled="submitting" @click="submit">
        提交订单
      </button>
    </div>

    <!-- 优惠券选择 -->
    <van-popup v-model:show="showCouponSheet" round position="bottom" :style="{ padding: '20px', maxHeight: '70vh' }">
      <div class="coupon-sheet">
        <div class="coupon-sheet__title">选择优惠券</div>
        <div class="coupon-sheet__list">
          <button
            v-for="c in couponList"
            :key="c.id"
            class="coupon-card"
            :class="{ 'coupon-card--active': coupon?.id === c.id, 'coupon-card--disabled': totalAmount < c.threshold }"
            @click="chooseCoupon(c)"
          >
            <div class="coupon-card__left">
              <div class="coupon-card__value">
                <template v-if="c.type === 'amount'"><span>¥</span>{{ c.value }}</template>
                <template v-else>{{ (c.value * 10).toFixed(1) }}<span>折</span></template>
              </div>
              <div class="coupon-card__threshold">
                {{ c.threshold ? `满 ${c.threshold} 可用` : '无门槛' }}
              </div>
            </div>
            <div class="coupon-card__right">
              <div class="coupon-card__name">{{ c.title }}</div>
              <div class="coupon-card__desc">{{ c.desc }}</div>
            </div>
          </button>
          <button class="coupon-card coupon-card--none" @click="chooseCoupon(null)">不使用优惠券</button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<style lang="scss" scoped>
.checkout {
  min-height: 100vh;
  background: $color-bg-page;
  padding-bottom: 80px;
}

.addr {
  background: #fff;
  margin: 12px;
  border-radius: 12px;
  padding: 14px 12px;
  display: flex;
  align-items: center;
  gap: 8px;

  &__icon {
    font-size: 22px;
    color: $color-primary;
  }

  &__body {
    flex: 1;
    min-width: 0;
  }

  &__line1 {
    display: flex;
    gap: 12px;
    align-items: center;
    font-size: 14px;
    margin-bottom: 4px;
  }

  &__line2 {
    font-size: 12px;
    color: $color-text-secondary;
  }

  &__placeholder {
    flex: 1;
    color: $color-text-secondary;
    font-size: 13px;
  }

  &__arrow {
    font-size: 18px;
    color: $color-text-placeholder;
  }
}

.goods {
  background: #fff;
  margin: 0 12px;
  border-radius: 12px;
  padding: 12px;

  &__item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 0;
    border-bottom: 1px solid $color-divider;
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
    margin-top: 4px;
  }

  &__price {
    color: $color-primary;
    font-weight: 700;
    font-size: 14px;
  }
}

.row {
  background: #fff;
  margin: 12px;
  border-radius: 12px;
  padding: 14px 12px;
  display: flex;
  align-items: center;
  font-size: 14px;

  &__label {
    flex: 1;
  }

  &__value {
    color: $color-text-secondary;
    margin-right: 4px;

    &--accent {
      color: $color-primary;
      font-weight: 600;
    }
  }

  &__arrow {
    font-size: 18px;
    color: $color-text-placeholder;
  }
}

.amount-card {
  background: #fff;
  margin: 0 12px;
  border-radius: 12px;
  padding: 12px;

  &__row {
    display: flex;
    justify-content: space-between;
    padding: 4px 0;
    font-size: 13px;
    color: $color-text-secondary;

    &--total {
      border-top: 1px dashed $color-divider;
      margin-top: 8px;
      padding-top: 12px;
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

.bar {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 480px;
  height: 60px;
  background: #fff;
  border-top: 1px solid $color-divider;
  display: flex;
  align-items: center;
  padding: 0 16px;
  z-index: 9;

  &__amount {
    flex: 1;
    text-align: right;
    margin-right: 12px;
    font-size: 13px;
    color: $color-text-secondary;
  }

  &__price {
    color: $color-primary;
    font-weight: 800;
    font-size: 20px;
    margin-left: 4px;
  }

  &__btn {
    height: 40px;
    padding: 0 28px;
    border-radius: $radius-pill;
    background: $color-primary;
    color: #fff;
    font-weight: 700;
    font-size: 14px;

    &:disabled {
      opacity: 0.5;
    }
  }
}

.coupon-sheet {
  &__title {
    font-size: 16px;
    font-weight: 700;
    text-align: center;
    margin-bottom: 16px;
  }

  &__list {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
}

.coupon-card {
  display: flex;
  background: linear-gradient(90deg, #fff 0%, #fff8f8 100%);
  border-radius: 12px;
  border: 1px solid $color-divider;
  overflow: hidden;
  text-align: left;
  padding: 0;
  position: relative;

  &--active {
    border-color: $color-primary;
    box-shadow: 0 0 0 1px $color-primary;
  }

  &--disabled {
    opacity: 0.5;
  }

  &--none {
    justify-content: center;
    padding: 14px 0;
    color: $color-text-secondary;
    font-size: 13px;
  }

  &__left {
    width: 110px;
    padding: 14px;
    background: rgba(255, 77, 79, 0.06);
    text-align: center;
    border-right: 1px dashed $color-divider;
  }

  &__value {
    color: $color-primary;
    font-size: 22px;
    font-weight: 800;
    line-height: 1.2;
    span {
      font-size: 12px;
    }
  }

  &__threshold {
    font-size: 11px;
    color: $color-text-secondary;
    margin-top: 4px;
  }

  &__right {
    flex: 1;
    padding: 14px 12px;
  }

  &__name {
    font-size: 14px;
    font-weight: 700;
  }

  &__desc {
    font-size: 11px;
    color: $color-text-secondary;
    margin-top: 4px;
  }
}
</style>
