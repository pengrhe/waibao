<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { CityIpApi, CityIpItemApi, CulturalElementApi } from '@/api/admin'

const list = ref<any[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const form = reactive<any>({ city: '', description: '', cover_url: '' })

const itemDialog = ref(false)
const itemForm = reactive<any>({ city_ip_id: 0, category: 'landmark', title: '', image_url: '', sort: 0 })

const elemDialog = ref(false)
const elemForm = reactive<any>({ city: '', name: '', category: 'landmark', description: '', style_hint: '', enabled: true, sort: 0 })
const editingElemId = ref<number | null>(null)

async function fetchList() {
  loading.value = true
  try {
    const d: any = await CityIpApi.list()
    list.value = d.items || []
  } finally { loading.value = false }
}

function openCreate() {
  editingId.value = null
  Object.assign(form, { city: '', description: '', cover_url: '' })
  dialogVisible.value = true
}

function openEdit(row: any) {
  editingId.value = row.id
  Object.assign(form, { city: row.city, description: row.description || '', cover_url: row.cover_url || '' })
  dialogVisible.value = true
}

async function submit() {
  if (!form.city) { ElMessage.error('请输入城市'); return }
  if (editingId.value) {
    await CityIpApi.update(editingId.value, form)
  } else {
    await CityIpApi.create(form)
  }
  ElMessage.success('已保存')
  dialogVisible.value = false
  fetchList()
}

async function remove(row: any) {
  await ElMessageBox.confirm(`删除城市 ${row.city}（含全部子项）？`, '提示', { type: 'warning' })
  await CityIpApi.remove(row.id)
  fetchList()
}

function openAddItem(row: any) {
  Object.assign(itemForm, { city_ip_id: row.id, category: 'landmark', title: '', image_url: '', sort: 0 })
  itemDialog.value = true
}

async function submitItem() {
  if (!itemForm.title || !itemForm.image_url) { ElMessage.error('标题/图片必填'); return }
  await CityIpItemApi.create(itemForm)
  ElMessage.success('已添加')
  itemDialog.value = false
  fetchList()
}

async function removeItem(it: any) {
  await ElMessageBox.confirm('删除该子项？', '提示', { type: 'warning' })
  await CityIpItemApi.remove(it.id)
  fetchList()
}

function openAddElem(row: any) {
  editingElemId.value = null
  Object.assign(elemForm, { city: row.city, name: '', category: 'landmark', description: '', style_hint: '', enabled: true, sort: 0 })
  elemDialog.value = true
}

function openEditElem(row: any, e: any) {
  editingElemId.value = e.id
  Object.assign(elemForm, { city: row.city, name: e.name, category: e.category, description: e.description, style_hint: e.style_hint, enabled: e.enabled, sort: e.sort || 0 })
  elemDialog.value = true
}

async function submitElem() {
  if (!elemForm.name) { ElMessage.error('名称必填'); return }
  if (editingElemId.value) {
    await CulturalElementApi.update(editingElemId.value, elemForm)
  } else {
    await CulturalElementApi.create(elemForm)
  }
  elemDialog.value = false
  fetchList()
}

async function removeElem(e: any) {
  await ElMessageBox.confirm(`删除元素 ${e.name}？`, '提示', { type: 'warning' })
  await CulturalElementApi.remove(e.id)
  fetchList()
}

onMounted(fetchList)
</script>

<template>
  <div class="crud">
    <div class="crud-header">
      <h2 class="crud-title">城市 IP 库</h2>
      <div>
        <el-button @click="fetchList">刷新</el-button>
        <el-button type="primary" @click="openCreate">+ 新增城市</el-button>
      </div>
    </div>
    <el-card v-loading="loading" shadow="never">
      <el-collapse>
        <el-collapse-item v-for="c in list" :key="c.id" :name="String(c.id)">
          <template #title>
            <div style="display:flex;align-items:center;gap:12px">
              <strong>{{ c.city }}</strong>
              <span style="color:#94a3b8">{{ c.description || '—' }}</span>
              <el-tag size="small">items {{ c.items.length }}</el-tag>
              <el-tag size="small" type="info">elements {{ c.elements.length }}</el-tag>
            </div>
          </template>
          <div style="margin-bottom:12px">
            <el-button size="small" @click.stop="openEdit(c)">编辑城市</el-button>
            <el-button size="small" @click.stop="openAddItem(c)">+ 添加图项</el-button>
            <el-button size="small" @click.stop="openAddElem(c)">+ 添加元素</el-button>
            <el-button size="small" type="danger" @click.stop="remove(c)">删除城市</el-button>
          </div>

          <h4 style="margin:8px 0">图库（city_ip_items）</h4>
          <el-table :data="c.items" size="small" border>
            <el-table-column prop="category" label="类型" width="100" />
            <el-table-column prop="title" label="标题" min-width="120" />
            <el-table-column label="图" width="80">
              <template #default="{ row }">
                <el-image v-if="row.image_url" :src="row.image_url" style="width:40px;height:40px" fit="cover" />
              </template>
            </el-table-column>
            <el-table-column prop="sort" label="排序" width="60" />
            <el-table-column label="操作" width="80">
              <template #default="{ row }">
                <el-button size="small" type="danger" link @click="removeItem(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <h4 style="margin:12px 0 8px">文化元素（cultural_elements）</h4>
          <el-table :data="c.elements" size="small" border>
            <el-table-column prop="category" label="分类" width="100" />
            <el-table-column prop="name" label="名称" width="120" />
            <el-table-column prop="description" label="说明" min-width="160" />
            <el-table-column prop="style_hint" label="风格暗示" width="120" />
            <el-table-column label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.enabled ? 'success' : 'info'">{{ row.enabled ? '启用' : '停用' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="160">
              <template #default="{ row }">
                <el-button size="small" @click="openEditElem(c, row)">编辑</el-button>
                <el-button size="small" type="danger" link @click="removeElem(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-collapse-item>
      </el-collapse>
    </el-card>

    <!-- 城市 dialog -->
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑城市' : '新建城市'" width="520px" destroy-on-close>
      <el-form :model="form" label-width="80px">
        <el-form-item label="城市"><el-input v-model="form.city" :disabled="!!editingId" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" /></el-form-item>
        <el-form-item label="封面"><el-input v-model="form.cover_url" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submit">提交</el-button>
      </template>
    </el-dialog>

    <!-- 图项 dialog -->
    <el-dialog v-model="itemDialog" title="添加图项" width="520px" destroy-on-close>
      <el-form :model="itemForm" label-width="80px">
        <el-form-item label="类型">
          <el-select v-model="itemForm.category">
            <el-option label="地标" value="landmark" />
            <el-option label="民俗" value="folk" />
            <el-option label="符号" value="symbol" />
            <el-option label="美食" value="food" />
            <el-option label="方言" value="dialect" />
          </el-select>
        </el-form-item>
        <el-form-item label="标题"><el-input v-model="itemForm.title" /></el-form-item>
        <el-form-item label="图片 URL"><el-input v-model="itemForm.image_url" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="itemForm.sort" :min="0" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="itemDialog = false">取消</el-button>
        <el-button type="primary" @click="submitItem">提交</el-button>
      </template>
    </el-dialog>

    <!-- 元素 dialog -->
    <el-dialog v-model="elemDialog" :title="editingElemId ? '编辑元素' : '新建元素'" width="520px" destroy-on-close>
      <el-form :model="elemForm" label-width="80px">
        <el-form-item label="名称"><el-input v-model="elemForm.name" /></el-form-item>
        <el-form-item label="分类">
          <el-select v-model="elemForm.category">
            <el-option label="地标" value="landmark" />
            <el-option label="民俗" value="folk" />
            <el-option label="符号" value="symbol" />
            <el-option label="美食" value="food" />
            <el-option label="方言" value="dialect" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述"><el-input v-model="elemForm.description" /></el-form-item>
        <el-form-item label="风格暗示"><el-input v-model="elemForm.style_hint" /></el-form-item>
        <el-form-item label="启用"><el-switch v-model="elemForm.enabled" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="elemForm.sort" :min="0" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="elemDialog = false">取消</el-button>
        <el-button type="primary" @click="submitElem">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.crud { padding:16px; }
.crud-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; }
.crud-title { font-size:18px; font-weight:700; margin:0; }
</style>
