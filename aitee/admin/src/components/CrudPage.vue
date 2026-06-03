<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

export interface CrudField {
  prop: string
  label: string
  type?: 'input' | 'textarea' | 'number' | 'switch' | 'select' | 'json' | 'date'
  options?: { label: string; value: any }[]
  placeholder?: string
  required?: boolean
  span?: number
  hideInForm?: boolean
  hideInTable?: boolean
  /** 表格列宽 */
  width?: number | string
  format?: (val: any, row: any) => any
}

interface Api {
  list: (params?: any) => Promise<any>
  create?: (data: any) => Promise<any>
  update?: (id: number, data: any) => Promise<any>
  remove?: (id: number) => Promise<any>
  toggle?: (id: number) => Promise<any>
}

const props = defineProps<{
  title: string
  fields: CrudField[]
  api: Api
  searchable?: boolean
  pagination?: boolean
  defaultForm?: () => Record<string, any>
}>()

const loading = ref(false)
const list = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const keyword = ref('')

const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const form = reactive<Record<string, any>>({})

function resetForm() {
  for (const k of Object.keys(form)) delete form[k]
  const d = props.defaultForm ? props.defaultForm() : {}
  for (const f of props.fields) {
    if (f.hideInForm) continue
    form[f.prop] = d[f.prop] ?? (f.type === 'switch' ? true : f.type === 'number' ? 0 : '')
  }
  Object.assign(form, d)
}

async function fetchList() {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize.value }
    if (keyword.value) params.keyword = keyword.value
    const data: any = await props.api.list(params)
    list.value = data.items || []
    total.value = data.total ?? list.value.length
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  resetForm()
  dialogVisible.value = true
}

function openEdit(row: any) {
  editingId.value = row.id
  resetForm()
  for (const f of props.fields) {
    if (f.hideInForm) continue
    form[f.prop] = row[f.prop]
  }
  dialogVisible.value = true
}

async function submit() {
  const payload: any = {}
  for (const f of props.fields) {
    if (f.hideInForm) continue
    let v = form[f.prop]
    if (f.type === 'json' && typeof v === 'string' && v) {
      try {
        v = JSON.parse(v)
      } catch {
        ElMessage.error(`${f.label} JSON 格式错误`)
        return
      }
    }
    if (f.required && (v === '' || v === null || v === undefined)) {
      ElMessage.error(`${f.label} 必填`)
      return
    }
    payload[f.prop] = v
  }
  try {
    if (editingId.value) {
      if (!props.api.update) throw new Error('no update api')
      await props.api.update(editingId.value, payload)
      ElMessage.success('更新成功')
    } else {
      if (!props.api.create) throw new Error('no create api')
      await props.api.create(payload)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    await fetchList()
  } catch (e: any) {
    // axios error msg 已在 interceptor 弹
  }
}

async function remove(row: any) {
  try {
    await ElMessageBox.confirm(`确定删除 #${row.id}？`, '提示', { type: 'warning' })
    if (!props.api.remove) return
    await props.api.remove(row.id)
    ElMessage.success('已删除')
    fetchList()
  } catch {}
}

async function toggle(row: any) {
  if (!props.api.toggle) return
  await props.api.toggle(row.id)
  fetchList()
}

function jsonStringify(v: any): string {
  if (v == null) return ''
  if (typeof v === 'string') return v
  return JSON.stringify(v, null, 2)
}

onMounted(fetchList)

defineExpose({ fetchList })
</script>

<template>
  <div class="crud">
    <div class="crud-header">
      <h2 class="crud-title">{{ title }}</h2>
      <div class="crud-actions">
        <el-input
          v-if="searchable !== false"
          v-model="keyword"
          placeholder="搜索关键字"
          style="width: 220px; margin-right: 8px"
          clearable
          @keyup.enter="fetchList"
          @clear="fetchList"
        />
        <el-button @click="fetchList">刷新</el-button>
        <el-button type="primary" @click="openCreate" v-if="api.create">+ 新增</el-button>
      </div>
    </div>

    <el-card shadow="never" body-style="padding:0">
      <el-table :data="list" v-loading="loading" stripe size="default">
        <template v-for="col in fields.filter((f) => !f.hideInTable)" :key="col.prop">
          <el-table-column :prop="col.prop" :label="col.label" :width="col.width">
            <template #default="{ row }">
              <template v-if="col.type === 'switch'">
                <el-tag :type="row[col.prop] ? 'success' : 'info'">{{ row[col.prop] ? '启用' : '停用' }}</el-tag>
              </template>
              <template v-else-if="col.type === 'json'">
                <code style="font-size: 11px; color: #64748b">{{ jsonStringify(row[col.prop]).slice(0, 60) }}</code>
              </template>
              <template v-else-if="col.format">
                {{ col.format(row[col.prop], row) }}
              </template>
              <template v-else>{{ row[col.prop] }}</template>
            </template>
          </el-table-column>
        </template>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button size="small" v-if="api.update" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" v-if="api.toggle" @click="toggle(row)">切换</el-button>
            <el-button size="small" type="danger" v-if="api.remove" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="pagination !== false" style="padding: 12px; display: flex; justify-content: flex-end">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="fetchList"
        />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑' : '新增'" width="640px" destroy-on-close>
      <el-form :model="form" label-width="100px">
        <el-form-item
          v-for="f in fields.filter((x) => !x.hideInForm)"
          :key="f.prop"
          :label="f.label"
          :required="f.required"
        >
          <el-input v-if="!f.type || f.type === 'input'" v-model="form[f.prop]" :placeholder="f.placeholder" />
          <el-input
            v-else-if="f.type === 'textarea'"
            v-model="form[f.prop]"
            type="textarea"
            :rows="3"
            :placeholder="f.placeholder"
          />
          <el-input-number v-else-if="f.type === 'number'" v-model="form[f.prop]" :min="0" />
          <el-switch v-else-if="f.type === 'switch'" v-model="form[f.prop]" />
          <el-select v-else-if="f.type === 'select'" v-model="form[f.prop]" :placeholder="f.placeholder">
            <el-option v-for="o in f.options || []" :key="o.value" :label="o.label" :value="o.value" />
          </el-select>
          <el-input
            v-else-if="f.type === 'json'"
            type="textarea"
            :rows="4"
            v-model="form[f.prop]"
            :placeholder="f.placeholder || '请输入合法 JSON'"
          />
          <el-date-picker v-else-if="f.type === 'date'" v-model="form[f.prop]" type="datetime" style="width: 100%" />
        </el-form-item>
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
.crud-actions { display: flex; align-items: center; }
</style>
