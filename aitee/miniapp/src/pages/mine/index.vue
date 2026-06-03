<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import BrandHeader from '../../components/BrandHeader.vue'
import CustomTabBar from '../../components/CustomTabBar.vue'
import { useAuthStore } from '../../store/auth'
import { User, Messages, Coupon, Design, Order } from '../../api'
import { maskPhone } from '../../utils/format'
import { isDouyin } from '../../utils/platform'

const auth = useAuthStore()
const user = ref<any>(auth.user)
const unread = ref(0)
const couponCount = ref(0)
const designs = ref<any[]>([])
const orders = ref<any[]>([])

interface Status {
  key: string
  label: string
  icon: string
}
const orderStatuses: Status[] = [
  { key: 'pending_pay', label: '待付款', icon: '💰' },
  { key: 'pending_print', label: '待打印', icon: '🖨️' },
  { key: 'printing', label: '打印中', icon: '⏳' },
  { key: 'completed', label: '已完成', icon: '✅' },
]

const orderCounts = computed(() => {
  const r: Record<string, number> = {}
  orderStatuses.forEach((s) => {
    r[s.key] = orders.value.filter((o) => o.status === s.key || (s.key === 'completed' && o.status === 'done')).length
  })
  return r
})

async function refresh() {
  if (!auth.isAuthed) {
    user.value = null
    unread.value = 0
    couponCount.value = 0
    designs.value = []
    orders.value = []
    return
  }
  try {
    user.value = await User.profile()
    auth.setAuth(auth.token, user.value)
  } catch {}
  try { unread.value = (await Messages.unreadCount()).count } catch {}
  try { couponCount.value = (await Coupon.mine('unused')).length } catch {}
  try { designs.value = await Design.list() } catch {}
  try { orders.value = await Order.list() } catch {}
}

onMounted(refresh)
onShow(() => {
  refresh()
  try { uni.hideTabBar({ animation: false }) } catch {}
})

function go(path: string) {
  if (!auth.isAuthed) { uni.navigateTo({ url: '/pages/login/index' }); return }
  uni.navigateTo({ url: path })
}

function onLogin() {
  if (auth.isAuthed) {
    uni.showModal({ title: '退出登录', content: '确定退出当前账号？', success: (r) => { if (r.confirm) { auth.logout(); refresh() } } })
  } else {
    uni.navigateTo({ url: '/pages/login/index' })
  }
}

function onContact() {
  uni.showToast({ title: '客服已经在路上...', icon: 'none' })
}
</script>

<template>
  <view class="mine">
    <BrandHeader title="我的" />

    <!-- 用户信息 -->
    <view class="user" @click="onLogin">
      <view v-if="user?.avatar_url" class="user__avatar">
        <image :src="user.avatar_url" class="user__avatar-img" />
      </view>
      <view v-else class="user__avatar user__avatar--ph">
        <text>{{ (user?.nickname || (isDouyin ? '游' : 'A')).charAt(0) }}</text>
      </view>
      <view class="user__body">
        <text class="user__name">{{ auth.isAuthed ? (maskPhone(user?.phone) || user?.nickname) : '点此登录' }}</text>
        <text class="user__sub">
          {{ auth.isAuthed ? `ID ${user?.id}` : (isDouyin ? '抖音游客模式 · 浏览免登录' : '登录解锁全部功能') }}
        </text>
      </view>
      <view class="user__settings">
        <text>⚙</text>
      </view>
    </view>

    <!-- 优惠券 banner -->
    <view class="coupon-banner" @click="go('/pages/coupons/index')">
      <view class="coupon-banner__icon"><text>🎁</text></view>
      <view class="coupon-banner__body">
        <text class="coupon-banner__title">我的优惠券</text>
        <text class="coupon-banner__sub">现有优惠券 {{ couponCount }} 张</text>
      </view>
      <text class="coupon-banner__arrow">›</text>
    </view>

    <!-- 设计 / 订单 双卡片 -->
    <view class="dual">
      <view class="dual__card" @click="go('/pages/editor/index')">
        <text class="dual__title">我的设计</text>
        <view class="dual__icon dual__icon--design"><text>🎨</text></view>
        <text v-if="!designs.length" class="dual__placeholder">快去设计您的专属好物吧～</text>
        <text v-else class="dual__count">{{ designs.length }} 个设计</text>
        <view class="dual__btn">{{ designs.length ? '去看看' : '去设计' }}</view>
      </view>
      <view class="dual__card" @click="go('/pages/orders/index')">
        <text class="dual__title">我的订单</text>
        <view class="dual__icon dual__icon--order"><text>📋</text></view>
        <text v-if="!orders.length" class="dual__placeholder">快去首页选购吧～</text>
        <text v-else class="dual__count">{{ orders.length }} 笔订单</text>
        <view class="dual__btn">{{ orders.length ? '去看看' : '去首页' }}</view>
      </view>
    </view>

    <!-- 订单状态快捷 -->
    <view class="orders-quick">
      <view
        v-for="s in orderStatuses"
        :key="s.key"
        class="orders-quick__item"
        @click="go(`/pages/orders/index?status=${s.key}`)"
      >
        <view class="orders-quick__icon">
          <text>{{ s.icon }}</text>
          <text v-if="orderCounts[s.key]" class="orders-quick__badge">{{ orderCounts[s.key] }}</text>
        </view>
        <text class="orders-quick__label">{{ s.label }}</text>
      </view>
    </view>

    <!-- 菜单列表 -->
    <view class="menu">
      <view class="menu__item" @click="go('/pages/messages/index')">
        <text class="menu__icon">🔔</text>
        <text class="menu__label">消息中心</text>
        <text v-if="unread > 0" class="menu__badge">{{ unread }}</text>
        <text class="menu__arrow">›</text>
      </view>
      <view class="menu__item" @click="go('/pages/addresses/index')">
        <text class="menu__icon">📍</text>
        <text class="menu__label">地址管理</text>
        <text class="menu__arrow">›</text>
      </view>
      <view class="menu__item" @click="onContact">
        <text class="menu__icon">💬</text>
        <text class="menu__label">联系客服</text>
        <text class="menu__arrow">›</text>
      </view>
      <view class="menu__item" @click="uni.showToast({ title: 'aitee v0.2.0', icon: 'none' })">
        <text class="menu__icon">ℹ️</text>
        <text class="menu__label">关于 aitee</text>
        <text class="menu__arrow">›</text>
      </view>
    </view>

    <view class="footer-tip">aitee · 把灵感穿上身</view>

    <CustomTabBar current="mine" />
  </view>
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
  display: flex; align-items: center; gap: 12px;
  &__avatar {
    width: 56px; height: 56px; border-radius: 50%;
    overflow: hidden;
    flex-shrink: 0;
    background: linear-gradient(135deg, #ff7a2a, #ff4d4f);
    display: flex; align-items: center; justify-content: center;
    text { color: #fff; font-size: 24px; font-weight: 800; }
    &--ph text { color: #fff; }
  }
  &__avatar-img { width: 100%; height: 100%; }
  &__body { flex: 1; min-width: 0; }
  &__name { display: block; font-size: 16px; font-weight: 700; color: $color-text-primary; }
  &__sub { display: block; font-size: 12px; color: $color-text-secondary; margin-top: 4px; }
  &__settings {
    width: 36px; height: 36px; line-height: 36px; text-align: center;
    border-radius: 50%; background: rgba(0,0,0,.04);
    color: $color-text-primary; font-size: 18px;
  }
}

.coupon-banner {
  margin: 12px;
  padding: 12px 16px;
  background: linear-gradient(90deg, #ffe4e6 0%, #fff7f0 100%);
  border-radius: 12px;
  display: flex; align-items: center; gap: 10px;
  &__icon {
    width: 32px; height: 32px; line-height: 32px;
    text-align: center;
    font-size: 22px;
  }
  &__body { flex: 1; }
  &__title { display: block; font-size: 14px; font-weight: 700; color: $color-text-primary; }
  &__sub { display: block; font-size: 12px; color: $color-primary; margin-top: 2px; }
  &__arrow { color: $color-text-secondary; font-size: 18px; }
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
    box-shadow: 0 2px 6px rgba(0,0,0,.04);
  }
  &__title { display: block; font-size: 13px; font-weight: 700; text-align: left; }
  &__icon {
    margin: 8px 0 0; font-size: 36px;
    &--design text { color: rgba(255,77,79,.4); }
    &--order text { color: rgba(34,197,94,.5); }
  }
  &__placeholder { display: block; font-size: 11px; color: $color-text-secondary; margin-top: 4px; }
  &__count { display: block; font-size: 12px; color: $color-primary; font-weight: 600; margin-top: 4px; }
  &__btn {
    margin-top: 10px;
    background: $color-bg-tag;
    border-radius: 999px;
    padding: 6px 14px;
    font-size: 12px;
    color: $color-text-primary;
    display: inline-block;
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
    display: flex; flex-direction: column; align-items: center; gap: 4px;
  }
  &__icon {
    width: 32px; height: 32px;
    position: relative;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 22px;
  }
  &__badge {
    position: absolute; top: -4px; right: -8px;
    min-width: 16px; height: 16px; padding: 0 4px;
    background: $color-primary; color: #fff;
    border-radius: 8px;
    font-size: 10px; font-weight: 600;
    line-height: 16px; text-align: center;
  }
  &__label { font-size: 11px; color: $color-text-secondary; }
}

.menu {
  background: #fff;
  margin: 12px;
  border-radius: 12px;
  overflow: hidden;
  &__item {
    display: flex; align-items: center;
    height: 48px;
    padding: 0 14px;
    gap: 10px;
    border-bottom: 1px solid $color-divider;
    &:last-child { border-bottom: 0; }
  }
  &__icon { font-size: 18px; }
  &__label { flex: 1; font-size: 14px; color: $color-text-primary; }
  &__badge { background: $color-primary; color: #fff; padding: 1px 6px; border-radius: 8px; font-size: 10px; margin-right: 6px; }
  &__arrow { font-size: 18px; color: $color-text-placeholder; }
}

.footer-tip { text-align: center; font-size: 11px; color: $color-text-placeholder; padding: 24px 0; }
</style>
