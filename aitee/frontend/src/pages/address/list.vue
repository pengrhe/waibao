<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showDialog, showToast } from 'vant'
import NavBar from '@/components/NavBar.vue'
import { deleteAddress, listAddresses, saveAddress } from '@/api/address'
import type { Address } from '@/types'

const route = useRoute()
const router = useRouter()

const list = ref<Address[]>([])
const isPicker = !!route.query.picker

async function load() {
  list.value = await listAddresses()
}

onMounted(load)

async function setDefault(a: Address, e: Event) {
  e.stopPropagation()
  list.value = await saveAddress({ ...a, isDefault: true })
  showToast('已设为默认')
}

async function remove(a: Address, e: Event) {
  e.stopPropagation()
  showDialog({ title: '删除地址？', message: `${a.region} ${a.detail}`, showCancelButton: true })
    .then(async () => {
      list.value = await deleteAddress(a.id)
      showToast('已删除')
    })
    .catch(() => {})
}

function add() {
  router.push('/address/edit')
}

function edit(a: Address, e: Event) {
  e.stopPropagation()
  router.push(`/address/edit?id=${a.id}`)
}

function pick(a: Address) {
  if (!isPicker) return
  // 设为默认（演示版简化）
  saveAddress({ ...a, isDefault: true }).then(() => {
    router.back()
  })
}
</script>

<template>
  <div class="addr">
    <NavBar title="收货地址" />

    <div v-if="!list.length" class="empty">
      <span class="i-material-symbols:location-on-outline-rounded empty__icon" />
      <p>还没有地址</p>
    </div>

    <ul v-else class="list">
      <li
        v-for="a in list"
        :key="a.id"
        class="card"
        :class="{ 'card--picker': isPicker }"
        @click="pick(a)"
      >
        <div class="card__header">
          <strong>{{ a.name }}</strong>
          <span>{{ a.phone }}</span>
          <span v-if="a.isDefault" class="badge">默认</span>
        </div>
        <div class="card__detail">{{ a.region }} {{ a.detail }}</div>
        <div class="card__actions">
          <button v-if="!a.isDefault" class="card__action" @click="setDefault(a, $event)">
            <span class="i-material-symbols:radio-button-unchecked-rounded" />
            设为默认
          </button>
          <span v-else class="card__action card__action--default">
            <span class="i-material-symbols:check-circle-rounded" />
            默认
          </span>
          <button class="card__action" @click="edit(a, $event)">
            <span class="i-material-symbols:edit-outline-rounded" />
            编辑
          </button>
          <button class="card__action" @click="remove(a, $event)">
            <span class="i-material-symbols:delete-outline-rounded" />
            删除
          </button>
        </div>
      </li>
    </ul>

    <div class="bar">
      <button class="bar__btn" @click="add">
        <span class="i-material-symbols:add-rounded" />
        新增收货地址
      </button>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.addr {
  min-height: 100vh;
  background: $color-bg-page;
  padding-bottom: 80px;
}

.empty {
  text-align: center;
  padding: 80px 24px;
  color: $color-text-secondary;
  &__icon {
    font-size: 64px;
    color: $color-text-placeholder;
    display: block;
    margin: 0 auto 12px;
  }
}

.list {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.card {
  background: #fff;
  border-radius: 12px;
  padding: 12px 14px;

  &__header {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 14px;
  }

  &__detail {
    margin-top: 6px;
    font-size: 13px;
    color: $color-text-regular;
  }

  &__actions {
    margin-top: 12px;
    border-top: 1px dashed $color-divider;
    padding-top: 8px;
    display: flex;
    justify-content: space-around;
  }

  &__action {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    color: $color-text-secondary;
    font-size: 12px;

    &--default {
      color: $color-primary;
      font-weight: 600;
    }
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
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 480px;
  height: 60px;
  background: #fff;
  border-top: 1px solid $color-divider;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9;

  &__btn {
    width: calc(100% - 32px);
    height: 40px;
    border-radius: $radius-pill;
    background: $color-primary;
    color: #fff;
    font-size: 14px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
  }
}
</style>
