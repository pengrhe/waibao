<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ModelChannelApi } from '@/api/admin'

const list = ref<any[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const form = reactive<any>({
  name: '',
  provider: 'openrouter',
  base_url: 'https://openrouter.ai/api/v1',
  api_key: '',
  model_name: '',
  enabled: true,
  is_active: false,
  remark: '',
})

async function fetchList() {
  loading.value = true
  try {
    const d: any = await ModelChannelApi.list()
    list.value = d.items || []
  } finally { loading.value = false }
}

function openCreate() {
  editingId.value = null
  Object.assign(form, { name: '', provider: 'openrouter', base_url: 'https://openrouter.ai/api/v1', api_key: '', model_name: '', enabled: true, is_active: false, remark: '' })
  dialogVisible.value = true
}

function openEdit(row: any) {
  editingId.value = row.id
  Object.assign(form, row, { api_key: '' })
  dialogVisible.value = true
}

async function submit() {
  if (!form.name || !form.model_name) { ElMessage.error('名称和 model_name 必填'); return }
  if (editingId.value) {
    await ModelChannelApi.update(editingId.value, form)
    ElMessage.success('更新成功')
  } else {
    await ModelChannelApi.create(form)
    ElMessage.success('已新建')
  }
  dialogVisible.value = false
  fetchList()
}

async function remove(row: any) {
  await ElMessageBox.confirm(`删除模型通道 ${row.name}？`, '提示', { type: 'warning' })
  await ModelChannelApi.remove(row.id)
  fetchList()
}

async function activate(row: any) {
  await ModelChannelApi.activate(row.id)
  ElMessage.success('已切换为 active')
  fetchList()
}

onMounted(fetchList)
</script>

<template>
  <div class="crud">
    <div class="crud-header">
      <h2 class="crud-title">AI 模型通道</h2>
      <div>
        <el-button @click="fetchList">刷新</el-button>
        <el-button type="primary" @click="openCreate">+ 新增通道</el-button>
      </div>
    </div>
    <el-card shadow="never" body-style="padding:0">
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="name" label="通道名称" min-width="140" />
        <el-table-column prop="provider" label="供应商" width="120" />
        <el-table-column prop="model_name" label="模型" min-width="200" />
        <el-table-column prop="api_key" label="API Key" width="200" />
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.is_active" type="success">激活中</el-tag>
            <el-tag v-else-if="row.enabled" type="info">启用</el-tag>
            <el-tag v-else type="danger">停用</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="140" />
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button v-if="!row.is_active" size="small" type="primary" @click="activate(row)">设为激活</el-button>
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑通道' : '新建通道'" width="560px" destroy-on-close>
      <el-form :model="form" label-width="100px">
        <el-form-item label="通道名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="供应商">
          <el-select v-model="form.provider">
            <el-option label="OpenRouter" value="openrouter" />
            <el-option label="OpenAI" value="openai" />
            <el-option label="Anthropic" value="anthropic" />
            <el-option label="Stub (占位)" value="stub" />
          </el-select>
        </el-form-item>
        <el-form-item label="base_url"><el-input v-model="form.base_url" /></el-form-item>
        <el-form-item label="API Key">
          <el-input v-model="form.api_key" type="password" :placeholder="editingId ? '留空表示不修改' : 'sk-or-v1-...'" show-password />
        </el-form-item>
        <el-form-item label="model_name"><el-input v-model="form.model_name" placeholder="google/gemini-3-pro 等" /></el-form-item>
        <el-form-item label="启用"><el-switch v-model="form.enabled" /></el-form-item>
        <el-form-item label="激活"><el-switch v-model="form.is_active" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="form.remark" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submit">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.crud { padding: 16px; }
.crud-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.crud-title { font-size: 18px; font-weight: 700; margin: 0; }
</style>
