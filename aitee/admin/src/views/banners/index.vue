<script setup lang="ts">
import CrudPage from '@/components/CrudPage.vue'
import { BannerApi } from '@/api/admin'

const fields = [
  { prop: 'id', label: 'ID', width: 80, hideInForm: true },
  { prop: 'position', label: '位置', required: true, type: 'select' as const,
    options: [
      { label: '首页顶部', value: 'home_top' },
      { label: '首页中部', value: 'home_mid' },
      { label: '首页推荐', value: 'home_recommend' },
      { label: '我的页邀请', value: 'mine_invite' },
    ] },
  { prop: 'title', label: '标题' },
  { prop: 'image_url', label: '图片 URL', required: true },
  { prop: 'link_to', label: '跳转链接' },
  { prop: 'sort', label: '排序', type: 'number' as const, width: 90 },
  { prop: 'enabled', label: '启用', type: 'switch' as const, width: 90 },
]
</script>
<template>
  <CrudPage title="Banner 管理" :fields="fields" :api="BannerApi" />
</template>
