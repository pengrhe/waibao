<script setup lang="ts">
interface Props {
  showLogo?: boolean
  title?: string
  bg?: string
}
withDefaults(defineProps<Props>(), {
  showLogo: true,
  title: 'aitee',
  bg: 'transparent',
})
</script>

<template>
  <header class="brand-header" :style="{ background: bg }">
    <div class="brand-header__logo">
      <span class="brand-header__avatar">
        <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
          <path d="M12 1.5l2.4 7.7 7.7 2.4-7.7 2.4-2.4 7.7-2.4-7.7-7.7-2.4 7.7-2.4z"/>
        </svg>
      </span>
      <span class="brand-header__title">{{ title }}</span>
    </div>
    <div class="brand-header__capsule">
      <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
        <circle cx="5" cy="12" r="2"/>
        <circle cx="12" cy="12" r="2"/>
        <circle cx="19" cy="12" r="2"/>
      </svg>
      <span class="brand-header__divider" />
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
        <circle cx="12" cy="12" r="9"/>
      </svg>
    </div>
  </header>
</template>

<style lang="scss" scoped>
.brand-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 44px;
  padding: 0 12px;
  position: relative;

  svg {
    width: 1em;
    height: 1em;
    display: inline-block;
    flex-shrink: 0;
  }

  &__logo {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  &__avatar {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: linear-gradient(135deg, #ff6a6c, #ff4d4f);
    color: #fff;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    box-shadow: 0 4px 10px rgba(255, 77, 79, 0.35);
  }

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
    border: 1px solid rgba(0, 0, 0, 0.08);
    display: inline-flex;
    align-items: center;
    padding: 0 10px;
    color: #6b7280;
    font-size: 16px;
    gap: 6px;
  }

  &__divider {
    width: 1px;
    height: 14px;
    background: rgba(0, 0, 0, 0.1);
  }
}
</style>
