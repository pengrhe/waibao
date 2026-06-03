<script setup lang="ts">
import CrudPage from '@/components/CrudPage.vue'
import { TopicApi } from '@/api/admin'

const fields = [
  { prop: 'id', label: 'ID', width: 80, hideInForm: true },
  { prop: 'title', label: '标题', required: true },
  { prop: 'subtitle', label: '副标题' },
  { prop: 'cover_url', label: '封面图' },
  { prop: 'link_to', label: '跳转链接' },
  { prop: 'items', label: '专区内容(JSON)', type: 'json' as const, hideInTable: true,
    placeholder: '[{"title": "国潮系列", "image": "..."}]' },
  { prop: 'sort', label: '排序', type: 'number' as const, width: 90 },
  { prop: 'enabled', label: '启用', type: 'switch' as const, width: 90 },
]
</script>
<template>
  <CrudPage title="首页专区" :fields="fields" :api="TopicApi" />
</template>
