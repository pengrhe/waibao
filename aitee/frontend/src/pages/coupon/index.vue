<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import NavBar from '@/components/NavBar.vue'
import { listCoupons } from '@/api/coupon'
import { fmtTime } from '@/utils/format'
import type { Coupon, CouponStatus } from '@/types'

const tabs: { key: CouponStatus; label: string }[] = [
  { key: 'unused', label: '未使用' },
  { key: 'used', label: '已使用' },
  { key: 'expired', label: '已过期' },
]

const active = ref<CouponStatus>('unused')
const list = ref<Coupon[]>([])

async function load() {
  list.value = await listCoupons(active.value)
}

onMounted(load)
watch(active, load)
</script>

<template>
  <div class="cp">
    <NavBar title="我的优惠券" />

    <nav class="tabs">
      <button
        v-for="t in tabs"
        :key="t.key"
        class="tabs__item"
        :class="{ 'tabs__item--active': active === t.key }"
        @click="active = t.key"
      >
        {{ t.label }}
        <span v-if="active === t.key" class="tabs__indicator" />
      </button>
    </nav>

    <div v-if="!list.length" class="empty">
      <span class="i-material-symbols:redeem-rounded empty__icon" />
      <p>暂无{{ tabs.find((t) => t.key === active)?.label }}的优惠券</p>
    </div>

    <ul v-else class="list">
      <li v-for="c in list" :key="c.id" class="card" :class="{ 'card--disabled': c.status !== 'unused' }">
        <div class="card__left">
          <div class="card__value">
            <template v-if="c.type === 'amount'">
              <span class="card__yuan">¥</span>{{ c.value }}
            </template>
            <template v-else>
              {{ (c.value * 10).toFixed(1) }}<span class="card__yuan">折</span>
            </template>
          </div>
          <div class="card__threshold">
            {{ c.threshold ? `满 ${c.threshold} 可用` : '无门槛' }}
          </div>
        </div>
        <div class="card__right">
          <div class="card__title">{{ c.title }}</div>
          <div class="card__desc">{{ c.desc }}</div>
          <div class="card__expire">{{ fmtTime(c.expireAt) }} 到期</div>
        </div>
        <div v-if="c.status === 'unused'" class="card__action">使用</div>
        <div v-else-if="c.status === 'used'" class="card__stamp">已使用</div>
        <div v-else class="card__stamp card__stamp--expired">已过期</div>
      </li>
    </ul>
  </div>
</template>

<style lang="scss" scoped>
.cp {
  min-height: 100vh;
  background: $color-bg-page;
}

.tabs {
  display: flex;
  background: #fff;
  padding: 8px 12px 12px;

  &__item {
    flex: 1;
    color: $color-text-secondary;
    font-size: 14px;
    padding: 6px 0;
    position: relative;
    font-weight: 500;

    &--active {
      color: $color-text-primary;
      font-weight: 700;
    }
  }

  &__indicator {
    position: absolute;
    bottom: -4px;
    left: 50%;
    transform: translateX(-50%);
    width: 24px;
    height: 3px;
    border-radius: 2px;
    background: $color-primary;
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
}

.list {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.card {
  background: linear-gradient(90deg, #fff 0%, #fffafa 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  padding: 14px;
  position: relative;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);

  &--disabled {
    opacity: 0.5;
    background: #fafafa;
  }

  &__left {
    width: 110px;
    text-align: center;
    border-right: 1px dashed $color-divider;
    padding-right: 8px;
  }

  &__value {
    color: $color-primary;
    font-size: 26px;
    font-weight: 800;
    line-height: 1;
  }

  &__yuan {
    font-size: 14px;
  }

  &__threshold {
    font-size: 11px;
    color: $color-text-secondary;
    margin-top: 4px;
  }

  &__right {
    flex: 1;
    padding-left: 12px;
  }

  &__title {
    font-size: 14px;
    font-weight: 700;
  }

  &__desc {
    font-size: 11px;
    color: $color-text-secondary;
    margin-top: 4px;
  }

  &__expire {
    font-size: 10px;
    color: $color-text-placeholder;
    margin-top: 6px;
  }

  &__action {
    background: $color-primary;
    color: #fff;
    font-size: 12px;
    font-weight: 700;
    padding: 6px 14px;
    border-radius: $radius-pill;
  }

  &__stamp {
    font-size: 11px;
    color: $color-text-placeholder;
    border: 1px solid $color-text-placeholder;
    padding: 2px 6px;
    border-radius: 4px;

    &--expired {
      color: $color-error;
      border-color: $color-error;
    }
  }
}
</style>
