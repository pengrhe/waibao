<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppTabbar from '@/components/AppTabbar.vue'

const route = useRoute()

const showTabbar = computed(() => Boolean(route.meta?.tabbar))
</script>

<template>
  <div class="app-shell">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
    <AppTabbar v-if="showTabbar" />
  </div>
</template>

<style lang="scss" scoped>
.app-shell {
  min-height: 100vh;
}
</style>
