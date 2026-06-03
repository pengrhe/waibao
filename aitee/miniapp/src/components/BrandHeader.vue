<script setup lang="ts">
interface Props {
  showLogo?: boolean
  title?: string
  bg?: string
  rightText?: string
  showBack?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  showLogo: true,
  title: 'aitee',
  bg: 'transparent',
  rightText: '',
  showBack: false,
})
defineEmits<{ rightClick: [] }>()

function back() {
  uni.navigateBack().catch(() => {
    uni.switchTab({ url: '/pages/index/index' })
  })
}
</script>

<template>
  <view class="brand-header" :style="{ background: bg }">
    <view class="brand-header__left">
      <view v-if="showBack" class="brand-header__back" @click="back">‹</view>
      <view v-if="showLogo" class="brand-header__avatar">
        <text class="brand-header__star">✦</text>
      </view>
      <text class="brand-header__title">{{ title }}</text>
    </view>
    <view class="brand-header__capsule" @click="$emit('rightClick')">
      <text v-if="rightText">{{ rightText }}</text>
      <template v-else>
        <text class="brand-header__dot">•</text>
        <text class="brand-header__dot">•</text>
        <text class="brand-header__dot">•</text>
        <text class="brand-header__divider">|</text>
        <text class="brand-header__circle">○</text>
      </template>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.brand-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 44px;
  padding: 0 12px;

  &__left {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  &__back {
    width: 28px; height: 28px; line-height: 26px; text-align: center;
    background: rgba(255,255,255,.7);
    border-radius: 50%; font-size: 20px; color: #1f2937;
    margin-right: 4px;
  }

  &__avatar {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: linear-gradient(135deg, #ff6a6c, #ff4d4f);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 10px rgba(255, 77, 79, 0.35);
  }

  &__star { color: #fff; font-size: 14px; font-weight: 800; line-height: 1; }

  &__title {
    font-size: 16px;
    font-weight: 800;
    color: #1f2937;
    letter-spacing: 0.4px;
  }

  &__capsule {
    height: 28px;
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.7);
    border: 1rpx solid rgba(0, 0, 0, 0.08);
    display: flex;
    align-items: center;
    padding: 0 10px;
    color: #6b7280;
    gap: 4px;
    font-size: 12px;
  }

  &__dot { color: #6b7280; font-size: 12px; line-height: 1; }
  &__circle { color: #6b7280; font-size: 14px; line-height: 1; }
  &__divider { color: rgba(0,0,0,.1); margin: 0 2px; font-size: 12px; line-height: 1; }
}
</style>
