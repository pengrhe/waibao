<script setup lang="ts">
import { useAuthStore } from '@aitee/shared'

const auth = useAuthStore()
</script>

<template>
  <div class="portal-page">
    <div class="portal-card">
      <div style="display:flex; justify-content:space-between; align-items:center">
        <div>
          <div style="font-size: 16px; font-weight: 700">{{ auth.user?.name || auth.user?.username }}</div>
          <div class="muted" style="font-size: 12px; margin-top: 4px">店员 · 门店 ID {{ auth.user?.extra?.store_id ?? '—' }}</div>
        </div>
        <van-tag :color="'#ff7a2a'" round>已登录</van-tag>
      </div>
    </div>

    <div class="portal-card">
      <van-grid :column-num="2" :gutter="0" :border="false">
        <van-grid-item>
          <div class="muted" style="font-size:12px">待打印</div>
          <div style="font-size:22px; font-weight:800; color:#ff7a2a">—</div>
        </van-grid-item>
        <van-grid-item>
          <div class="muted" style="font-size:12px">待核销</div>
          <div style="font-size:22px; font-weight:800; color:#ff7a2a">—</div>
        </van-grid-item>
        <van-grid-item>
          <div class="muted" style="font-size:12px">今日完成</div>
          <div style="font-size:18px; font-weight:700">—</div>
        </van-grid-item>
        <van-grid-item>
          <div class="muted" style="font-size:12px">设备状态</div>
          <div style="font-size:18px; font-weight:700">就绪</div>
        </van-grid-item>
      </van-grid>
    </div>

    <div class="portal-card">
      <div style="font-weight: 700; margin-bottom: 8px">M1 状态</div>
      <div class="muted" style="font-size: 13px; line-height: 1.8">
        本端已接通后端登录，订单核销 / 录单 / 设备 等业务页面 M2 实装。
      </div>
    </div>
  </div>
</template>
