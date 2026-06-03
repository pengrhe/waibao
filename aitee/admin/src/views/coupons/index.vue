<script setup lang="ts">
import CrudPage from '@/components/CrudPage.vue'
import { CouponApi } from '@/api/admin'

const fields = [
  { prop: 'id', label: 'ID', width: 80, hideInForm: true },
  { prop: 'name', label: '券名', required: true },
  { prop: 'type', label: '类型', type: 'select' as const, required: true,
    options: [
      { label: '满减券 (cash)', value: 'cash' },
      { label: '折扣券 (discount)', value: 'discount' },
    ] },
  { prop: 'value', label: '面值/折扣', type: 'number' as const, required: true,
    placeholder: '满减填金额，折扣填 0~1（如 0.78 = 78折）' },
  { prop: 'threshold', label: '使用门槛', type: 'number' as const, placeholder: '满 X 元可用' },
  { prop: 'valid_days', label: '有效天数', type: 'number' as const, placeholder: '默认 30 天' },
  { prop: 'total', label: '发放上限', type: 'number' as const, placeholder: '0 = 不限' },
  { prop: 'claimed', label: '已领', width: 80, hideInForm: true },
  { prop: 'description', label: '说明', type: 'textarea' as const, hideInTable: true },
  { prop: 'status', label: '状态', type: 'select' as const,
    options: [
      { label: '上架', value: 'active' },
      { label: '下架', value: 'inactive' },
    ] },
]
</script>
<template>
  <CrudPage title="优惠券" :fields="fields" :api="CouponApi" />
</template>
