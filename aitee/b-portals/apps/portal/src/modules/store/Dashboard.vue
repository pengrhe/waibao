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
          <div class="muted" style="font-size: 12px; margin-top: 4px">加盟店 · M1 演示账号</div>
        </div>
        <van-tag :color="'#16a34a'" round>已登录</van-tag>
      </div>
    </div>

    <div class="portal-card">
      <van-grid :column-num="2" :gutter="0" :border="false">
        <van-grid-item>
          <div class="muted" style="font-size:12px">今日订单</div>
          <div style="font-size:22px; font-weight:800; color:#16a34a">—</div>
        </van-grid-item>
        <van-grid-item>
          <div class="muted" style="font-size:12px">今日营收</div>
          <div style="font-size:22px; font-weight:800; color:#16a34a">— 元</div>
        </van-grid-item>
        <van-grid-item>
          <div class="muted" style="font-size:12px">本月结算</div>
          <div style="font-size:18px; font-weight:700">— 元</div>
        </van-grid-item>
        <van-grid-item>
          <div class="muted" style="font-size:12px">在线设备</div>
          <div style="font-size:18px; font-weight:700">—</div>
        </van-grid-item>
      </van-grid>
    </div>

    <div class="portal-card">
      <div style="font-weight: 700; margin-bottom: 8px">M1 状态</div>
      <div class="muted" style="font-size: 13px; line-height: 1.8">
        本端已接通后端登录，业务页面（设备 / 结算 / 优惠）M2 实装。
      </div>
    </div>
  </div>
</template>
