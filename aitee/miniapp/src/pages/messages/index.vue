<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { Messages } from '../../api'

const list = ref<any[]>([])

async function load() {
  list.value = await Messages.list()
  Messages.readAll().catch(() => {})
}

onMounted(load)
onShow(load)

function open(m: any) {
  if (m.link_to) {
    uni.navigateTo({ url: m.link_to })
  }
}
</script>

<template>
  <view class="page">
    <view v-if="!list.length" class="empty">暂无消息</view>
    <view v-for="m in list" :key="m.id" class="msg" @click="open(m)">
      <view class="msg__title">
        <text>{{ m.title }}</text>
        <text class="msg__dot" v-if="!m.read_at"></text>
      </view>
      <view class="msg__body">{{ m.body }}</view>
      <view class="msg__time">{{ m.sent_at || m.created_at }}</view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.page { padding: 12px; }
.empty { text-align: center; color: #94a3b8; padding: 80px 0; }
.msg { background: #fff; border-radius: 12px; padding: 14px; margin-bottom: 10px;
  &__title { font-weight: 700; display: flex; align-items: center; }
  &__dot { width: 6px; height: 6px; border-radius: 3px; background: #ef4444; margin-left: 6px; }
  &__body { color: #475569; margin-top: 6px; font-size: 13px; line-height: 1.6; }
  &__time { color: #cbd5e1; font-size: 11px; margin-top: 6px; }
}
</style>
