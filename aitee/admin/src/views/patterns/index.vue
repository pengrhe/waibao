<script setup lang="ts">
import CrudPage from '@/components/CrudPage.vue'
import { PatternApi } from '@/api/admin'

const fields = [
  { prop: 'id', label: 'ID', width: 80, hideInForm: true },
  { prop: 'category_id', label: '分类 ID', type: 'number' as const, width: 100 },
  { prop: 'name', label: '名称', required: true },
  { prop: 'image_url', label: '图片 URL', required: true },
  { prop: 'thumb_url', label: '缩略图' },
  { prop: 'tags', label: '标签(JSON 数组)', type: 'json' as const, hideInTable: true,
    placeholder: '["国潮","原创"]' },
  { prop: 'source', label: '来源', type: 'select' as const,
    options: [
      { label: '内置', value: 'builtin' },
      { label: 'AI', value: 'ai' },
      { label: '用户', value: 'user' },
    ] },
  { prop: 'sort', label: '排序', type: 'number' as const, width: 90 },
  { prop: 'enabled', label: '启用', type: 'switch' as const, width: 90 },
]
</script>
<template>
  <CrudPage title="印花库" :fields="fields" :api="PatternApi" />
</template>
