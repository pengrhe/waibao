<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/store/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const groups: { key: string; title: string }[] = [
  { key: 'main', title: '工作台' },
  { key: 'catalog', title: '内容与商品' },
  { key: 'c_user', title: 'C 端' },
  { key: 'order', title: '订单' },
  { key: 'b_user', title: '伙伴与门店' },
  { key: 'finance', title: '财务' },
  { key: 'system', title: '系统与 AI' },
]

const menuItems = computed(() => {
  const all = router.getRoutes().filter((r) => r.meta?.title && !r.meta?.public)
  return all.map((r) => ({
    path: r.path,
    title: r.meta?.title as string,
    icon: (r.meta?.icon as string) ?? 'Menu',
    group: (r.meta?.group as string) ?? 'main',
  }))
})

const grouped = computed(() =>
  groups.map((g) => ({ ...g, items: menuItems.value.filter((m) => m.group === g.key) })),
)

const activeKey = computed(() => route.path)

async function onLogout() {
  try {
    await ElMessageBox.confirm('确定退出登录？', '提示', { type: 'warning' })
    auth.logout()
  } catch {
    /* canceled */
  }
}
</script>

<template>
  <el-container class="layout">
    <el-aside width="220px" class="layout__aside">
      <div class="layout__brand">
        <span class="layout__logo">aitee</span>
        <span class="layout__sub">总部后台</span>
      </div>
      <el-menu :default-active="activeKey" router class="layout__menu">
        <template v-for="g in grouped" :key="g.key">
          <el-menu-item-group :title="g.title" v-if="g.items.length">
            <el-menu-item
              v-for="m in g.items"
              :key="m.path"
              :index="m.path"
            >
              <el-icon><component :is="m.icon" /></el-icon>
              <span>{{ m.title }}</span>
            </el-menu-item>
          </el-menu-item-group>
        </template>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="layout__header">
        <div class="layout__crumb">{{ route.meta?.title || '工作台' }}</div>
        <el-dropdown trigger="click">
          <span class="layout__user">
            <el-avatar size="small" style="background: linear-gradient(135deg,#ff7a2a,#ff4d6e); color:#fff">A</el-avatar>
            <span class="layout__uname">{{ auth.user.name || auth.user.username || 'admin' }}</span>
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="onLogout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>
      <el-main class="layout__main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped lang="scss">
.layout {
  height: 100vh;

  &__aside {
    background: linear-gradient(180deg, #1f2937 0%, #111827 100%);
    color: #fff;
    overflow-y: auto;
    border-right: 1px solid #0f172a;
  }

  &__brand {
    padding: 18px 20px;
    display: flex;
    align-items: baseline;
    gap: 8px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  }

  &__logo {
    font-size: 22px;
    font-weight: 900;
    background: linear-gradient(135deg, #ff8a3a 0%, #ff4d6e 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
  }

  &__sub { color: rgba(255, 255, 255, 0.5); font-size: 12px; }

  &__menu {
    border: none;
    background: transparent;

    :deep(.el-menu-item) {
      color: rgba(255, 255, 255, 0.7);
      &:hover { background: rgba(255, 255, 255, 0.06); color: #fff; }
      &.is-active { background: rgba(255, 138, 58, 0.18); color: #ff8a3a; }
    }
    :deep(.el-menu-item-group__title) {
      color: rgba(255, 255, 255, 0.35);
      font-size: 11px;
      letter-spacing: 0.5px;
    }
  }

  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #fff;
    border-bottom: 1px solid #eef2f7;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
  }

  &__crumb { font-weight: 600; }

  &__user {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    padding: 4px 8px;
    border-radius: 6px;
    &:hover { background: #f5f7fa; }
  }

  &__uname { font-size: 13px; color: #475569; }

  &__main {
    background: #f5f7fa;
    padding: 0;
    overflow-y: auto;
  }
}
</style>
