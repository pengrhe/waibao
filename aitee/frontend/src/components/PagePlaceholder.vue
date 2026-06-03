<script setup lang="ts">
import NavBar from './NavBar.vue'

interface Props {
  title: string
  subtitle?: string
  showBack?: boolean
}

withDefaults(defineProps<Props>(), {
  subtitle: '此页面正在打磨中…',
  showBack: true,
})
</script>

<template>
  <div class="placeholder-page">
    <NavBar :title="title" :show-back="showBack" />
    <div class="placeholder-page__body">
      <span class="placeholder-page__icon i-material-symbols:design-services-outline-rounded" />
      <p class="placeholder-page__title">{{ title }}</p>
      <p class="placeholder-page__sub">{{ subtitle }}</p>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.placeholder-page {
  min-height: 100vh;
  background: $color-bg-page;
  padding-bottom: calc(#{$tabbar-height} + 48px);

  &__body {
    padding: 96px 24px;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    color: $color-text-secondary;
  }

  &__icon {
    font-size: 64px;
    color: $color-primary;
    opacity: 0.7;
    margin-bottom: 16px;
  }

  &__title {
    font-size: 18px;
    font-weight: 600;
    color: $color-text-primary;
    margin: 0 0 8px;
  }

  &__sub {
    font-size: 13px;
    color: $color-text-secondary;
    margin: 0;
  }
}
</style>
