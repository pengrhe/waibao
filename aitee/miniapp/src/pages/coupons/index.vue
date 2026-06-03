<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import BrandHeader from '../../components/BrandHeader.vue'
import { Coupon } from '../../api'
import { fmtTime } from '../../utils/format'

const tabs = [
  { key: 'unused', label: '未使用' },
  { key: 'used', label: '已使用' },
  { key: 'expired', label: '已过期' },
  { key: 'shop', label: '领取中心' },
]
const active = ref('unused')
const list = ref<any[]>([])
const templates = ref<any[]>([])

async function load() {
  if (active.value === 'shop') {
    try { templates.value = await Coupon.templates() } catch {}
  } else {
    try { list.value = await Coupon.mine(active.value) } catch {}
  }
}
onMounted(load)
watch(active, load)

async function claim(t: any) {
  try {
    await Coupon.claim(t.id)
    uni.showToast({ title: '已领取', icon: 'success' })
  } catch {}
}

function discountText(c: any) {
  if (!c) return ''
  if (c.type === 'cash') return `¥${c.value}`
  return `${(Number(c.value) * 10).toFixed(1)}折`
}
</script>

<template>
  <view class="cp">
    <BrandHeader title="我的优惠券" show-back :show-logo="false" />

    <view class="tabs">
      <view
        v-for="t in tabs"
        :key="t.key"
        class="tabs__item"
        :class="{ on: active === t.key }"
        @click="active = t.key"
      >
        <text>{{ t.label }}</text>
        <view v-if="active === t.key" class="tabs__indicator" />
      </view>
    </view>

    <view v-if="active === 'shop'">
      <view v-if="!templates.length" class="empty">
        <text class="empty__icon">🎁</text>
        <text class="empty__text">暂无可领取的优惠券</text>
      </view>
      <view v-else class="list">
        <view v-for="t in templates" :key="t.id" class="card">
          <view class="card__left">
            <view class="card__value">
              <template v-if="t.type === 'cash'">
                <text class="card__yuan">¥</text>
                <text>{{ t.value }}</text>
              </template>
              <template v-else>
                <text>{{ (Number(t.value) * 10).toFixed(1) }}</text>
                <text class="card__yuan">折</text>
              </template>
            </view>
            <text class="card__threshold">满 {{ t.threshold }} 可用</text>
          </view>
          <view class="card__right">
            <text class="card__title">{{ t.name }}</text>
            <text class="card__desc">{{ t.description || '' }}</text>
            <text v-if="t.end_at" class="card__expire">{{ fmtTime(t.end_at) }} 截止</text>
          </view>
          <view class="card__action" @click="claim(t)">领取</view>
        </view>
      </view>
    </view>

    <view v-else>
      <view v-if="!list.length" class="empty">
        <text class="empty__icon">🎫</text>
        <text class="empty__text">暂无{{ tabs.find((t) => t.key === active)?.label }}的优惠券</text>
      </view>
      <view v-else class="list">
        <view v-for="uc in list" :key="uc.id" class="card" :class="{ 'card--dis': uc.status !== 'unused' }">
          <view class="card__left">
            <view class="card__value">
              <template v-if="uc.coupon?.type === 'cash'">
                <text class="card__yuan">¥</text>
                <text>{{ uc.coupon?.value }}</text>
              </template>
              <template v-else>
                <text>{{ (Number(uc.coupon?.value) * 10).toFixed(1) }}</text>
                <text class="card__yuan">折</text>
              </template>
            </view>
            <text class="card__threshold">满 {{ uc.coupon?.threshold }} 可用</text>
          </view>
          <view class="card__right">
            <text class="card__title">{{ uc.coupon?.name }}</text>
            <text class="card__desc">{{ uc.coupon?.description || '' }}</text>
            <text v-if="uc.expire_at" class="card__expire">{{ fmtTime(uc.expire_at) }} 到期</text>
          </view>
          <view v-if="uc.status === 'unused'" class="card__action">使用</view>
          <view v-else-if="uc.status === 'used'" class="card__stamp">已使用</view>
          <view v-else class="card__stamp card__stamp--expired">已过期</view>
        </view>
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.cp { min-height: 100vh; background: $color-bg-page; padding-bottom: 40px; }

.tabs {
  display: flex;
  background: #fff;
  padding: 8px 12px 12px;
}
.tabs__item {
  flex: 1;
  position: relative;
  color: $color-text-secondary;
  font-size: 14px;
  padding: 6px 0;
  text-align: center;
  font-weight: 500;
  &.on { color: $color-text-primary; font-weight: 700; }
}
.tabs__indicator {
  position: absolute;
  bottom: -4px; left: 50%; margin-left: -12px;
  width: 24px; height: 3px; border-radius: 2px;
  background: $color-primary;
}

.empty {
  text-align: center;
  padding: 80px 24px;
  color: $color-text-secondary;
  &__icon { display: block; font-size: 64px; color: $color-text-placeholder; margin-bottom: 12px; }
  &__text { display: block; }
}

.list {
  padding: 12px;
  display: flex; flex-direction: column; gap: 12px;
}

.card {
  background: linear-gradient(90deg, #fff 0%, #fffafa 100%);
  border-radius: 12px;
  display: flex; align-items: center;
  padding: 14px;
  box-shadow: 0 2px 6px rgba(0,0,0,.04);
  &--dis { opacity: .5; background: #fafafa; }
  &__left {
    width: 110px;
    text-align: center;
    border-right: 1px dashed $color-divider;
    padding-right: 8px;
  }
  &__value {
    color: $color-primary;
    font-size: 26px; font-weight: 800; line-height: 1;
  }
  &__yuan { font-size: 14px; }
  &__threshold { display: block; font-size: 11px; color: $color-text-secondary; margin-top: 4px; }
  &__right { flex: 1; padding-left: 12px; min-width: 0; }
  &__title { display: block; font-size: 14px; font-weight: 700; }
  &__desc { display: block; font-size: 11px; color: $color-text-secondary; margin-top: 4px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
  &__expire { display: block; font-size: 10px; color: $color-text-placeholder; margin-top: 6px; }
  &__action {
    background: $color-primary; color: #fff;
    font-size: 12px; font-weight: 700;
    padding: 6px 14px;
    border-radius: 999px;
    flex-shrink: 0;
  }
  &__stamp {
    font-size: 11px; color: $color-text-placeholder;
    border: 1px solid $color-text-placeholder;
    padding: 2px 6px; border-radius: 4px;
    &--expired { color: $color-error; border-color: $color-error; }
  }
}
</style>
