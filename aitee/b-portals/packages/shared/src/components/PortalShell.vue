<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showConfirmDialog } from 'vant'
import { useAuthStore } from '../auth'
import type { PortalBrand, PortalMenuItem } from '../types'

const props = defineProps<{
  brand: PortalBrand
  menus: PortalMenuItem[]
}>()

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const tabActive = computed(() => {
  const i = props.menus.findIndex((m) => m.path === route.path)
  return i < 0 ? 0 : i
})

function onChange(index: number) {
  const m = props.menus[index]
  if (m) router.push(m.path)
}

async function onLogout() {
  try {
    await showConfirmDialog({ title: '退出登录', message: '确认退出？' })
    auth.logout()
  } catch {
    /* canceled */
  }
}
</script>

<template>
  <div class="shell">
    <van-nav-bar :title="brand.name" left-text="" :border="false" class="shell__nav">
      <template #left>
        <span class="shell__logo" :style="{ background: brand.gradient, WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent' }">aitee</span>
        <span class="shell__sub">{{ brand.sub }}</span>
      </template>
      <template #right>
        <van-icon name="cross" class="shell__logout" @click="onLogout" />
      </template>
    </van-nav-bar>
    <div class="shell__body">
      <router-view />
    </div>
    <van-tabbar :model-value="tabActive" :active-color="brand.primary" @change="onChange" class="shell__tabbar" :border="true">
      <van-tabbar-item v-for="m in menus" :key="m.path" :icon="m.icon || 'apps-o'">{{ m.title }}</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<style scoped lang="scss">
.shell {
  min-height: 100vh;
  background: #f6f7fb;
  padding-bottom: 60px;

  &__nav {
    background: #fff;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
  }
  &__logo {
    font-weight: 900;
    font-size: 18px;
    letter-spacing: -0.5px;
  }
  &__sub {
    margin-left: 8px;
    color: #94a3b8;
    font-size: 12px;
  }
  &__logout {
    font-size: 18px;
    color: #94a3b8;
  }
  &__body {
    padding-top: 12px;
  }
}
</style>
