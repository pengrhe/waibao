<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { showDialog, showToast } from 'vant'
import BrandHeader from '@/components/BrandHeader.vue'
import { useUserStore } from '@/store/user'
import { fetchHomeBanners } from '@/api/home'
import { listCoupons } from '@/api/coupon'
import { listDesigns } from '@/api/design'
import { listOrders } from '@/api/order'
import { resetDemoAll } from '@/store/bootstrap'
import { maskPhone } from '@/utils/format'
import type { Banner, Coupon, Design, Order } from '@/types'

const router = useRouter()
const userStore = useUserStore()

const inviteBanner = ref<Banner | null>(null)
const couponCount = ref(0)
const designs = ref<Design[]>([])
const orders = ref<Order[]>([])

interface Status {
  key: 'pending_pay' | 'pending_print' | 'printing' | 'done'
  label: string
  icon: string
}
const orderStatuses: Status[] = [
  { key: 'pending_pay', label: '待付款', icon: 'i-material-symbols:payments-outline-rounded' },
  { key: 'pending_print', label: '待打印', icon: 'i-material-symbols:print-outline-rounded' },
  { key: 'printing', label: '打印中', icon: 'i-material-symbols:hourglass-empty-rounded' },
  { key: 'done', label: '已完成', icon: 'i-material-symbols:task-alt-rounded' },
]

const orderCounts = computed(() => {
  const counts: Record<string, number> = {}
  orderStatuses.forEach((s) => {
    counts[s.key] = orders.value.filter((o) => o.status === s.key).length
  })
  return counts
})

const profile = computed(() => userStore.profile)

async function load() {
  await userStore.load()
  const [banners, coupons, ds, os] = await Promise.all([
    fetchHomeBanners('mine_invite'),
    listCoupons('unused'),
    listDesigns(),
    listOrders('all'),
  ])
  inviteBanner.value = banners[0] ?? null
  couponCount.value = coupons.length
  designs.value = ds
  orders.value = os
}

onMounted(load)

async function onLogin() {
  if (profile.value?.loggedIn) {
    showDialog({ title: '退出登录', message: '确定退出当前账号？', showCancelButton: true })
      .then(async () => {
        await userStore.logout()
      })
      .catch(() => {})
  } else {
    router.push('/login')
  }
}

function go(path: string) {
  router.push(path)
}

function onResetDemo() {
  showDialog({
    title: '重置 Demo 数据？',
    message: '将清空购物车、设计稿、订单、地址、优惠券，恢复初始演示态。',
    showCancelButton: true,
  })
    .then(() => {
      resetDemoAll()
      showToast({ type: 'success', message: '已重置' })
      setTimeout(() => location.reload(), 800)
    })
    .catch(() => {})
}
</script>

<template>
  <div class="mine">
    <BrandHeader title="我的" />

    <!-- 用户信息 -->
    <section class="user" @click="onLogin">
      <img class="user__avatar" :src="profile?.avatar" alt="" />
      <div class="user__body">
        <div class="user__name">{{ profile?.loggedIn ? maskPhone(profile.phone) : '点此登录' }}</div>
        <div class="user__sub">{{ profile?.loggedIn ? `ID ${profile.id}` : '登录解锁全部功能' }}</div>
      </div>
      <button class="user__settings">
        <span class="i-material-symbols:settings-outline-rounded" />
      </button>
    </section>

    <!-- 优惠券 banner -->
    <section class="coupon-banner" @click="go('/coupon')">
      <span class="i-material-symbols:redeem-rounded coupon-banner__icon" />
      <div class="coupon-banner__body">
        <div class="coupon-banner__title">我的优惠券</div>
        <div class="coupon-banner__sub">现有优惠券 {{ couponCount }} 张</div>
      </div>
      <span class="coupon-banner__arrow i-material-symbols:chevron-right-rounded" />
    </section>

    <!-- 设计 / 订单 双卡片 -->
    <section class="dual">
      <div class="dual__card" @click="go('/design-list')">
        <div class="dual__title">我的设计</div>
        <div class="dual__icon dual__icon--design">
          <span class="i-material-symbols:design-services-outline-rounded" />
        </div>
        <div v-if="!designs.length" class="dual__placeholder">快去设计您的专属好物吧～</div>
        <div v-else class="dual__count">{{ designs.length }} 个设计</div>
        <button class="dual__btn">{{ designs.length ? '去看看' : '去设计' }}</button>
      </div>
      <div class="dual__card" @click="go('/order/list')">
        <div class="dual__title">我的订单</div>
        <div class="dual__icon dual__icon--order">
          <span class="i-material-symbols:receipt-long-outline-rounded" />
        </div>
        <div v-if="!orders.length" class="dual__placeholder">快去首页选购吧～</div>
        <div v-else class="dual__count">{{ orders.length }} 笔订单</div>
        <button class="dual__btn">{{ orders.length ? '去看看' : '去首页' }}</button>
      </div>
    </section>

    <!-- 订单状态快捷 -->
    <section class="orders-quick">
      <button v-for="s in orderStatuses" :key="s.key" class="orders-quick__item" @click="go(`/order/list?status=${s.key}`)">
        <span class="orders-quick__icon">
          <component :is="s.icon" />
          <span v-if="orderCounts[s.key]" class="orders-quick__badge">{{ orderCounts[s.key] }}</span>
        </span>
        <span class="orders-quick__label">{{ s.label }}</span>
      </button>
    </section>

    <!-- 菜单列表 -->
    <section class="menu">
      <button class="menu__item" @click="go('/design-list')">
        <span class="i-material-symbols:photo-library-outline-rounded menu__icon" />
        <span class="menu__label">我的图库</span>
        <span class="menu__arrow i-material-symbols:chevron-right-rounded" />
      </button>
      <button class="menu__item" @click="go('/address/list')">
        <span class="i-material-symbols:location-on-outline-rounded menu__icon" />
        <span class="menu__label">地址管理</span>
        <span class="menu__arrow i-material-symbols:chevron-right-rounded" />
      </button>
      <button class="menu__item" @click="showToast('客服已经在路上...')">
        <span class="i-material-symbols:support-agent-rounded menu__icon" />
        <span class="menu__label">联系客服</span>
        <span class="menu__arrow i-material-symbols:chevron-right-rounded" />
      </button>
    </section>

    <!-- 邀请 banner -->
    <section v-if="inviteBanner" class="invite" @click="go('/coupon')">
      <img :src="inviteBanner.imageUrl" alt="" />
    </section>

    <!-- 重置 Demo -->
    <div class="reset" @click="onResetDemo">
      <span class="i-material-symbols:refresh-rounded" />
      重置 Demo 数据
    </div>
  </div>
</template>

<style lang="scss" scoped>
.mine {
  min-height: 100vh;
  background: $color-bg-page;
  padding-bottom: calc(#{$tabbar-height} + 24px);
}

.user {
  background: linear-gradient(135deg, #fff 0%, #fff7f7 100%);
  margin: 0 12px;
  padding: 16px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 12px;

  &__avatar {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  &__body {
    flex: 1;
    min-width: 0;
  }

  &__name {
    font-size: 16px;
    font-weight: 700;
    color: $color-text-primary;
  }

  &__sub {
    font-size: 12px;
    color: $color-text-secondary;
    margin-top: 4px;
  }

  &__settings {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: rgba(0, 0, 0, 0.04);
    color: $color-text-primary;
    font-size: 18px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }
}

.coupon-banner {
  margin: 12px;
  padding: 12px 16px;
  background: linear-gradient(90deg, #ffe4e6 0%, #fff7f0 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 10px;

  &__icon {
    font-size: 28px;
    color: $color-primary;
  }

  &__body {
    flex: 1;
    min-width: 0;
  }

  &__title {
    font-size: 14px;
    font-weight: 700;
    color: $color-text-primary;
  }

  &__sub {
    font-size: 12px;
    color: $color-primary;
    margin-top: 2px;
  }

  &__arrow {
    color: $color-text-secondary;
    font-size: 18px;
  }
}

.dual {
  display: flex;
  gap: 12px;
  padding: 0 12px;
  margin-bottom: 12px;

  &__card {
    flex: 1;
    background: #fff;
    border-radius: 12px;
    padding: 14px;
    text-align: center;
    position: relative;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
  }

  &__title {
    font-size: 13px;
    font-weight: 700;
    text-align: left;
  }

  &__icon {
    font-size: 36px;
    color: $color-text-placeholder;
    margin: 8px 0 0;

    &--design {
      color: rgba(255, 77, 79, 0.4);
    }
    &--order {
      color: rgba(34, 197, 94, 0.5);
    }
  }

  &__placeholder {
    font-size: 11px;
    color: $color-text-secondary;
    margin-top: 4px;
  }

  &__count {
    font-size: 12px;
    color: $color-primary;
    font-weight: 600;
    margin-top: 4px;
  }

  &__btn {
    margin-top: 10px;
    background: $color-bg-tag;
    border-radius: $radius-pill;
    padding: 6px 14px;
    font-size: 12px;
    color: $color-text-primary;
  }
}

.orders-quick {
  background: #fff;
  margin: 0 12px;
  border-radius: 12px;
  display: flex;
  padding: 12px 0;

  &__item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    color: $color-text-primary;
  }

  &__icon {
    width: 32px;
    height: 32px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    color: $color-text-primary;
    position: relative;
  }

  &__badge {
    position: absolute;
    top: -4px;
    right: -8px;
    min-width: 16px;
    height: 16px;
    padding: 0 4px;
    background: $color-primary;
    color: #fff;
    border-radius: 8px;
    font-size: 10px;
    font-weight: 600;
    line-height: 16px;
    text-align: center;
  }

  &__label {
    font-size: 11px;
    color: $color-text-secondary;
  }
}

.menu {
  background: #fff;
  margin: 12px;
  border-radius: 12px;
  overflow: hidden;

  &__item {
    width: 100%;
    height: 48px;
    padding: 0 14px;
    display: flex;
    align-items: center;
    gap: 10px;
    border-bottom: 1px solid $color-divider;
    &:last-child {
      border-bottom: 0;
    }
  }

  &__icon {
    font-size: 20px;
    color: $color-text-primary;
  }

  &__label {
    flex: 1;
    text-align: left;
    font-size: 14px;
    color: $color-text-primary;
  }

  &__arrow {
    font-size: 18px;
    color: $color-text-placeholder;
  }
}

.invite {
  margin: 0 12px;
  border-radius: 12px;
  overflow: hidden;
  img {
    width: 100%;
    display: block;
  }
}

.reset {
  text-align: center;
  font-size: 12px;
  color: $color-text-placeholder;
  padding: 24px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}
</style>
