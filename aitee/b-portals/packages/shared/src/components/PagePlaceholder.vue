<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<template>
  <div class="portal-page">
    <div class="portal-card" style="text-align:center; padding: 40px 20px; color:#94a3b8">
      <div style="font-size: 16px; font-weight: 700; color:#475569; margin-bottom: 8px">
        {{ route.meta?.title || '页面' }}
      </div>
      <div>本页面 M2 待实现</div>
      <div style="margin-top: 6px; font-size: 12px">路由 {{ route.path }}</div>
    </div>
  </div>
</template>
