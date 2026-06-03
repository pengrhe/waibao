<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast } from 'vant'
import NavBar from '@/components/NavBar.vue'
import { listAddresses, saveAddress } from '@/api/address'

const route = useRoute()
const router = useRouter()

const id = (route.query.id as string) || ''
const form = ref({
  id: '' as string | undefined,
  name: '',
  phone: '',
  region: '',
  detail: '',
  isDefault: false,
})

const regionPresets = [
  '广东省 深圳市 南山区',
  '广东省 深圳市 福田区',
  '广东省 深圳市 罗湖区',
  '广东省 广州市 天河区',
  '北京市 朝阳区',
  '上海市 浦东新区',
  '湖南省 长沙市 岳麓区',
]

onMounted(async () => {
  if (!id) return
  const list = await listAddresses()
  const target = list.find((a) => a.id === id)
  if (target) {
    form.value = { ...target }
  }
})

async function submit() {
  if (!form.value.name.trim()) return showToast('请填写收货人')
  if (!/^1\d{10}$/.test(form.value.phone)) return showToast('请填写正确的手机号')
  if (!form.value.region) return showToast('请选择地区')
  if (!form.value.detail.trim()) return showToast('请填写详细地址')
  await saveAddress(form.value)
  showToast({ type: 'success', message: id ? '已更新' : '已保存' })
  setTimeout(() => router.back(), 600)
}
</script>

<template>
  <div class="ed">
    <NavBar :title="id ? '编辑地址' : '新增地址'" />

    <div class="form">
      <label class="row">
        <span class="row__label">收货人</span>
        <input v-model="form.name" class="row__input" placeholder="请输入" />
      </label>
      <label class="row">
        <span class="row__label">手机号</span>
        <input v-model="form.phone" class="row__input" maxlength="11" placeholder="请输入手机号" />
      </label>
      <label class="row">
        <span class="row__label">所在地区</span>
        <select v-model="form.region" class="row__input">
          <option value="">请选择</option>
          <option v-for="r in regionPresets" :key="r" :value="r">{{ r }}</option>
        </select>
      </label>
      <label class="row row--multiline">
        <span class="row__label">详细地址</span>
        <textarea v-model="form.detail" rows="2" class="row__input row__textarea" placeholder="街道、楼栋、门牌号" />
      </label>
      <label class="row row--switch">
        <span class="row__label">设为默认地址</span>
        <span class="switch" :class="{ 'switch--on': form.isDefault }" @click="form.isDefault = !form.isDefault">
          <span class="switch__dot" />
        </span>
      </label>
    </div>

    <div class="bar">
      <button class="bar__btn" @click="submit">保存</button>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.ed {
  min-height: 100vh;
  background: $color-bg-page;
  padding-bottom: 80px;
}

.form {
  background: #fff;
  margin: 12px;
  border-radius: 12px;
  padding: 4px 14px;
}

.row {
  display: flex;
  align-items: center;
  min-height: 50px;
  padding: 8px 0;
  border-bottom: 1px solid $color-divider;
  &:last-child {
    border-bottom: 0;
  }

  &__label {
    width: 86px;
    flex-shrink: 0;
    font-size: 14px;
    color: $color-text-primary;
  }

  &__input {
    flex: 1;
    border: none;
    outline: none;
    font-size: 14px;
    background: transparent;
    text-align: right;
  }

  &__textarea {
    text-align: left;
    padding: 4px 0;
    resize: none;
  }

  &--multiline {
    align-items: flex-start;
  }

  &--switch {
    justify-content: space-between;
  }
}

.switch {
  width: 44px;
  height: 24px;
  border-radius: $radius-pill;
  background: $color-bg-tag;
  position: relative;
  transition: background 0.2s;
  cursor: pointer;

  &__dot {
    position: absolute;
    top: 2px;
    left: 2px;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #fff;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
    transition: transform 0.2s;
  }

  &--on {
    background: $color-primary;
    .switch__dot {
      transform: translateX(20px);
    }
  }
}

.bar {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 480px;
  padding: 12px 16px;
  background: #fff;
  border-top: 1px solid $color-divider;
  z-index: 9;

  &__btn {
    width: 100%;
    height: 44px;
    border-radius: $radius-pill;
    background: $color-primary;
    color: #fff;
    font-weight: 700;
    font-size: 15px;
  }
}
</style>
