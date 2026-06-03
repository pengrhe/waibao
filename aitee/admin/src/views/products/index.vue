<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ProductApi, ProductCategoryApi } from '@/api/admin'

const list = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const keyword = ref('')
const loading = ref(false)

const categories = ref<any[]>([])

const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const form = reactive<any>({
  category_id: null,
  name: '',
  subtitle: '',
  base_price: 49,
  main_image_url: '',
  gallery: '',
  description: '',
  available_colors: 'white,black',
  available_sizes: 'S,M,L,XL',
  enabled: true,
  sort: 0,
  skus: [] as any[],
})

async function fetchList() {
  loading.value = true
  try {
    const data: any = await ProductApi.list({ page: page.value, page_size: pageSize.value, keyword: keyword.value })
    list.value = data.items || []
    total.value = data.total || 0
  } finally {
    loading.value = false
  }
}

async function fetchCategories() {
  const d: any = await ProductCategoryApi.list({ page_size: 100 })
  categories.value = d.items || []
}

function openCreate() {
  editingId.value = null
  Object.assign(form, {
    category_id: null, name: '', subtitle: '', base_price: 49, main_image_url: '',
    gallery: '', description: '', available_colors: 'white,black',
    available_sizes: 'S,M,L,XL', enabled: true, sort: 0, skus: [],
  })
  addSku()
  dialogVisible.value = true
}

function openEdit(row: any) {
  editingId.value = row.id
  Object.assign(form, row, {
    gallery: Array.isArray(row.gallery) ? row.gallery.join('\n') : (row.gallery || ''),
    available_colors: Array.isArray(row.available_colors) ? row.available_colors.join(',') : '',
    available_sizes: Array.isArray(row.available_sizes) ? row.available_sizes.join(',') : '',
    skus: (row.skus || []).map((s: any) => ({ ...s })),
  })
  dialogVisible.value = true
}

function addSku() {
  form.skus.push({ color: 'white', size: 'M', price: form.base_price, stock: 999, enabled: true })
}

function removeSku(idx: number) {
  form.skus.splice(idx, 1)
}

async function submit() {
  if (!form.name) { ElMessage.error('请输入商品名'); return }
  if (!form.skus.length) { ElMessage.error('至少 1 个 SKU'); return }
  const payload: any = {
    category_id: form.category_id || null,
    name: form.name,
    subtitle: form.subtitle,
    base_price: form.base_price,
    main_image_url: form.main_image_url,
    gallery: form.gallery ? form.gallery.split('\n').map((s: string) => s.trim()).filter(Boolean) : [],
    description: form.description,
    available_colors: form.available_colors ? form.available_colors.split(',').map((s: string) => s.trim()) : [],
    available_sizes: form.available_sizes ? form.available_sizes.split(',').map((s: string) => s.trim()) : [],
    enabled: form.enabled,
    sort: form.sort,
    skus: form.skus,
  }
  if (editingId.value) {
    await ProductApi.update(editingId.value, payload)
    ElMessage.success('更新成功')
  } else {
    await ProductApi.create(payload)
    ElMessage.success('创建成功')
  }
  dialogVisible.value = false
  fetchList()
}

async function remove(row: any) {
  await ElMessageBox.confirm(`删除商品 ${row.name}？`, '提示', { type: 'warning' })
  await ProductApi.remove(row.id)
  ElMessage.success('已删除')
  fetchList()
}

async function toggle(row: any) {
  await ProductApi.toggle(row.id)
  fetchList()
}

onMounted(() => {
  fetchList()
  fetchCategories()
})
</script>

<template>
  <div class="crud">
    <div class="crud-header">
      <h2 class="crud-title">商品管理</h2>
      <div>
        <el-input v-model="keyword" placeholder="商品名" style="width:220px;margin-right:8px" @keyup.enter="fetchList" clearable @clear="fetchList" />
        <el-button @click="fetchList">刷新</el-button>
        <el-button type="primary" @click="openCreate">+ 新增商品</el-button>
      </div>
    </div>
    <el-card shadow="never" body-style="padding:0">
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column label="主图" width="80">
          <template #default="{ row }">
            <el-image v-if="row.main_image_url" :src="row.main_image_url" style="width:48px;height:48px;border-radius:6px" fit="cover" />
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" min-width="160" />
        <el-table-column prop="base_price" label="基础价" width="100">
          <template #default="{ row }">¥ {{ row.base_price }}</template>
        </el-table-column>
        <el-table-column label="SKU 数" width="80">
          <template #default="{ row }">{{ row.skus?.length || 0 }}</template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'">{{ row.enabled ? '上架' : '下架' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" @click="toggle(row)">{{ row.enabled ? '下架' : '上架' }}</el-button>
            <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="padding:12px;display:flex;justify-content:flex-end">
        <el-pagination v-model:current-page="page" v-model:page-size="pageSize" :total="total" layout="total, prev, pager, next" @current-change="fetchList" />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑商品' : '新建商品'" width="780px" destroy-on-close>
      <el-form :model="form" label-width="100px">
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="商品名">
              <el-input v-model="form.name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="分类">
              <el-select v-model="form.category_id" placeholder="选择分类" clearable>
                <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="基础价">
              <el-input-number v-model="form.base_price" :min="0" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="排序">
              <el-input-number v-model="form.sort" :min="0" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="副标题">
              <el-input v-model="form.subtitle" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="主图 URL">
              <el-input v-model="form.main_image_url" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="图集(每行一条)">
              <el-input v-model="form.gallery" type="textarea" :rows="2" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="可选颜色(逗号)"><el-input v-model="form.available_colors" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="可选尺码(逗号)"><el-input v-model="form.available_sizes" /></el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="详情">
              <el-input v-model="form.description" type="textarea" :rows="2" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="启用">
              <el-switch v-model="form.enabled" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider>SKU 列表</el-divider>
        <el-table :data="form.skus" border size="small">
          <el-table-column label="颜色" width="120">
            <template #default="{ row }">
              <el-input v-model="row.color" />
            </template>
          </el-table-column>
          <el-table-column label="尺码" width="100">
            <template #default="{ row }">
              <el-input v-model="row.size" />
            </template>
          </el-table-column>
          <el-table-column label="价格" width="120">
            <template #default="{ row }">
              <el-input-number v-model="row.price" :min="0" :step="1" />
            </template>
          </el-table-column>
          <el-table-column label="库存" width="120">
            <template #default="{ row }">
              <el-input-number v-model="row.stock" :min="0" :step="10" />
            </template>
          </el-table-column>
          <el-table-column label="启用" width="80">
            <template #default="{ row }">
              <el-switch v-model="row.enabled" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80">
            <template #default="{ $index }">
              <el-button size="small" type="danger" link @click="removeSku($index)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div style="margin-top: 8px">
          <el-button size="small" @click="addSku">+ 增加 SKU</el-button>
        </div>
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
.crud-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.crud-title { font-size: 18px; font-weight: 700; margin: 0; }
</style>
