<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UserApi } from '@/api/admin'
import { formatBJT } from '@/utils/time'

const list = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const keyword = ref('')
const statusFilter = ref('')
const loading = ref(false)

async function fetchList() {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize.value }
    if (keyword.value) params.keyword = keyword.value
    if (statusFilter.value) params.status_filter = statusFilter.value
    const d: any = await UserApi.list(params)
    list.value = d.items || []
    total.value = d.total || 0
  } finally {
    loading.value = false
  }
}

async function disable(row: any) {
  await ElMessageBox.confirm(`禁用用户 ${row.nickname || row.phone}？`, '提示', { type: 'warning' })
  await UserApi.disable(row.id)
  ElMessage.success('已禁用')
  fetchList()
}

async function enable(row: any) {
  await UserApi.enable(row.id)
  ElMessage.success('已启用')
  fetchList()
}

onMounted(fetchList)
</script>

<template>
  <div class="crud">
    <div class="crud-header">
      <h2 class="crud-title">C 端用户</h2>
      <div>
        <el-input v-model="keyword" placeholder="手机号/昵称" style="width:200px;margin-right:6px" clearable @keyup.enter="fetchList" @clear="fetchList" />
        <el-select v-model="statusFilter" placeholder="状态" style="width:120px;margin-right:6px" clearable @change="fetchList">
          <el-option label="全部" value="" />
          <el-option label="正常" value="active" />
          <el-option label="禁用" value="disabled" />
        </el-select>
        <el-button @click="fetchList">查询</el-button>
      </div>
    </div>
    <el-card shadow="never" body-style="padding:0">
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column label="头像" width="60">
          <template #default="{ row }">
            <el-avatar :src="row.avatar_url" :size="32">{{ (row.nickname || 'A').charAt(0) }}</el-avatar>
          </template>
        </el-table-column>
        <el-table-column prop="nickname" label="昵称" min-width="120" />
        <el-table-column prop="phone" label="手机号" width="140" />
        <el-table-column prop="city" label="城市" width="100" />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="最近登录" width="180">
          <template #default="{ row }">{{ formatBJT(row.last_login_at) }}</template>
        </el-table-column>
        <el-table-column label="注册" width="180">
          <template #default="{ row }">{{ formatBJT(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'active'" size="small" type="warning" @click="disable(row)">禁用</el-button>
            <el-button v-else size="small" type="success" @click="enable(row)">启用</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="padding:12px;display:flex;justify-content:flex-end">
        <el-pagination v-model:current-page="page" v-model:page-size="pageSize" :total="total" layout="total, prev, pager, next" @current-change="fetchList" />
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.crud { padding:16px; }
.crud-header { display:flex; justify-content:space-between; margin-bottom:12px; }
.crud-title { font-size:18px; font-weight:700; margin:0; }
</style>
