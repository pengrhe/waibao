<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<template>
  <div class="page">
    <div class="page-title">{{ route.meta?.title || '页面' }}</div>
    <div class="page-card">
      <div class="placeholder-tip">
        <h3>本页面 M2 待实现</h3>
        <p>路由：<code>{{ route.path }}</code></p>
        <p>骨架 M1 阶段先打通六端启动 + 鉴权，业务 CRUD 在 M2 逐个开。</p>
      </div>
    </div>
  </div>
</template>
