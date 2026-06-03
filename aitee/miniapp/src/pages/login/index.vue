<script setup lang="ts">
import { onBeforeUnmount, ref } from 'vue'
import { useAuthStore } from '../../store/auth'
import { Auth } from '../../api'
import { PLATFORM } from '../../utils/env'
import { getPlatformLoginCode, isWechat, isDouyin } from '../../utils/platform'

const auth = useAuthStore()
const phone = ref('13800138000')
const code = ref('')
const sentCountdown = ref(0)
const submitting = ref(false)
let timer: any = null

function sendCode() {
  if (!/^1\d{10}$/.test(phone.value)) {
    uni.showToast({ title: '请输入正确的手机号', icon: 'none' })
    return
  }
  sentCountdown.value = 60
  uni.showToast({ title: '演示版：验证码 0000', icon: 'none' })
  if (timer) clearInterval(timer)
  timer = setInterval(() => {
    sentCountdown.value--
    if (sentCountdown.value <= 0 && timer) clearInterval(timer)
  }, 1000)
}

onBeforeUnmount(() => { if (timer) clearInterval(timer) })

async function login() {
  if (!/^1\d{10}$/.test(phone.value)) { uni.showToast({ title: '请输入正确的手机号', icon: 'none' }); return }
  if (code.value && code.value !== '0000') { uni.showToast({ title: '演示验证码请填 0000 或留空', icon: 'none' }); return }
  await doLogin('h5')
}

async function quickLogin(ch: 'wx_app' | 'dy_app' | 'h5' = 'h5') {
  await doLogin(ch)
}

async function doLogin(channel: 'wx_app' | 'dy_app' | 'h5') {
  if (submitting.value) return
  submitting.value = true
  uni.showLoading({ title: '登录中…', mask: true })
  try {
    let codeStr = ''
    if (isWechat || isDouyin) {
      codeStr = await getPlatformLoginCode()
    }
    const out: any = await Auth.login({
      channel,
      phone: phone.value,
      nickname: 'aitee 用户',
      code: codeStr,
    })
    auth.setAuth(out.token, out.user)
    uni.hideLoading()
    uni.showToast({ title: '欢迎回来', icon: 'success' })
    setTimeout(() => uni.navigateBack().catch(() => uni.switchTab({ url: '/pages/mine/index' })), 600)
  } catch {
    uni.hideLoading()
    uni.showToast({ title: '登录失败', icon: 'none' })
  } finally { submitting.value = false }
}
</script>

<template>
  <view class="login">
    <view class="login__brand">
      <view class="login__logo">aitee</view>
      <view class="login__slogan">AI 驱动的 T 恤定制</view>
    </view>

    <view class="login__form">
      <view class="row">
        <text class="row__label">手机号</text>
        <input v-model="phone" maxlength="11" class="row__input" placeholder="请输入手机号" type="number" />
      </view>
      <view class="row">
        <text class="row__label">验证码</text>
        <input v-model="code" maxlength="4" class="row__input" placeholder="演示版填 0000 或留空" type="number" />
        <view class="row__send" :class="{ 'row__send--dis': sentCountdown > 0 }" @click="sentCountdown <= 0 && sendCode()">
          {{ sentCountdown > 0 ? `${sentCountdown}s` : '发送验证码' }}
        </view>
      </view>
    </view>

    <view class="login__btn" @click="login">登录 / 注册</view>

    <view class="login__divider"><text>- 一键登录 -</text></view>

    <view class="login__quick login__quick--h5" @click="quickLogin('h5')">
      <text>⚡ 一键体验登录（Demo）</text>
    </view>
    <view class="login__quick login__quick--wx" @click="quickLogin('wx_app')">
      <text>🟢 微信一键登录（mock wx.login）</text>
    </view>
    <view class="login__quick login__quick--dy" @click="quickLogin('dy_app')">
      <text>🔵 抖音一键登录（mock）</text>
    </view>

    <view class="login__agreement">
      登录即视为您同意<text class="login__link">用户协议</text>和<text class="login__link">隐私政策</text>
    </view>

    <view class="login__platform">当前平台：{{ PLATFORM }} · M2 全 mock 登录</view>
  </view>
</template>

<style lang="scss" scoped>
.login {
  min-height: 100vh;
  background: linear-gradient(180deg, #fff 0%, #fff7f5 100%);
  padding: 60px 24px 40px;
  &__brand { text-align: center; margin: 24px 0 32px; }
  &__logo {
    font-size: 36px; font-weight: 800; letter-spacing: 2px;
    background: linear-gradient(135deg, #ff7a2a, #ff4d4f);
    -webkit-background-clip: text; background-clip: text; color: transparent;
  }
  &__slogan { font-size: 13px; color: $color-text-secondary; margin-top: 6px; }
  &__form {
    background: #fff; border-radius: 12px;
    padding: 4px 14px;
    margin-bottom: 24px;
    box-shadow: $shadow-md;
  }
  &__btn {
    height: 48px; line-height: 48px;
    background: linear-gradient(135deg, #ff7a2a, #ff4d4f);
    color: #fff;
    border-radius: 999px;
    font-weight: 700; font-size: 16px;
    text-align: center;
    box-shadow: 0 6px 18px rgba(255,77,79,.35);
  }
  &__divider { text-align: center; color: $color-text-placeholder; font-size: 11px; margin: 22px 0 12px; }
  &__quick {
    margin-top: 10px;
    height: 44px; line-height: 44px; text-align: center;
    border-radius: 999px;
    font-weight: 600; font-size: 14px;
    background: #fff;
    border: 1px solid $color-divider;
    color: $color-text-primary;
    &--h5 { color: $color-primary; border-color: $color-primary; }
    &--wx { background: #07c160; color: #fff; border-color: transparent; }
    &--dy { background: #1f2937; color: #fff; border-color: transparent; }
  }
  &__agreement { text-align: center; margin-top: 24px; font-size: 11px; color: $color-text-secondary; }
  &__link { color: $color-primary; margin: 0 2px; }
  &__platform { text-align: center; margin-top: 6px; font-size: 11px; color: $color-text-placeholder; }
}

.row {
  display: flex; align-items: center;
  min-height: 50px;
  padding: 8px 0;
  border-bottom: 1px solid $color-divider;
  &:last-child { border-bottom: 0; }
  &__label { width: 64px; flex-shrink: 0; font-size: 14px; color: $color-text-regular; }
  &__input { flex: 1; background: transparent; font-size: 14px; }
  &__send {
    color: $color-primary;
    font-size: 12px;
    padding: 4px 12px;
    border-radius: 999px;
    background: rgba(255,77,79,.08);
    line-height: 1.5;
    &--dis { color: $color-text-placeholder; background: $color-bg-tag; }
  }
}
</style>
