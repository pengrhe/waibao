<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { PortalShell, useAuthStore } from '@aitee/shared'
import { modules } from '../modules'

const auth = useAuthStore()
const route = useRoute()

// 当前模块按 token role 决定（防止串号）
const current = computed(() => {
  const role = auth.user?.role ?? (route.params.role as keyof typeof modules)
  return modules[role as keyof typeof modules] ?? modules.partner
})
</script>

<template>
  <PortalShell :brand="current.brand" :menus="current.menus" />
</template>
