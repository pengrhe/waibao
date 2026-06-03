<script setup lang="ts">
/**
 * 自定义底部 tabBar —— 视觉与 8201 frontend/AppTabbar.vue 对齐。
 * H5 用 Material Symbols 矢量图标；小程序端回退 static PNG。
 */
import type { Component } from 'vue'
import IconHomeOutline from '~icons/material-symbols/home-outline-rounded'
import IconHomeFilled from '~icons/material-symbols/home-rounded'
import IconGalleryOutline from '~icons/material-symbols/auto-awesome-outline-rounded'
import IconGalleryFilled from '~icons/material-symbols/auto-awesome-rounded'
import IconCartOutline from '~icons/material-symbols/shopping-cart-outline-rounded'
import IconCartFilled from '~icons/material-symbols/shopping-cart-rounded'
import IconPersonOutline from '~icons/material-symbols/person-outline-rounded'
import IconPersonFilled from '~icons/material-symbols/person-rounded'

interface Props {
  current: 'home' | 'gallery' | 'cart' | 'mine'
}
const props = defineProps<Props>()

interface TabItem {
  id: 'home' | 'gallery' | 'cart' | 'mine' | 'editor'
  label: string
  path: string
  icon?: Component
  iconActive?: Component
  iconPath?: string
  iconActivePath?: string
  center?: boolean
}

const tabs: TabItem[] = [
  {
    id: 'home',
    label: '首页',
    path: '/pages/index/index',
    icon: IconHomeOutline,
    iconActive: IconHomeFilled,
    iconPath: '/static/img/tabbar/home.png',
    iconActivePath: '/static/img/tabbar/home-active.png',
  },
  {
    id: 'gallery',
    label: '印花库',
    path: '/pages/gallery/index',
    icon: IconGalleryOutline,
    iconActive: IconGalleryFilled,
    iconPath: '/static/img/tabbar/gallery.png',
    iconActivePath: '/static/img/tabbar/gallery-active.png',
  },
  { id: 'editor', label: '定制', path: '/pages/editor/index', center: true },
  {
    id: 'cart',
    label: '购物车',
    path: '/pages/cart/index',
    icon: IconCartOutline,
    iconActive: IconCartFilled,
    iconPath: '/static/img/tabbar/cart.png',
    iconActivePath: '/static/img/tabbar/cart-active.png',
  },
  {
    id: 'mine',
    label: '我的',
    path: '/pages/mine/index',
    icon: IconPersonOutline,
    iconActive: IconPersonFilled,
    iconPath: '/static/img/tabbar/mine.png',
    iconActivePath: '/static/img/tabbar/mine-active.png',
  },
]

function go(item: TabItem) {
  if (!item.center && item.id === props.current) return
  if (item.center) {
    uni.navigateTo({ url: item.path })
    return
  }
  uni.switchTab({ url: item.path })
}
</script>

<template>
  <view class="tabbar">
    <view
      v-for="item in tabs"
      :key="item.id"
      class="tabbar__item"
      :class="{
        'tabbar__item--active': current === item.id,
        'tabbar__item--center': item.center,
      }"
      @tap="go(item)"
    >
      <template v-if="item.center">
        <view class="tabbar__center">
          <text class="tabbar__center-logo">aitee</text>
        </view>
        <text class="tabbar__label tabbar__label--center">{{ item.label }}</text>
      </template>
      <template v-else>
        <!-- #ifdef H5 -->
        <view class="tabbar__icon">
          <component :is="current === item.id ? item.iconActive : item.icon" />
        </view>
        <!-- #endif -->
        <!-- #ifndef H5 -->
        <image
          class="tabbar__icon-img"
          :src="current === item.id ? item.iconActivePath : item.iconPath"
          mode="aspectFit"
        />
        <!-- #endif -->
        <text class="tabbar__label">{{ item.label }}</text>
      </template>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.tabbar {
  position: fixed;
  left: 50%;
  bottom: 0;
  transform: translateX(-50%);
  width: 100%;
  max-width: 480px;
  height: calc(#{$tabbar-height} + #{$safe-area-bottom});
  padding-bottom: $safe-area-bottom;
  background: #fff;
  border-top: 1px solid $color-divider;
  display: flex;
  align-items: center;
  justify-content: space-around;
  z-index: 100;
  overflow: visible;

  &__item {
    flex: 1;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: $color-text-secondary;
    font-size: 10px;
    gap: 2px;
    position: relative;

    &--active {
      color: $color-primary;
    }

    &--center {
      flex: 1;
    }
  }

  &__icon {
    font-size: 24px;
    line-height: 1;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: inherit;
  }

  &__icon-img {
    width: 24px;
    height: 24px;
  }

  &__label {
    font-size: 10px;
    line-height: 1;

    &--center {
      margin-top: 38px;
      color: $color-primary;
      font-weight: 600;
    }
  }

  &__center {
    position: absolute;
    top: -22px;
    left: 50%;
    transform: translateX(-50%);
    width: 56px;
    height: 56px;
    border-radius: $radius-pill;
    background: linear-gradient(135deg, #ff6a6c 0%, #ff4d4f 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 6px 16px rgba(255, 77, 79, 0.45);
    border: 4px solid #fff;
  }

  &__center-logo {
    color: #fff;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.5px;
    line-height: 1;
  }
}
</style>
