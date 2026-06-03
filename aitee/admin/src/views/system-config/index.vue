<script setup lang="ts">
import CrudPage from '@/components/CrudPage.vue'
import { SystemConfigApi } from '@/api/admin'

const fields = [
  { prop: 'id', label: 'ID', width: 80, hideInForm: true },
  { prop: 'key', label: 'Key', required: true, width: 220 },
  { prop: 'value', label: '值(JSON)', type: 'json' as const, placeholder: '{"price": 49}' },
  { prop: 'description', label: '说明' },
  { prop: 'category', label: '分类', type: 'select' as const,
    options: [
      { label: '通用 general', value: 'general' },
      { label: '价格 pricing', value: 'pricing' },
      { label: '分润 profit', value: 'profit' },
      { label: '渠道 channel', value: 'channel' },
      { label: 'AI ai', value: 'ai' },
    ] },
]
</script>
<template>
  <CrudPage title="系统配置" :fields="fields" :api="SystemConfigApi" />
</template>
