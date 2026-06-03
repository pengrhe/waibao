<script setup lang="ts">
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import BrandHeader from '../../components/BrandHeader.vue'
import { Product, Cart, User } from '../../api'
import { useAuthStore } from '../../store/auth'
import { setShareInfo } from '../../utils/platform'

const product = ref<any>(null)
const selectedColor = ref<string>('')
const selectedSize = ref<string>('')
const qty = ref(1)
const adding = ref(false)
const buyingNow = ref(false)
const auth = useAuthStore()

const colors = computed(() => {
  const set = new Set<string>()
  ;(product.value?.skus || []).forEach((s: any) => set.add(s.color))
  return Array.from(set)
})

const sizes = computed(() => {
  const set = new Set<string>()
  ;(product.value?.skus || []).forEach((s: any) => {
    if (!selectedColor.value || s.color === selectedColor.value) set.add(s.size)
  })
  return Array.from(set)
})

const matchedSku = computed(() => {
  if (!product.value) return null
  return product.value.skus.find(
    (s: any) => s.color === selectedColor.value && s.size === selectedSize.value
  ) || null
})

const stockHint = computed(() => {
  if (!matchedSku.value) return ''
  const st = matchedSku.value.stock
  if (st == null) return ''
  if (st <= 0) return '已售罄'
  if (st < 10) return `仅剩 ${st} 件`
  return `库存 ${st}+`
})

function colorBg(c: string) {
  const map: Record<string, string> = {
    白: '#ffffff', 白色: '#ffffff',
    黑: '#1f2937', 黑色: '#1f2937',
    灰: '#9ca3af', 灰色: '#9ca3af',
    红: '#ef4444', 红色: '#ef4444',
    粉: '#f9a8d4', 粉色: '#f9a8d4',
    蓝: '#3b82f6', 蓝色: '#3b82f6',
    绿: '#22c55e', 绿色: '#22c55e',
    黄: '#facc15', 黄色: '#facc15',
    橙: '#fb923c', 橙色: '#fb923c',
    紫: '#a855f7', 紫色: '#a855f7',
    棕: '#92400e', 棕色: '#92400e',
    米白: '#f5f1ea', 卡其: '#d4c5a0',
  }
  return c?.startsWith('#') ? c : (map[c] || '#f5f5f5')
}

onLoad(async (opt) => {
  const id = Number(opt?.id || 1)
  product.value = await Product.detail(id)
  if (opt?.color) selectedColor.value = decodeURIComponent(String(opt.color))
  if (product.value?.skus?.length) {
    if (!selectedColor.value) selectedColor.value = product.value.skus[0].color
    selectedSize.value = product.value.skus.find((s: any) => s.color === selectedColor.value)?.size || product.value.skus[0].size
  }
  if (product.value) {
    setShareInfo({
      title: `${product.value.name} - aitee 一键定制`,
      path: `/pages/product-detail/index?id=${product.value.id}`,
      imageUrl: product.value.main_image_url,
    })
  }
})

function ensureLogin(): boolean {
  if (!auth.isAuthed) {
    uni.navigateTo({ url: '/pages/login/index' })
    return false
  }
  return true
}

async function addToCart() {
  if (!ensureLogin()) return
  if (!matchedSku.value) { uni.showToast({ title: '请选择规格', icon: 'none' }); return }
  adding.value = true
  try {
    await Cart.add({
      sku_id: matchedSku.value.id,
      qty: qty.value,
      snapshot: { preview_url: product.value.main_image_url, name: product.value.name },
    })
    User.reportPref('color', selectedColor.value).catch(() => {})
    User.reportPref('size', selectedSize.value).catch(() => {})
    User.reportPref('product_id', product.value.id).catch(() => {})
    uni.showToast({ title: '已加入购物车', icon: 'success' })
  } finally { adding.value = false }
}

async function buyNow() {
  if (!ensureLogin() || !matchedSku.value) {
    uni.showToast({ title: '请选择规格', icon: 'none' })
    return
  }
  buyingNow.value = true
  try {
    uni.navigateTo({
      url: `/pages/checkout/index?sku_id=${matchedSku.value.id}&qty=${qty.value}&pname=${encodeURIComponent(product.value.name)}&price=${matchedSku.value.price}`,
    })
  } finally { buyingNow.value = false }
}

function goEditor() {
  if (!matchedSku.value) { uni.showToast({ title: '请先选规格', icon: 'none' }); return }
  uni.navigateTo({
    url: `/pages/editor/index?product_id=${product.value.id}&sku_id=${matchedSku.value.id}&color=${encodeURIComponent(selectedColor.value)}`,
  })
}
</script>

<template>
  <view v-if="product" class="page">
    <BrandHeader title="商品详情" show-back :show-logo="false" />

    <!-- 商品大图 -->
    <view class="hero" :style="{ background: colorBg(selectedColor) }">
      <image v-if="product.main_image_url" :src="product.main_image_url" class="hero__img" mode="aspectFit" />
    </view>

    <!-- 标题区 -->
    <view class="info">
      <view class="info__price-row">
        <text class="info__price">¥ {{ matchedSku?.price ?? product.base_price }}</text>
        <text v-if="stockHint" class="info__stock">{{ stockHint }}</text>
      </view>
      <text class="info__title">{{ product.name }}</text>
      <text v-if="product.subtitle" class="info__sub">{{ product.subtitle }}</text>
    </view>

    <!-- 颜色 -->
    <view class="card">
      <view class="card__label">
        <text>颜色</text>
        <text class="card__pick">{{ selectedColor || '请选择' }}</text>
      </view>
      <view class="chips">
        <view
          v-for="c in colors"
          :key="c"
          class="chip-color"
          :class="{ on: c === selectedColor }"
          @click="selectedColor = c"
        >
          <view class="chip-color__dot" :style="{ background: colorBg(c) }" />
          <text class="chip-color__txt">{{ c }}</text>
        </view>
      </view>
    </view>

    <!-- 尺码 -->
    <view class="card">
      <view class="card__label">
        <text>尺码</text>
        <text class="card__pick">{{ selectedSize || '请选择' }}</text>
      </view>
      <view class="chips">
        <view
          v-for="s in sizes"
          :key="s"
          class="chip-size"
          :class="{ on: s === selectedSize }"
          @click="selectedSize = s"
        >{{ s }}</view>
      </view>
    </view>

    <!-- 数量 -->
    <view class="card">
      <view class="card__label">
        <text>数量</text>
      </view>
      <view class="qty">
        <view class="qty__b" @click="qty = Math.max(1, qty - 1)">-</view>
        <text class="qty__n">{{ qty }}</text>
        <view class="qty__b" @click="qty = qty + 1">+</view>
      </view>
    </view>

    <!-- 详情描述 -->
    <view class="desc-card">
      <view class="desc-card__head">
        <text class="desc-card__title">商品详情</text>
        <text class="desc-card__sub">— 滑动查看 —</text>
      </view>
      <view class="desc-card__body">
        <text v-if="product.description">{{ product.description }}</text>
        <text v-else>使用环保印染技术，100% 纯棉，亲肤透气，机洗不变形。每一件都由 aitee 智能产线完成定制打印，48 小时内出货。</text>
      </view>
      <view class="desc-card__highlights">
        <view class="hi"><text class="hi__icon">🚚</text><text>48 小时打印发货</text></view>
        <view class="hi"><text class="hi__icon">🛡️</text><text>支持 7 天无理由</text></view>
        <view class="hi"><text class="hi__icon">🌱</text><text>环保印染 · 不褪色</text></view>
      </view>
    </view>

    <!-- 底部 CTA -->
    <view class="bar">
      <view class="bar__icon" @click="goEditor">
        <text class="bar__icon-emoji">🎨</text>
        <text class="bar__icon-label">去定制</text>
      </view>
      <view class="bar__btn bar__btn--out" :class="{ 'bar__btn--dis': adding }" @click="addToCart">
        <text>{{ adding ? '加入中…' : '加入购物车' }}</text>
      </view>
      <view class="bar__btn bar__btn--pri" :class="{ 'bar__btn--dis': buyingNow }" @click="buyNow">
        <text>{{ buyingNow ? '处理中…' : '立即购买' }}</text>
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.page { padding-bottom: 80px; min-height: 100vh; background: $color-bg-page; }

.hero {
  position: relative;
  height: 360px;
  display: flex; align-items: center; justify-content: center;
  transition: background .3s;
  &__img { width: 78%; height: 78%; }
}

.info {
  background: #fff;
  padding: 16px;
  &__price-row { display: flex; align-items: baseline; justify-content: space-between; }
  &__price { color: $color-primary; font-size: 24px; font-weight: 900; }
  &__stock { font-size: 11px; color: $color-warning; font-weight: 600; }
  &__title { display: block; font-size: 16px; font-weight: 700; color: #1f2937; margin-top: 8px; }
  &__sub { display: block; font-size: 12px; color: $color-text-placeholder; margin-top: 4px; }
}

.card {
  background: #fff;
  margin-top: 10px;
  padding: 14px 16px;
  &__label { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 10px; font-size: 13px; color: $color-text-regular; font-weight: 600; }
  &__pick { color: $color-text-placeholder; font-size: 12px; font-weight: 400; }
}

.chips { display: flex; flex-wrap: wrap; gap: 8px; }

.chip-color {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 6px 12px 6px 6px;
  background: $color-bg-tag;
  border-radius: 999px;
  font-size: 12px;
  border: 1px solid transparent;
  &.on { border-color: $color-primary; background: $color-primary-light; color: $color-primary; font-weight: 700; }
  &__dot { width: 16px; height: 16px; border-radius: 50%; border: 1px solid rgba(0,0,0,.1); }
  &__txt { line-height: 1; }
}

.chip-size {
  padding: 6px 16px;
  background: $color-bg-tag;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  color: $color-text-regular;
  border: 1px solid transparent;
  &.on { background: $color-primary-light; color: $color-primary; border-color: $color-primary; }
}

.qty {
  display: inline-flex; align-items: center; gap: 14px;
  background: $color-bg-tag;
  padding: 4px 10px;
  border-radius: 999px;
  &__b { width: 28px; height: 28px; line-height: 28px; text-align: center; background: #fff; border-radius: 14px; font-size: 16px; color: $color-text-regular; }
  &__n { font-weight: 700; min-width: 24px; text-align: center; }
}

.desc-card {
  background: #fff;
  margin-top: 10px;
  padding: 14px 16px;
  &__head { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 10px; }
  &__title { font-size: 14px; font-weight: 800; color: #1f2937; }
  &__sub { font-size: 10px; color: $color-text-placeholder; }
  &__body { color: $color-text-regular; line-height: 1.7; font-size: 13px; }
  &__highlights { display: flex; gap: 8px; margin-top: 12px; flex-wrap: wrap; }
}
.hi { flex: 1; min-width: 100px; display: flex; align-items: center; gap: 4px; padding: 6px 10px; background: $color-bg-tag; border-radius: 8px; font-size: 11px; color: $color-text-regular;
  &__icon { font-size: 14px; }
}

.bar {
  position: fixed; bottom: 0; left: 0; right: 0;
  background: #fff;
  padding: 8px 12px;
  display: flex; gap: 8px; align-items: center;
  border-top: 1px solid $color-divider;
  z-index: 9;
}
.bar__icon {
  width: 56px; text-align: center; padding-top: 2px; color: $color-text-secondary;
  &-emoji { display: block; font-size: 20px; }
  &-label { display: block; font-size: 10px; margin-top: 2px; }
}
.bar__btn {
  flex: 1; height: 42px; line-height: 42px; text-align: center;
  border-radius: 999px;
  font-size: 14px; font-weight: 700;
  &--out { background: $color-primary-light; color: $color-primary; }
  &--pri { background: linear-gradient(135deg, #ff7a2a, #ff4d4f); color: #fff;
    box-shadow: 0 4px 12px rgba(255,77,79,.3);
  }
  &--dis { opacity: .6; }
}
</style>
