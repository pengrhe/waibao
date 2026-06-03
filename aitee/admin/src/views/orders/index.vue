<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { OrderApi } from '@/api/admin'
import { formatBJT } from '@/utils/time'

const list = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)

const filters = reactive({
  keyword: '',
  status: '',
  channel: '',
  category: '',
  start_date: '',
  end_date: '',
})

const STATUSES = [
  { label: '全部', value: '' },
  { label: '待支付', value: 'pending_pay' },
  { label: '已支付', value: 'paid' },
  { label: '待打印', value: 'pending_print' },
  { label: '打印中', value: 'printing' },
  { label: '已打印', value: 'printed' },
  { label: '已取件', value: 'picked' },
  { label: '已完成', value: 'completed' },
  { label: '已取消', value: 'canceled' },
  { label: '已退款', value: 'refunded' },
]

const detailVisible = ref(false)
const detail = ref<any>(null)

async function fetchList() {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize.value }
    Object.entries(filters).forEach(([k, v]) => { if (v) params[k] = v })
    const d: any = await OrderApi.list(params)
    list.value = d.items || []
    total.value = d.total || 0
  } finally { loading.value = false }
}

function reset() {
  filters.keyword = ''
  filters.status = ''
  filters.channel = ''
  filters.category = ''
  filters.start_date = ''
  filters.end_date = ''
  page.value = 1
  fetchList()
}

async function openDetail(id: number) {
  const d: any = await OrderApi.detail(id)
  detail.value = d
  detailVisible.value = true
}

async function changeStatus(row: any, status: string) {
  await ElMessageBox.confirm(`将订单 ${row.order_no} 切到 ${status}？`, '提示', { type: 'warning' })
  await OrderApi.changeStatus(row.id, { status })
  ElMessage.success('已修改')
  fetchList()
  if (detail.value && detail.value.id === row.id) openDetail(row.id)
}

async function refund(row: any) {
  await ElMessageBox.confirm(`确定退款订单 ${row.order_no}？`, '提示', { type: 'warning' })
  await OrderApi.refund(row.id, { reason: 'admin 操作' })
  ElMessage.success('已退款')
  fetchList()
}

function exportCsv() {
  const params = new URLSearchParams()
  Object.entries(filters).forEach(([k, v]) => { if (v) params.append(k, String(v)) })
  const raw = localStorage.getItem('aitee_admin_auth') || ''
  let token = ''
  try { token = JSON.parse(raw).token } catch {}
  const url = `${OrderApi.exportUrl}?${params.toString()}`
  fetch(url, { headers: { Authorization: `Bearer ${token}` } })
    .then((r) => r.blob())
    .then((blob) => {
      const a = document.createElement('a')
      a.href = URL.createObjectURL(blob)
      a.download = `orders_${Date.now()}.csv`
      document.body.appendChild(a)
      a.click()
      a.remove()
    })
}

function statusType(s: string) {
  if (s === 'completed' || s === 'paid') return 'success'
  if (s === 'pending_pay') return 'warning'
  if (s === 'canceled' || s === 'refunded') return 'danger'
  return ''
}

onMounted(fetchList)
</script>

<template>
  <div class="crud">
    <div class="crud-header">
      <h2 class="crud-title">订单管理</h2>
    </div>
    <el-card shadow="never" style="margin-bottom:12px">
      <el-form :model="filters" inline>
        <el-form-item><el-input v-model="filters.keyword" placeholder="订单号/备注" clearable style="width:180px" /></el-form-item>
        <el-form-item>
          <el-select v-model="filters.status" placeholder="状态" clearable style="width:140px">
            <el-option v-for="s in STATUSES" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-select v-model="filters.channel" placeholder="渠道" clearable style="width:120px">
            <el-option label="H5" value="h5" />
            <el-option label="微信小程序" value="wx_app" />
            <el-option label="抖音小程序" value="dy_app" />
            <el-option label="门店扫码" value="offline_store" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-select v-model="filters.category" placeholder="分类" clearable style="width:120px">
            <el-option label="个人" value="personal" />
            <el-option label="企业批量" value="enterprise_batch" />
            <el-option label="城市 IP" value="city_ip" />
            <el-option label="门店" value="offline" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-date-picker v-model="filters.start_date" type="datetime" placeholder="起始时间" />
        </el-form-item>
        <el-form-item>
          <el-date-picker v-model="filters.end_date" type="datetime" placeholder="结束时间" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="page = 1; fetchList()">查询</el-button>
          <el-button @click="reset">重置</el-button>
          <el-button @click="exportCsv">导出 CSV</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never" body-style="padding:0">
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="order_no" label="订单号" width="220" />
        <el-table-column prop="user_phone" label="用户" width="120">
          <template #default="{ row }">{{ row.user_nickname }}<br><span style="color:#94a3b8">{{ row.user_phone }}</span></template>
        </el-table-column>
        <el-table-column prop="amount_total" label="实付" width="100">
          <template #default="{ row }">¥ {{ row.amount_total }}</template>
        </el-table-column>
        <el-table-column prop="channel" label="渠道" width="100" />
        <el-table-column prop="category" label="分类" width="100" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="180">
          <template #default="{ row }">{{ formatBJT(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openDetail(row.id)">详情</el-button>
            <el-button v-if="row.status === 'pending_print'" size="small" @click="changeStatus(row, 'printing')">开始打印</el-button>
            <el-button v-if="row.status === 'printing'" size="small" @click="changeStatus(row, 'printed')">打印完成</el-button>
            <el-button v-if="['paid','pending_print','printing','printed'].includes(row.status)" size="small" type="danger" @click="refund(row)">退款</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="padding:12px;display:flex;justify-content:flex-end">
        <el-pagination v-model:current-page="page" v-model:page-size="pageSize" :total="total" layout="total, prev, pager, next" @current-change="fetchList" />
      </div>
    </el-card>

    <el-drawer v-model="detailVisible" size="640px" :title="detail ? `订单 ${detail.order_no}` : '订单'">
      <template v-if="detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="状态"><el-tag :type="statusType(detail.status)">{{ detail.status }}</el-tag></el-descriptions-item>
          <el-descriptions-item label="实付">¥ {{ detail.amount_total }}</el-descriptions-item>
          <el-descriptions-item label="商品金额">¥ {{ detail.amount_goods }}</el-descriptions-item>
          <el-descriptions-item label="优惠">¥ {{ detail.amount_discount }}</el-descriptions-item>
          <el-descriptions-item label="渠道">{{ detail.channel }}</el-descriptions-item>
          <el-descriptions-item label="分类">{{ detail.category }}</el-descriptions-item>
          <el-descriptions-item label="支付时间">{{ formatBJT(detail.paid_at) }}</el-descriptions-item>
          <el-descriptions-item label="完成时间">{{ formatBJT(detail.completed_at) }}</el-descriptions-item>
          <el-descriptions-item label="用户">{{ detail.user_nickname }} ({{ detail.user_phone }})</el-descriptions-item>
          <el-descriptions-item label="备注">{{ detail.remark || '-' }}</el-descriptions-item>
        </el-descriptions>
        <h4 style="margin:16px 0 8px">商品明细</h4>
        <el-table :data="detail.items" size="small" border>
          <el-table-column label="预览" width="60">
            <template #default="{ row }">
              <el-image v-if="row.preview_url" :src="row.preview_url" style="width:40px;height:40px" fit="cover" />
            </template>
          </el-table-column>
          <el-table-column prop="name" label="名称" min-width="140" />
          <el-table-column prop="color" label="颜色" width="80" />
          <el-table-column prop="size" label="尺码" width="80" />
          <el-table-column prop="unit_price" label="单价" width="80" />
          <el-table-column prop="qty" label="数量" width="60" />
          <el-table-column prop="subtotal" label="小计" width="80" />
        </el-table>
        <h4 style="margin:16px 0 8px">状态流水</h4>
        <el-timeline>
          <el-timeline-item v-for="(l, i) in detail.logs" :key="i" :timestamp="formatBJT(l.at)" placement="top">
            <strong>{{ l.from || '—' }} → {{ l.to }}</strong>
            <div style="color:#94a3b8;font-size:12px">{{ l.by }} {{ l.reason || '' }}</div>
          </el-timeline-item>
        </el-timeline>
      </template>
    </el-drawer>
  </div>
</template>

<style scoped>
.crud { padding:16px; }
.crud-header { display:flex; justify-content:space-between; margin-bottom:12px; }
.crud-title { font-size:18px; font-weight:700; margin:0; }
</style>
