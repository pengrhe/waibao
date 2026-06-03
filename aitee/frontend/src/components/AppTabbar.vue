<script setup lang="ts">
import { computed, type Component } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import IconHomeOutline from '~icons/material-symbols/home-outline-rounded'
import IconHomeFilled from '~icons/material-symbols/home-rounded'
import IconGalleryOutline from '~icons/material-symbols/auto-awesome-outline-rounded'
import IconGalleryFilled from '~icons/material-symbols/auto-awesome-rounded'
import IconCartOutline from '~icons/material-symbols/shopping-cart-outline-rounded'
import IconCartFilled from '~icons/material-symbols/shopping-cart-rounded'
import IconPersonOutline from '~icons/material-symbols/person-outline-rounded'
import IconPersonFilled from '~icons/material-symbols/person-rounded'

interface TabItem {
  name: string
  path: string
  label: string
  icon?: Component
  iconActive?: Component
  center?: boolean
}

const tabs: TabItem[] = [
  { name: 'home', path: '/', label: '首页', icon: IconHomeOutline, iconActive: IconHomeFilled },
  { name: 'gallery', path: '/gallery', label: '印花库', icon: IconGalleryOutline, iconActive: IconGalleryFilled },
  { name: 'editor', path: '/editor', label: '定制', center: true },
  { name: 'cart', path: '/cart', label: '购物车', icon: IconCartOutline, iconActive: IconCartFilled },
  { name: 'mine', path: '/mine', label: '我的', icon: IconPersonOutline, iconActive: IconPersonFilled },
]

const route = useRoute()
const router = useRouter()

const activeName = computed(() => {
  const matched = tabs.find((t) => t.path === route.path)
  return matched?.name ?? ''
})

function go(item: TabItem) {
  if (route.path === item.path) return
  router.push(item.path)
}
</script>

<template>
  <nav class="tabbar">
    <button
      v-for="item in tabs"
      :key="item.name"
      class="tabbar__item"
      :class="{
        'tabbar__item--active': activeName === item.name,
        'tabbar__item--center': item.center,
      }"
      @click="go(item)"
    >
      <template v-if="item.center">
        <span class="tabbar__center">
          <span class="tabbar__center-logo">aitee</span>
        </span>
        <span class="tabbar__label tabbar__label--center">{{ item.label }}</span>
      </template>
      <template v-else>
        <span class="tabbar__icon">
          <component
            :is="activeName === item.name ? item.iconActive : item.icon"
          />
        </span>
        <span class="tabbar__label">{{ item.label }}</span>
      </template>
    </button>
  </nav>
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
  }
}
</style>
