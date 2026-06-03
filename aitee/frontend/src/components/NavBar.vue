<script setup lang="ts">
import { useRouter } from 'vue-router'

interface Props {
  title?: string
  showBack?: boolean
  fixed?: boolean
  bgColor?: string
  textColor?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  showBack: true,
  fixed: false,
  bgColor: '#ffffff',
  textColor: '#1F2937',
})

const router = useRouter()

function goBack() {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.replace('/')
  }
}
</script>

<template>
  <header
    class="navbar"
    :class="{ 'navbar--fixed': props.fixed }"
    :style="{ background: props.bgColor, color: props.textColor }"
  >
    <button v-if="props.showBack" class="navbar__back" @click="goBack">
      <span class="i-material-symbols:arrow-back-ios-rounded" />
    </button>
    <div v-else class="navbar__back navbar__back--placeholder" />
    <h1 class="navbar__title">{{ props.title }}</h1>
    <div class="navbar__right">
      <slot name="right" />
    </div>
  </header>
  <div v-if="props.fixed" class="navbar__placeholder" />
</template>

<style lang="scss" scoped>
.navbar {
  height: $navbar-height;
  display: flex;
  align-items: center;
  padding: 0 $space-3;
  position: relative;
  z-index: 50;

  &--fixed {
    position: fixed;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 100%;
    max-width: 480px;
  }

  &__back {
    width: 36px;
    height: 36px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    color: inherit;

    &--placeholder {
      visibility: hidden;
    }
  }

  &__title {
    flex: 1;
    text-align: center;
    font-size: $font-lg;
    font-weight: 600;
    margin: 0;
    color: inherit;
  }

  &__right {
    min-width: 36px;
    display: inline-flex;
    align-items: center;
    justify-content: flex-end;
  }

  &__placeholder {
    height: $navbar-height;
  }
}
</style>
