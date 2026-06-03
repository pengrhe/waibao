<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showSuccessToast } from 'vant'
import { getHttp, useAuthStore, type PortalLoginResp, type PortalRole } from '@aitee/shared'
import { moduleList, modules } from '../modules'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const activeRole = ref<PortalRole>(
  (route.query.role as PortalRole) || moduleList[0].role,
)

const form = reactive({ username: '', password: '' })

watch(
  activeRole,
  (r) => {
    const m = modules[r]
    form.username = m.defaultUser?.username ?? ''
    form.password = m.defaultUser?.password ?? ''
  },
  { immediate: true },
)

const currentBrand = computed(() => modules[activeRole.value].brand)
const currentHint = computed(() => modules[activeRole.value].loginHint)

const loading = ref(false)

async function onSubmit() {
  loading.value = true
  try {
    const data = await getHttp().post<unknown, PortalLoginResp>(
      `/${activeRole.value}/auth/login`,
      form,
    )
    auth.setAuth(data.token, data.user)
    showSuccessToast('登录成功')
    const r =
      (route.query.redirect as string) || `/${data.user.role}/dashboard`
    router.replace(r)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login" :style="{ background: currentBrand.gradient }">
    <div class="login__panel">
      <div class="login__brand">
        <span class="login__logo">aitee</span>
        <span class="login__sub">业务端登录</span>
      </div>

      <van-tabs v-model:active="activeRole" line-width="24px" :swipeable="false" shrink>
        <van-tab v-for="m in moduleList" :key="m.role" :name="m.role" :title="m.label" />
      </van-tabs>

      <van-form @submit="onSubmit">
        <van-cell-group inset>
          <van-field v-model="form.username" label="账号" placeholder="请输入账号" />
          <van-field v-model="form.password" type="password" label="密码" placeholder="请输入密码" />
        </van-cell-group>
        <div style="padding: 16px">
          <van-button
            :loading="loading"
            round
            block
            type="primary"
            native-type="submit"
            :color="currentBrand.primary"
          >
            登录 · {{ modules[activeRole].label }}
          </van-button>
        </div>
      </van-form>

      <div class="login__hint">{{ currentHint }}</div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.login {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  transition: background 0.3s;

  &__panel {
    width: 100%;
    max-width: 400px;
    background: rgba(255, 255, 255, 0.96);
    border-radius: 18px;
    padding: 28px 16px 20px;
    box-shadow: 0 12px 40px rgba(15, 23, 42, 0.12);
  }
  &__brand {
    display: flex;
    align-items: baseline;
    justify-content: center;
    gap: 10px;
    margin-bottom: 16px;
  }
  &__logo {
    font-size: 28px;
    font-weight: 900;
    background: linear-gradient(135deg, #ff7a2a 0%, #ff4d6e 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
  }
  &__sub {
    color: #94a3b8;
    font-size: 13px;
  }
  &__hint {
    text-align: center;
    color: #94a3b8;
    font-size: 12px;
    padding: 4px 16px 0;
  }
}
</style>
