<script setup lang="ts">
import { ref } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import BrandHeader from '../../components/BrandHeader.vue'
import { Address } from '../../api'

const list = ref<any[]>([])
const picker = ref(false)

onLoad((opt) => { picker.value = opt?.picker === '1' })
onShow(load)

async function load() {
  try { list.value = await Address.list() } catch {}
}

async function setDefault(a: any, e: any) {
  e?.stopPropagation?.()
  await Address.update(a.id, { ...a, is_default: true })
  uni.showToast({ title: '已设为默认', icon: 'success' })
  load()
}

async function remove(a: any, e: any) {
  e?.stopPropagation?.()
  uni.showModal({
    title: '删除地址？',
    content: `${a.province}${a.city}${a.district} ${a.detail}`,
    success: async (r) => {
      if (r.confirm) {
        await Address.remove(a.id)
        uni.showToast({ title: '已删除', icon: 'success' })
        load()
      }
    },
  })
}

function add() {
  uni.navigateTo({ url: '/pages/address-edit/index' })
}

function edit(a: any, e: any) {
  e?.stopPropagation?.()
  uni.navigateTo({ url: `/pages/address-edit/index?id=${a.id}` })
}

function pick(a: any) {
  if (!picker.value) return
  Address.update(a.id, { ...a, is_default: true }).then(() => {
    uni.$emit('aitee:picked-address', { ...a, is_default: true })
    uni.navigateBack()
  })
}
</script>

<template>
  <view class="addr">
    <BrandHeader title="收货地址" show-back :show-logo="false" />

    <view v-if="!list.length" class="empty">
      <text class="empty__icon">📍</text>
      <text class="empty__text">还没有地址</text>
    </view>

    <view v-else class="list">
      <view
        v-for="a in list"
        :key="a.id"
        class="card"
        :class="{ 'card--picker': picker }"
        @click="pick(a)"
      >
        <view class="card__header">
          <text class="card__name">{{ a.receiver }}</text>
          <text class="card__phone">{{ a.phone }}</text>
          <text v-if="a.is_default" class="badge">默认</text>
        </view>
        <text class="card__detail">{{ a.province }}{{ a.city }}{{ a.district }} {{ a.detail }}</text>
        <view class="card__actions">
          <view
            v-if="!a.is_default"
            class="card__action"
            @click="setDefault(a, $event)"
          >
            <text>○</text>
            <text>设为默认</text>
          </view>
          <view v-else class="card__action card__action--default">
            <text>✓</text>
            <text>默认</text>
          </view>
          <view class="card__action" @click="edit(a, $event)">
            <text>✎</text>
            <text>编辑</text>
          </view>
          <view class="card__action" @click="remove(a, $event)">
            <text>🗑</text>
            <text>删除</text>
          </view>
        </view>
      </view>
    </view>

    <view class="bar">
      <view class="bar__btn" @click="add">
        <text>+ 新增收货地址</text>
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.addr { min-height: 100vh; background: $color-bg-page; padding-bottom: 80px; }

.empty { text-align: center; padding: 80px 24px; color: $color-text-secondary;
  &__icon { display: block; font-size: 64px; color: $color-text-placeholder; margin-bottom: 12px; }
  &__text { display: block; }
}

.list { padding: 12px; display: flex; flex-direction: column; gap: 12px; }

.card {
  background: #fff;
  border-radius: 12px;
  padding: 12px 14px;
  &__header { display: flex; align-items: center; gap: 12px; font-size: 14px; }
  &__name { font-weight: 700; }
  &__phone { color: $color-text-secondary; font-size: 13px; }
  &__detail { display: block; margin-top: 6px; font-size: 13px; color: $color-text-regular; }
  &__actions {
    margin-top: 12px;
    border-top: 1px dashed $color-divider;
    padding-top: 8px;
    display: flex;
    justify-content: space-around;
  }
  &__action {
    display: inline-flex; align-items: center; gap: 4px;
    color: $color-text-secondary;
    font-size: 12px;
    &--default { color: $color-primary; font-weight: 600; }
  }
}

.badge {
  background: $color-primary-light;
  color: $color-primary;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 700;
}

.bar {
  position: fixed; bottom: 0; left: 0; right: 0;
  background: #fff;
  border-top: 1px solid $color-divider;
  padding: 10px 16px;
  z-index: 9;
}
.bar__btn {
  height: 40px; line-height: 40px;
  border-radius: 999px;
  background: linear-gradient(135deg, #ff7a2a, #ff4d4f);
  color: #fff;
  font-size: 14px; font-weight: 700;
  text-align: center;
  box-shadow: 0 4px 14px rgba(255,77,79,.3);
}
</style>
