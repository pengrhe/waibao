<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { StoreApi } from '@/api/admin'

const list = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)
const keyword = ref('')
const statusFilter = ref('')

const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const form = reactive<any>({
  username: '', password: '', name: '', owner: '', phone: '',
  province: '', city: '', district: '', address: '',
  management_fee_ratio: 0.1, settle_mode: 'unified',
  bank_card: '', bank_name: '', status: 'active',
})

async function fetchList() {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize.value }
    if (keyword.value) params.keyword = keyword.value
    if (statusFilter.value) params.status_filter = statusFilter.value
    const d: any = await StoreApi.list(params)
    list.value = d.items || []
    total.value = d.total || 0
  } finally { loading.value = false }
}

function openCreate() {
  editingId.value = null
  Object.assign(form, { username: '', password: 'store123', name: '', owner: '', phone: '', province: '', city: '', district: '', address: '', management_fee_ratio: 0.1, settle_mode: 'unified', bank_card: '', bank_name: '', status: 'active' })
  dialogVisible.value = true
}

function openEdit(row: any) {
  editingId.value = row.id
  Object.assign(form, row, { password: '' })
  dialogVisible.value = true
}

async function submit() {
  if (!form.username || !form.name) { ElMessage.error('账号/名称必填'); return }
  if (editingId.value) {
    await StoreApi.update(editingId.value, form)
  } else {
    await StoreApi.create(form)
  }
  ElMessage.success('已保存')
  dialogVisible.value = false
  fetchList()
}

async function remove(row: any) {
  await ElMessageBox.confirm(`删除门店 ${row.name}？`, '提示', { type: 'warning' })
  await StoreApi.remove(row.id)
  fetchList()
}

async function audit(row: any, action: 'approve' | 'reject') {
  let reason = ''
  if (action === 'reject') {
    try {
      const { value } = await ElMessageBox.prompt('请输入驳回理由', '驳回', { type: 'warning' })
      reason = value
    } catch { return }
  }
  await StoreApi.audit(row.id, action, reason)
  fetchList()
}

onMounted(fetchList)
</script>

<template>
  <div class="crud">
    <div class="crud-header">
      <h2 class="crud-title">加盟门店</h2>
      <div>
        <el-input v-model="keyword" placeholder="账号/名称/城市" style="width:220px;margin-right:6px" clearable @keyup.enter="fetchList" @clear="fetchList" />
        <el-select v-model="statusFilter" placeholder="状态" style="width:120px;margin-right:6px" clearable @change="fetchList">
          <el-option label="待审核" value="pending" />
          <el-option label="已通过" value="active" />
          <el-option label="已驳回" value="rejected" />
          <el-option label="已禁用" value="disabled" />
        </el-select>
        <el-button @click="fetchList">查询</el-button>
        <el-button type="primary" @click="openCreate">+ 新增门店</el-button>
      </div>
    </div>
    <el-card shadow="never" body-style="padding:0">
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="name" label="店名" min-width="140" />
        <el-table-column prop="username" label="账号" width="120" />
        <el-table-column prop="owner" label="负责人" width="100" />
        <el-table-column prop="city" label="城市" width="100" />
        <el-table-column label="管理费" width="90">
          <template #default="{ row }">{{ (row.management_fee_ratio * 100).toFixed(0) }}%</template>
        </el-table-column>
        <el-table-column prop="settle_mode" label="结算" width="90" />
        <el-table-column label="余额" width="100">
          <template #default="{ row }">¥ {{ row.balance }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : row.status === 'rejected' ? 'danger' : 'info'">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'pending'" size="small" type="success" @click="audit(row, 'approve')">通过</el-button>
            <el-button v-if="row.status === 'pending'" size="small" type="warning" @click="audit(row, 'reject')">驳回</el-button>
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="padding:12px;display:flex;justify-content:flex-end">
        <el-pagination v-model:current-page="page" v-model:page-size="pageSize" :total="total" layout="total, prev, pager, next" @current-change="fetchList" />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑门店' : '新建门店'" width="640px" destroy-on-close>
      <el-form :model="form" label-width="100px">
        <el-row :gutter="12">
          <el-col :span="12"><el-form-item label="账号"><el-input v-model="form.username" :disabled="!!editingId" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="密码"><el-input v-model="form.password" type="password" :placeholder="editingId ? '留空不修改' : 'store123'" show-password /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="店名"><el-input v-model="form.name" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="负责人"><el-input v-model="form.owner" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="电话"><el-input v-model="form.phone" /></el-form-item></el-col>
          <el-col :span="6"><el-form-item label="省"><el-input v-model="form.province" /></el-form-item></el-col>
          <el-col :span="6"><el-form-item label="市"><el-input v-model="form.city" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="区"><el-input v-model="form.district" /></el-form-item></el-col>
          <el-col :span="24"><el-form-item label="详细地址"><el-input v-model="form.address" /></el-form-item></el-col>
          <el-col :span="12">
            <el-form-item label="管理费比例"><el-input-number v-model="form.management_fee_ratio" :min="0" :max="1" :step="0.01" :precision="4" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结算模式">
              <el-select v-model="form.settle_mode">
                <el-option label="自营结算 self" value="self" />
                <el-option label="统一结算 unified" value="unified" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12"><el-form-item label="银行卡"><el-input v-model="form.bank_card" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="开户行"><el-input v-model="form.bank_name" /></el-form-item></el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="form.status">
                <el-option label="待审核" value="pending" />
                <el-option label="已通过" value="active" />
                <el-option label="已驳回" value="rejected" />
                <el-option label="已禁用" value="disabled" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submit">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.crud { padding:16px; }
.crud-header { display:flex; justify-content:space-between; margin-bottom:12px; }
.crud-title { font-size:18px; font-weight:700; margin:0; }
</style>
