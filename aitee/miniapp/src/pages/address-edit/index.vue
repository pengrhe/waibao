<script setup lang="ts">
import { reactive, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import BrandHeader from '../../components/BrandHeader.vue'
import { Address } from '../../api'

const id = ref<number | null>(null)
const form = reactive({
  receiver: '',
  phone: '',
  province: '广东省',
  city: '深圳市',
  district: '宝安区',
  detail: '',
  is_default: false,
})
const showRegionPicker = ref(false)

const regionPresets = [
  ['广东省', '深圳市', '南山区'],
  ['广东省', '深圳市', '福田区'],
  ['广东省', '深圳市', '罗湖区'],
  ['广东省', '深圳市', '宝安区'],
  ['广东省', '广州市', '天河区'],
  ['北京市', '北京市', '朝阳区'],
  ['上海市', '上海市', '浦东新区'],
  ['湖南省', '长沙市', '岳麓区'],
]

onLoad(async (opt) => {
  if (opt?.id) {
    id.value = Number(opt.id)
    try {
      const list = await Address.list()
      const a = list.find((x: any) => x.id === id.value)
      if (a) Object.assign(form, a)
    } catch {}
  }
})

function pickRegion(r: string[]) {
  form.province = r[0]
  form.city = r[1]
  form.district = r[2]
  showRegionPicker.value = false
}

async function save() {
  if (!form.receiver?.trim()) { uni.showToast({ title: '请填写收货人', icon: 'none' }); return }
  if (!/^1\d{10}$/.test(form.phone)) { uni.showToast({ title: '请填写正确的手机号', icon: 'none' }); return }
  if (!form.detail?.trim()) { uni.showToast({ title: '请填写详细地址', icon: 'none' }); return }
  uni.showLoading({ title: '保存中…', mask: true })
  try {
    if (id.value) {
      await Address.update(id.value, form)
    } else {
      await Address.create(form)
    }
    uni.hideLoading()
    uni.showToast({ title: id.value ? '已更新' : '已保存', icon: 'success' })
    setTimeout(() => uni.navigateBack(), 600)
  } catch {
    uni.hideLoading()
    uni.showToast({ title: '保存失败', icon: 'none' })
  }
}
</script>

<template>
  <view class="ed">
    <BrandHeader :title="id ? '编辑地址' : '新增地址'" show-back :show-logo="false" />

    <view class="form">
      <view class="row">
        <text class="row__label">收货人</text>
        <input v-model="form.receiver" class="row__input" placeholder="请输入" />
      </view>
      <view class="row">
        <text class="row__label">手机号</text>
        <input v-model="form.phone" class="row__input" maxlength="11" type="number" placeholder="请输入手机号" />
      </view>
      <view class="row" @click="showRegionPicker = true">
        <text class="row__label">所在地区</text>
        <text class="row__value">{{ form.province }} {{ form.city }} {{ form.district }}</text>
        <text class="row__arrow">›</text>
      </view>
      <view class="row row--multiline">
        <text class="row__label">详细地址</text>
        <textarea v-model="form.detail" class="row__textarea" placeholder="街道、楼栋、门牌号" />
      </view>
      <view class="row row--switch">
        <text class="row__label">设为默认地址</text>
        <view class="switch" :class="{ on: form.is_default }" @click="form.is_default = !form.is_default">
          <view class="switch__dot" />
        </view>
      </view>
    </view>

    <view class="bar">
      <view class="bar__btn" @click="save">保存</view>
    </view>

    <view v-if="showRegionPicker" class="popup" @click="showRegionPicker = false">
      <view class="popup__sheet" @click.stop>
        <text class="popup__title">选择地区</text>
        <view
          v-for="r in regionPresets"
          :key="r.join('-')"
          class="popup__item"
          @click="pickRegion(r)"
        >
          <text>{{ r.join(' ') }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.ed { min-height: 100vh; background: $color-bg-page; padding-bottom: 80px; }

.form { background: #fff; margin: 12px; border-radius: 12px; padding: 4px 14px; }

.row {
  display: flex; align-items: center;
  min-height: 50px;
  padding: 8px 0;
  border-bottom: 1px solid $color-divider;
  &:last-child { border-bottom: 0; }
  &__label { width: 86px; flex-shrink: 0; font-size: 14px; color: $color-text-primary; }
  &__input { flex: 1; font-size: 14px; background: transparent; text-align: right; padding: 0; border: 0; }
  &__value { flex: 1; text-align: right; color: $color-text-regular; font-size: 14px; }
  &__textarea { flex: 1; text-align: left; padding: 4px 0; font-size: 14px; min-height: 44px; box-sizing: border-box; }
  &__arrow { color: $color-text-placeholder; font-size: 18px; margin-left: 6px; }
  &--multiline { align-items: flex-start; }
  &--switch { justify-content: space-between; }
}

.switch {
  width: 44px; height: 24px;
  border-radius: 999px;
  background: $color-bg-tag;
  position: relative;
  transition: background .2s;
  &__dot {
    position: absolute;
    top: 2px; left: 2px;
    width: 20px; height: 20px;
    border-radius: 50%;
    background: #fff;
    box-shadow: 0 1px 3px rgba(0,0,0,.2);
    transition: transform .2s;
  }
  &.on { background: $color-primary;
    .switch__dot { transform: translateX(20px); }
  }
}

.bar {
  position: fixed; bottom: 0; left: 0; right: 0;
  padding: 12px 16px;
  background: #fff;
  border-top: 1px solid $color-divider;
  z-index: 9;
}
.bar__btn {
  height: 44px; line-height: 44px;
  border-radius: 999px;
  background: linear-gradient(135deg, #ff7a2a, #ff4d4f);
  color: #fff;
  font-weight: 700; font-size: 15px;
  text-align: center;
  box-shadow: 0 6px 18px rgba(255,77,79,.3);
}

.popup {
  position: fixed; inset: 0;
  background: rgba(0,0,0,.4);
  z-index: 100;
  display: flex; align-items: flex-end;
  &__sheet { width: 100%; background: #fff; border-radius: 16px 16px 0 0; padding: 16px; max-height: 70vh; overflow-y: auto; }
  &__title { display: block; font-size: 16px; font-weight: 700; text-align: center; margin-bottom: 12px; }
  &__item {
    padding: 14px 8px;
    border-bottom: 1px solid $color-divider;
    font-size: 14px;
  }
}
</style>
