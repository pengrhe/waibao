<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login } from '@/api/auth'
import { useAuthStore } from '@/store/auth'

const form = reactive({ username: 'admin', password: 'admin123' })
const loading = ref(false)
const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

async function onSubmit() {
  loading.value = true
  try {
    const data = await login(form)
    auth.setAuth(data.token, data.user)
    ElMessage.success('登录成功')
    const redirect = (route.query.redirect as string) || '/dashboard'
    router.replace(redirect)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login">
    <div class="login__panel">
      <div class="login__brand">
        <span class="login__logo">aitee</span>
        <span class="login__sub">总部后台</span>
      </div>
      <el-form label-position="top" class="login__form" @submit.prevent="onSubmit">
        <el-form-item label="账号">
          <el-input v-model="form.username" placeholder="admin" size="large" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" placeholder="admin123" size="large" show-password />
        </el-form-item>
        <el-button type="primary" :loading="loading" size="large" class="login__btn" @click="onSubmit">登录</el-button>
        <div class="login__tip">M1 默认账号：admin / admin123（由 seed 脚本写入）</div>
      </el-form>
    </div>
  </div>
</template>

<style scoped lang="scss">
.login {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background:
    radial-gradient(80% 60% at 100% 0%, rgba(255, 138, 58, 0.16) 0%, transparent 60%),
    radial-gradient(80% 60% at 0% 100%, rgba(91, 108, 255, 0.16) 0%, transparent 60%),
    linear-gradient(135deg, #f6f9ff 0%, #fff5ed 100%);

  &__panel {
    width: 420px;
    background: #fff;
    border-radius: 16px;
    padding: 40px 36px;
    box-shadow: 0 12px 40px rgba(15, 23, 42, 0.08);
  }

  &__brand {
    display: flex;
    align-items: baseline;
    gap: 12px;
    margin-bottom: 28px;
  }

  &__logo {
    font-size: 28px;
    font-weight: 900;
    background: linear-gradient(135deg, #ff7a2a 0%, #ff4d6e 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    letter-spacing: -1px;
  }

  &__sub {
    color: #94a3b8;
    font-size: 14px;
  }

  &__form {
    margin-top: 8px;
  }

  &__btn {
    width: 100%;
    margin-top: 6px;
    background: linear-gradient(135deg, #ff7a2a 0%, #ff4d6e 100%);
    border: none;
  }

  &__tip {
    text-align: center;
    color: #94a3b8;
    font-size: 12px;
    margin-top: 16px;
  }
}
</style>
