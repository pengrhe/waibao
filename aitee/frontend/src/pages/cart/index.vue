<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showDialog, showToast } from 'vant'
import { storeToRefs } from 'pinia'
import BrandHeader from '@/components/BrandHeader.vue'
import { useCartStore } from '@/store/cart'
import { fmtPrice } from '@/utils/format'

const router = useRouter()
const cart = useCartStore()
const { items, totalCount, selectedItems, selectedAmount } = storeToRefs(cart)

onMounted(() => {
  cart.reload()
})

const allSelected = computed(() => items.value.length > 0 && items.value.every((i) => i.selected))

async function toggleAll() {
  await cart.selectAll(!allSelected.value)
}

async function inc(id: string, qty: number) {
  await cart.setQty(id, qty + 1)
}

async function dec(id: string, qty: number) {
  if (qty <= 1) {
    await showDialog({ title: '提示', message: '商品已是最少 1 件，要删除吗？', showCancelButton: true })
      .then(() => cart.remove([id]))
      .catch(() => {})
  } else {
    await cart.setQty(id, qty - 1)
  }
}

async function onCheckout() {
  if (!selectedItems.value.length) {
    showToast('请先勾选商品')
    return
  }
  router.push('/checkout')
}
</script>

<template>
  <div class="cart">
    <BrandHeader :title="`购物车(${totalCount})`" />

    <div v-if="!items.length" class="empty">
      <span class="i-material-symbols:shopping-cart-outline-rounded empty__icon" />
      <p>暂无数据</p>
      <button class="btn-primary" @click="router.push('/')">去逛逛</button>
    </div>

    <div v-else class="list">
      <div v-for="i in items" :key="i.id" class="item">
        <button class="item__check" @click="cart.toggleSelected(i.id)">
          <span
            class="check"
            :class="{ 'check--on': i.selected }"
          >
            <span class="i-material-symbols:check-rounded" />
          </span>
        </button>
        <div class="item__pic">
          <img :src="i.previewUrl" alt="" />
        </div>
        <div class="item__body">
          <div class="item__name text-ellipsis">{{ i.productName }}</div>
          <div class="item__sku">{{ i.size }} · 颜色 <span class="dot" :style="{ background: i.color }" /></div>
          <div class="item__bottom">
            <span class="item__price">¥ {{ fmtPrice(i.price) }}</span>
            <span class="qty">
              <button class="qty__btn" @click="dec(i.id, i.qty)">-</button>
              <span class="qty__num">{{ i.qty }}</span>
              <button class="qty__btn" @click="inc(i.id, i.qty)">+</button>
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 结算栏 -->
    <div class="checkout-bar">
      <button class="checkout-bar__all" @click="toggleAll">
        <span class="check" :class="{ 'check--on': allSelected }">
          <span class="i-material-symbols:check-rounded" />
        </span>
        全选
      </button>
      <div class="checkout-bar__amount">
        已选<span class="checkout-bar__count">{{ selectedItems.length }}</span>件
        合计 <span class="checkout-bar__price">¥{{ fmtPrice(selectedAmount) }}</span>
      </div>
      <button class="checkout-bar__btn" @click="onCheckout">结算</button>
    </div>
  </div>
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

  &__icon {
    font-size: 80px;
    color: $color-text-placeholder;
    display: block;
    margin: 0 auto 16px;
  }

  p {
    margin: 0 0 16px;
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

  &__check {
    flex-shrink: 0;
  }

  &__pic {
    width: 84px;
    height: 84px;
    border-radius: 8px;
    overflow: hidden;
    background: $color-bg-tag;
    flex-shrink: 0;
    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
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
    display: flex;
    align-items: center;
    gap: 4px;
    margin: 4px 0 8px;

    .dot {
      display: inline-block;
      width: 12px;
      height: 12px;
      border-radius: 50%;
      border: 1px solid $color-border;
    }
  }

  &__bottom {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  &__price {
    color: $color-primary;
    font-weight: 800;
    font-size: 16px;
  }
}

.qty {
  display: inline-flex;
  align-items: center;
  background: $color-bg-tag;
  border-radius: $radius-pill;

  &__btn {
    width: 28px;
    height: 26px;
    font-size: 14px;
    color: $color-text-primary;
  }

  &__num {
    min-width: 24px;
    text-align: center;
    font-size: 13px;
    font-weight: 600;
  }
}

.check {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 1.5px solid $color-border;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: transparent;
  font-size: 12px;
  background: #fff;

  &--on {
    background: $color-primary;
    border-color: $color-primary;
    color: #fff;
  }
}

.checkout-bar {
  position: fixed;
  bottom: $tabbar-height;
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

  &__all {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    color: $color-text-regular;
  }

  &__amount {
    flex: 1;
    text-align: right;
    margin-right: 12px;
    font-size: 12px;
    color: $color-text-secondary;
  }

  &__count {
    color: $color-primary;
    font-weight: 700;
    margin: 0 2px;
  }

  &__price {
    color: $color-primary;
    font-weight: 800;
    font-size: 18px;
    margin-left: 4px;
  }

  &__btn {
    height: 38px;
    padding: 0 24px;
    border-radius: $radius-pill;
    background: $color-primary;
    color: #fff;
    font-weight: 700;
    font-size: 14px;
  }
}
</style>
