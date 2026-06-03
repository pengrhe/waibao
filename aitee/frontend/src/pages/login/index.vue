<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showLoadingToast, showToast } from 'vant'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()

const phone = ref('13800138000')
const code = ref('')
const sentCountdown = ref(0)
let timer: ReturnType<typeof setInterval> | null = null

function sendCode() {
  if (!/^1\d{10}$/.test(phone.value)) {
    showToast('请输入正确的手机号')
    return
  }
  sentCountdown.value = 60
  showToast('演示版：验证码 0000')
  if (timer) clearInterval(timer)
  timer = setInterval(() => {
    sentCountdown.value--
    if (sentCountdown.value <= 0 && timer) clearInterval(timer)
  }, 1000)
}

async function login() {
  if (!/^1\d{10}$/.test(phone.value)) return showToast('请输入正确的手机号')
  if (code.value !== '0000' && code.value !== '') return showToast('演示验证码请填 0000 或留空')
  const t = showLoadingToast({ message: '登录中…', duration: 0, forbidClick: true })
  try {
    await userStore.login()
    t.close()
    showToast({ type: 'success', message: '欢迎回来' })
    setTimeout(() => router.replace('/mine'), 600)
  } catch {
    t.close()
    showToast({ type: 'fail', message: '登录失败' })
  }
}

async function quickLogin() {
  const t = showLoadingToast({ message: '一键登录…', duration: 0, forbidClick: true })
  try {
    await userStore.login()
    t.close()
    showToast({ type: 'success', message: '欢迎回来' })
    setTimeout(() => router.replace('/mine'), 600)
  } catch {
    t.close()
  }
}
</script>

<template>
  <div class="login">
    <div class="login__brand">
      <div class="login__logo">aitee</div>
      <div class="login__slogan">AI 驱动的 T 恤定制</div>
    </div>

    <div class="login__form">
      <label class="row">
        <span class="row__label">手机号</span>
        <input v-model="phone" maxlength="11" class="row__input" placeholder="请输入手机号" />
      </label>
      <label class="row">
        <span class="row__label">验证码</span>
        <input v-model="code" maxlength="4" class="row__input" placeholder="演示版填 0000 或留空" />
        <button class="row__send" :disabled="sentCountdown > 0" @click="sendCode">
          {{ sentCountdown > 0 ? `${sentCountdown}s` : '发送验证码' }}
        </button>
      </label>
    </div>

    <button class="login__btn" @click="login">登录 / 注册</button>
    <button class="login__quick" @click="quickLogin">
      <span class="i-material-symbols:bolt-rounded" />
      一键体验登录（Demo）
    </button>

    <div class="login__agreement">
      登录即视为您同意<a>用户协议</a>和<a>隐私政策</a>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.login {
  min-height: 100vh;
  background: linear-gradient(180deg, #fff 0%, #fff7f5 100%);
  padding: 60px 24px 40px;
  display: flex;
  flex-direction: column;
  align-items: stretch;

  &__brand {
    text-align: center;
    margin: 24px 0 32px;
  }

  &__logo {
    font-size: 36px;
    font-weight: 800;
    color: $color-primary;
    letter-spacing: 2px;
  }

  &__slogan {
    font-size: 13px;
    color: $color-text-secondary;
    margin-top: 6px;
  }

  &__form {
    background: #fff;
    border-radius: 12px;
    padding: 4px 14px;
    margin-bottom: 24px;
    box-shadow: $shadow-md;
  }

  &__btn {
    height: 48px;
    background: $color-primary;
    color: #fff;
    border-radius: $radius-pill;
    font-weight: 700;
    font-size: 16px;
  }

  &__quick {
    margin-top: 12px;
    height: 44px;
    background: #fff;
    color: $color-primary;
    border: 1px solid $color-primary;
    border-radius: $radius-pill;
    font-weight: 600;
    font-size: 14px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
  }

  &__agreement {
    text-align: center;
    margin-top: 24px;
    font-size: 11px;
    color: $color-text-secondary;
    a {
      color: $color-primary;
      margin: 0 2px;
    }
  }
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
    width: 64px;
    flex-shrink: 0;
    font-size: 14px;
  }

  &__input {
    flex: 1;
    border: none;
    outline: none;
    background: transparent;
    font-size: 14px;
  }

  &__send {
    color: $color-primary;
    font-size: 12px;
    padding: 4px 10px;
    border-radius: 999px;
    background: rgba(255, 77, 79, 0.08);
    flex-shrink: 0;

    &:disabled {
      color: $color-text-placeholder;
      background: $color-bg-tag;
    }
  }
}
</style>
