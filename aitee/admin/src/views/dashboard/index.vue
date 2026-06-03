<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { get } from '@/utils/request'

interface HealthData {
  status: string
  name: string
  env: string
  db: string
  version: string
}

const health = ref<HealthData | null>(null)
const loading = ref(true)

const tiles = [
  { title: '今日订单', value: '—', tip: 'M2 接入' },
  { title: '今日营收', value: '—', tip: 'M2 接入' },
  { title: '活跃门店', value: '—', tip: 'M2 接入' },
  { title: 'AI 出图次数', value: '—', tip: 'M2 接入' },
]

onMounted(async () => {
  try {
    health.value = await get<HealthData>('/health')
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="page">
    <div class="page-title">工作台</div>
    <el-row :gutter="16">
      <el-col v-for="t in tiles" :key="t.title" :span="6">
        <el-card shadow="never">
          <div style="display:flex; flex-direction:column; gap:8px">
            <span class="muted" style="font-size:12px">{{ t.title }}</span>
            <span style="font-size:28px; font-weight:800">{{ t.value }}</span>
            <span class="muted" style="font-size:12px">{{ t.tip }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never" style="margin-top:16px">
      <template #header><strong>后端连通性</strong></template>
      <div v-if="loading">检测中…</div>
      <div v-else-if="health">
        <el-tag :type="health.status === 'ok' ? 'success' : 'danger'">{{ health.status }}</el-tag>
        <span style="margin-left:8px">{{ health.name }} · {{ health.env }} · v{{ health.version }} · DB {{ health.db }}</span>
      </div>
      <div v-else>
        <el-tag type="danger">后端无响应</el-tag>
        <span style="margin-left:8px">请确认 backend 已启动在 http://127.0.0.1:8200</span>
      </div>
    </el-card>

    <el-card shadow="never" style="margin-top:16px">
      <template #header><strong>M1 完成度</strong></template>
      <ul style="line-height:2; margin:0; padding-left:18px; color:#475569">
        <li>backend：FastAPI + 38 张表 + admin/partner/store/staff 登录</li>
        <li>admin：登录 + 21 个菜单占位 + 路由守卫</li>
        <li>partner-web / store-web / staff-web：M1 同步搭建中</li>
        <li>miniapp：uniapp 微信 + 抖音双端骨架（M1 同步搭建中）</li>
      </ul>
    </el-card>
  </div>
</template>
