<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { Design, Pattern, Cart, Product } from '../../api'
import { useAuthStore } from '../../store/auth'
import { setShareInfo, requestSubscribe, WX_TPL, isWechat } from '../../utils/platform'
import { API_BASE } from '../../utils/env'

interface Layer {
  id: string
  type: 'pattern' | 'text' | 'upload' | 'ai'
  image_url?: string
  text?: string
  color?: string
  x: number
  y: number
  w: number
  h: number
  side: 'front' | 'back'
}

const auth = useAuthStore()
const productId = ref<number | undefined>()
const skuId = ref<number | undefined>()
const product = ref<any>(null)

// 颜色选择（取自产品 sku 的 color）
const tshirtColor = ref<string>('白')
const side = ref<'front' | 'back'>('front')
const layers = ref<Layer[]>([])
const selectedId = ref<string | null>(null)
const history = ref<Layer[][]>([])
const future = ref<Layer[][]>([])

// 弹层状态
const showPatternPanel = ref(false)
const showTextEditor = ref(false)
const showSizePicker = ref(false)
const showColorPanel = ref(false)
const patternList = ref<any[]>([])
const newText = reactive({ value: '', color: '#1F2937' })
const sizeChosen = ref('')

const currentLayers = computed(() => layers.value.filter((l) => l.side === side.value))
const canUndo = computed(() => history.value.length > 0)
const canRedo = computed(() => future.value.length > 0)

const colors = computed<string[]>(() => {
  const set = new Set<string>()
  ;(product.value?.skus || []).forEach((s: any) => set.add(s.color))
  return Array.from(set)
})

const sizes = computed<string[]>(() => {
  const set = new Set<string>()
  ;(product.value?.skus || [])
    .filter((s: any) => s.color === tshirtColor.value)
    .forEach((s: any) => set.add(s.size))
  return Array.from(set)
})

// 颜色名 -> hex（与后端 services/mockup.py COLOR_MAP 一致），兼容英文 / 中文 / hex。
function colorBg(c?: string) {
  if (!c) return '#f5f5f5'
  if (c.startsWith('#')) return c
  const map: Record<string, string> = {
    white: '#ffffff', black: '#1f2937', gray: '#9ca3af', grey: '#9ca3af',
    red: '#ef4444', pink: '#f9a8d4', blue: '#3b82f6', green: '#22c55e',
    yellow: '#facc15', orange: '#fb923c', purple: '#a855f7', brown: '#92400e',
    natural: '#f5f1ea', khaki: '#d4c5a0',
    白: '#ffffff', 黑: '#1f2937', 灰: '#9ca3af',
    红: '#ef4444', 粉: '#f9a8d4', 蓝: '#3b82f6',
    绿: '#22c55e', 黄: '#facc15', 橙: '#fb923c',
    紫: '#a855f7', 棕: '#92400e', 米白: '#f5f1ea', 卡其: '#d4c5a0',
  }
  const key = c.toLowerCase()
  if (map[key]) return map[key]
  for (const k of Object.keys(map)) if (c.includes(k)) return map[k]
  return '#f5f5f5'
}

// 底图统一走后端：按当前商品 + 颜色 + 正反面实时取 SVG
const mockupUrl = computed(() => {
  const pid = productId.value || 1
  const color = encodeURIComponent(tshirtColor.value || '')
  return `${API_BASE}/products/${pid}/mockup?color=${color}&side=${side.value}`
})

onLoad(async (opt) => {
  productId.value = opt?.product_id ? Number(opt.product_id) : 1
  skuId.value = opt?.sku_id ? Number(opt.sku_id) : undefined
  if (opt?.color) tshirtColor.value = decodeURIComponent(String(opt.color))

  try {
    product.value = await Product.detail(productId.value)
    if (!opt?.color && product.value?.skus?.length) {
      tshirtColor.value = product.value.skus[0].color
    }
  } catch {}

  if (opt?.pattern_url) {
    const url = decodeURIComponent(String(opt.pattern_url))
    addPatternLayer(url)
  }

  setShareInfo({
    title: '我在 aitee 设计了一件潮 T 恤，快来看',
    path: `/pages/editor/index${productId.value ? `?product_id=${productId.value}` : ''}`,
  })
})

function snapshot() {
  history.value.push(JSON.parse(JSON.stringify(layers.value)))
  if (history.value.length > 30) history.value.shift()
  future.value = []
}

function undo() {
  if (!history.value.length) return
  future.value.push(JSON.parse(JSON.stringify(layers.value)))
  layers.value = history.value.pop()!
}

function redo() {
  if (!future.value.length) return
  history.value.push(JSON.parse(JSON.stringify(layers.value)))
  layers.value = future.value.pop()!
}

function addPatternLayer(url: string, type: 'pattern' | 'upload' | 'ai' = 'pattern') {
  snapshot()
  layers.value.push({
    id: `${type[0]}_${Date.now()}`,
    type,
    image_url: url,
    x: 80, y: 100, w: 140, h: 140,
    side: side.value,
  })
  selectedId.value = layers.value[layers.value.length - 1].id
}

function addText() {
  const v = newText.value.trim()
  if (!v) { uni.showToast({ title: '请输入文字', icon: 'none' }); return }
  snapshot()
  layers.value.push({
    id: `t_${Date.now()}`,
    type: 'text',
    text: v,
    color: newText.color,
    x: 90, y: 90, w: 180, h: 40,
    side: side.value,
  })
  selectedId.value = layers.value[layers.value.length - 1].id
  newText.value = ''
  showTextEditor.value = false
}

// 自实现的拖拽（替代 uniapp H5 缺失的 <movable-view>，同时兼容小程序）
let dragState: {
  layerId: string
  startTouchX: number
  startTouchY: number
  startLayerX: number
  startLayerY: number
  moved: boolean
} | null = null

function pickPoint(e: any): { x: number; y: number } | null {
  const t = e?.touches?.[0] || e?.changedTouches?.[0]
  if (!t) return null
  return { x: t.clientX ?? t.pageX ?? 0, y: t.clientY ?? t.pageY ?? 0 }
}

function onDragStart(l: Layer, e: any) {
  const p = pickPoint(e)
  if (!p) return
  selectedId.value = l.id
  dragState = {
    layerId: l.id,
    startTouchX: p.x,
    startTouchY: p.y,
    startLayerX: l.x,
    startLayerY: l.y,
    moved: false,
  }
}

function onDragMove(e: any) {
  if (!dragState) return
  const p = pickPoint(e)
  if (!p) return
  const dx = p.x - dragState.startTouchX
  const dy = p.y - dragState.startTouchY
  // 只在真正发生位移时入栈历史，避免点选也产生 undo 记录
  if (!dragState.moved && (Math.abs(dx) > 2 || Math.abs(dy) > 2)) {
    snapshot()
    dragState.moved = true
  }
  if (!dragState.moved) return
  const layer = layers.value.find((x) => x.id === dragState!.layerId)
  if (!layer) return
  layer.x = Math.max(0, dragState.startLayerX + dx)
  layer.y = Math.max(0, dragState.startLayerY + dy)
}

function onDragEnd() {
  dragState = null
}

function selectLayer(id: string, e: any) {
  e?.stopPropagation?.()
  selectedId.value = id
}

function deselect() {
  selectedId.value = null
}

function bringForward() {
  if (!selectedId.value) return
  const i = layers.value.findIndex((l) => l.id === selectedId.value)
  if (i >= 0 && i < layers.value.length - 1) {
    snapshot()
    const tmp = layers.value[i]
    layers.value[i] = layers.value[i + 1]
    layers.value[i + 1] = tmp
  }
}

function sendBackward() {
  if (!selectedId.value) return
  const i = layers.value.findIndex((l) => l.id === selectedId.value)
  if (i > 0) {
    snapshot()
    const tmp = layers.value[i]
    layers.value[i] = layers.value[i - 1]
    layers.value[i - 1] = tmp
  }
}

function removeSelected() {
  if (!selectedId.value) return
  snapshot()
  layers.value = layers.value.filter((l) => l.id !== selectedId.value)
  selectedId.value = null
}

function flipSide() {
  side.value = side.value === 'front' ? 'back' : 'front'
  selectedId.value = null
}

async function openPatternPanel() {
  if (!patternList.value.length) {
    try { patternList.value = await Pattern.list() } catch {}
  }
  showPatternPanel.value = true
}

function pickPattern(p: any) {
  addPatternLayer(p.image_url)
  showPatternPanel.value = false
}

function onUpload() {
  uni.chooseImage({
    count: 1,
    success: (r: any) => {
      const u = (r.tempFilePaths && r.tempFilePaths[0]) || ''
      if (u) addPatternLayer(u, 'upload')
    },
  })
}

function onAi() {
  uni.navigateTo({ url: '/pages/ai-create/index' })
}

async function onSave(silent = false) {
  if (!auth.isAuthed) { uni.navigateTo({ url: '/pages/login/index' }); return }
  if (!layers.value.length && !silent) {
    uni.showToast({ title: '画布是空的', icon: 'none' })
    return
  }
  if (!silent) uni.showLoading({ title: '保存中…', mask: true })
  try {
    const d: any = await Design.create({
      name: `设计-${new Date().toLocaleString()}`,
      product_id: productId.value,
      sku_id: skuId.value,
      side: side.value,
      layers: layers.value,
    })
    if (!silent) {
      uni.hideLoading()
      uni.showToast({ title: '设计已保存', icon: 'success' })
    }
    return d
  } catch {
    if (!silent) {
      uni.hideLoading()
      uni.showToast({ title: '保存失败', icon: 'none' })
    }
  }
}

function onBuy() {
  if (!layers.value.length) {
    uni.showToast({ title: '请先添加印花/文字/AI 图', icon: 'none' })
    return
  }
  showSizePicker.value = true
}

async function confirmAddToCart() {
  if (!sizeChosen.value) { uni.showToast({ title: '请选择尺码', icon: 'none' }); return }
  if (!auth.isAuthed) { uni.navigateTo({ url: '/pages/login/index' }); return }
  const matchedSku = product.value?.skus?.find((s: any) => s.color === tshirtColor.value && s.size === sizeChosen.value)
  if (!matchedSku) { uni.showToast({ title: '该规格暂未配置', icon: 'none' }); return }
  uni.showLoading({ title: '加入购物车…', mask: true })
  try {
    const d = await onSave(true)
    await Cart.add({
      sku_id: matchedSku.id,
      qty: 1,
      design_id: d?.id,
      snapshot: {
        preview_url: layers.value[0]?.image_url,
        name: product.value?.name,
        design_id: d?.id,
      },
    })
    if (isWechat) requestSubscribe([WX_TPL.order_paid, WX_TPL.print_ready]).catch(() => {})
    uni.hideLoading()
    uni.showToast({ title: '已加入购物车', icon: 'success' })
    showSizePicker.value = false
    sizeChosen.value = ''
  } catch {
    uni.hideLoading()
    uni.showToast({ title: '加入失败', icon: 'none' })
  }
}

function back() {
  uni.navigateBack().catch(() => uni.switchTab({ url: '/pages/index/index' }))
}

function switchProduct() {
  uni.redirectTo({ url: '/pages/product-list/index' })
}
</script>

<template>
  <view class="editor">
    <!-- 顶部栏 -->
    <view class="editor__header">
      <view class="editor__back" @click="back">‹</view>
      <view class="editor__switch" @click="switchProduct">
        <text>切换款式</text>
        <text class="editor__arrow">▾</text>
      </view>
      <view class="editor__save" :class="{ 'is-dis': !layers.length }" @click="onSave(false)">保存设计</view>
    </view>

    <!-- 颜色色块 -->
    <view class="editor__colors">
      <view
        v-for="c in colors"
        :key="c"
        class="editor__color"
        :class="{
          'editor__color--active': tshirtColor === c,
          'editor__color--white': colorBg(c).toLowerCase() === '#ffffff',
        }"
        :style="{ background: colorBg(c) }"
        @click="tshirtColor = c"
      />
    </view>

    <!-- 画布 -->
    <view class="editor__stage" @click="deselect">
      <view class="editor__canvas">
        <!-- 底图：从后端按颜色 / 正反面实时取（SVG），不在端内写死 -->
        <image class="editor__mockup" :src="mockupUrl" mode="aspectFit" />
        <!-- 安全区虚线框 -->
        <view class="editor__safezone" />

        <!-- 图层（自实现拖拽，兼容 H5 + 小程序）-->
        <view class="editor__movable">
          <view
            v-for="l in currentLayers"
            :key="l.id"
            :class="['layer', { 'layer--active': selectedId === l.id }]"
            :style="{ left: l.x + 'px', top: l.y + 'px', width: l.w + 'px', height: l.h + 'px' }"
            @touchstart.stop="onDragStart(l, $event)"
            @touchmove.stop.prevent="onDragMove($event)"
            @touchend.stop="onDragEnd"
            @touchcancel.stop="onDragEnd"
            @click.stop="selectLayer(l.id, $event)"
          >
            <image v-if="l.type !== 'text'" :src="l.image_url" mode="aspectFit" class="layer__img" />
            <view v-else class="layer__text" :style="{ color: l.color }">{{ l.text }}</view>
          </view>
        </view>

        <!-- 右侧浮按钮 -->
        <view class="editor__floats">
          <view class="float-btn" :class="{ 'is-dis': !selectedId }" @click="bringForward">
            <text class="float-btn__icon">▲</text>
            <text class="float-btn__label">上移</text>
          </view>
          <view class="float-btn" :class="{ 'is-dis': !selectedId }" @click="sendBackward">
            <text class="float-btn__icon">▼</text>
            <text class="float-btn__label">下移</text>
          </view>
          <view class="float-btn" :class="{ 'is-dis': !selectedId }" @click="removeSelected">
            <text class="float-btn__icon">🗑</text>
            <text class="float-btn__label">删除</text>
          </view>
          <view class="float-btn" @click="flipSide">
            <text class="float-btn__icon">↻</text>
            <text class="float-btn__label">{{ side === 'front' ? '背面' : '正面' }}</text>
          </view>
        </view>

        <!-- 撤销/重做 -->
        <view class="editor__history">
          <view class="hist-btn" :class="{ 'is-dis': !canUndo }" @click="undo"><text>↶</text></view>
          <view class="hist-btn" :class="{ 'is-dis': !canRedo }" @click="redo"><text>↷</text></view>
        </view>
      </view>
    </view>

    <!-- 工具栏 -->
    <view class="editor__toolbar">
      <view class="tool" @click="openPatternPanel">
        <text class="tool__icon">🎨</text>
        <text class="tool__label">印花素材</text>
      </view>
      <view class="tool" @click="showTextEditor = true">
        <text class="tool__icon">🅣</text>
        <text class="tool__label">文字</text>
      </view>
      <view class="tool" @click="onUpload">
        <text class="tool__icon">🖼</text>
        <text class="tool__label">来图定制</text>
      </view>
      <view class="tool" @click="onAi">
        <text class="tool__icon tool__icon--accent">✦</text>
        <text class="tool__label tool__label--accent">AI 创作</text>
      </view>
    </view>

    <!-- 底部 CTA -->
    <view class="editor__cta">
      <view class="editor__price">
        <text class="editor__price-label">¥</text>
        <text class="editor__price-num">{{ product?.base_price || 0 }}</text>
      </view>
      <view class="editor__buy" @click="onBuy">
        <text>🛒 加入购物车</text>
      </view>
    </view>

    <!-- 印花弹层 -->
    <view v-if="showPatternPanel" class="popup" @click="showPatternPanel = false">
      <view class="popup__sheet" @click.stop>
        <text class="popup__title">选择印花</text>
        <scroll-view scroll-y class="popup__scroll">
          <view class="picker__grid">
            <view v-for="p in patternList" :key="p.id" class="picker__item" @click="pickPattern(p)">
              <image :src="p.image_url" class="picker__img" mode="aspectFit" />
              <text class="picker__name">{{ p.title || p.name }}</text>
            </view>
          </view>
        </scroll-view>
      </view>
    </view>

    <!-- 文字弹层 -->
    <view v-if="showTextEditor" class="popup" @click="showTextEditor = false">
      <view class="popup__sheet popup__sheet--auto" @click.stop>
        <text class="popup__title">添加文字</text>
        <textarea v-model="newText.value" class="text-ta" placeholder="输入要印的文字…" />
        <view class="text-colors">
          <text class="text-colors__label">颜色：</text>
          <view
            v-for="c in ['#1F2937','#FF4D4F','#FACC15','#10B981','#3B82F6','#A855F7','#FFFFFF']"
            :key="c"
            class="text-color"
            :class="{ on: newText.color === c }"
            :style="{ background: c }"
            @click="newText.color = c"
          />
        </view>
        <view class="popup__actions">
          <view class="btn-ghost" @click="showTextEditor = false">取消</view>
          <view class="btn-primary" @click="addText">确定</view>
        </view>
      </view>
    </view>

    <!-- 选尺码弹层 -->
    <view v-if="showSizePicker" class="popup" @click="showSizePicker = false">
      <view class="popup__sheet popup__sheet--auto" @click.stop>
        <text class="popup__title">选择尺码</text>
        <view class="size-grid">
          <view
            v-for="s in sizes"
            :key="s"
            class="size-grid__item"
            :class="{ on: sizeChosen === s }"
            @click="sizeChosen = s"
          >{{ s }}</view>
        </view>
        <view class="btn-primary" style="margin-top: 16px" @click="confirmAddToCart">确认加入购物车</view>
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.editor {
  min-height: 100vh;
  background: #f9fafb;
  display: flex; flex-direction: column;
  padding-bottom: 120px;

  &__header {
    height: 48px;
    padding: 0 12px;
    background: rgba(255,255,255,.96);
    display: flex; align-items: center; justify-content: space-between;
    position: sticky; top: 0; z-index: 10;
  }
  &__back {
    width: 36px; height: 36px; line-height: 34px; text-align: center;
    border-radius: 50%;
    background: $color-bg-tag;
    font-size: 22px;
  }
  &__switch {
    height: 32px; padding: 0 12px; line-height: 32px;
    border-radius: 999px;
    background: rgba(0,0,0,.04);
    color: $color-text-primary;
    font-size: 13px; font-weight: 600;
    display: inline-flex; align-items: center; gap: 4px;
  }
  &__arrow { font-size: 10px; }
  &__save {
    height: 32px; padding: 0 14px; line-height: 32px;
    border-radius: 999px;
    background: $color-primary;
    color: #fff;
    font-size: 13px; font-weight: 700;
    &.is-dis { background: $color-bg-tag; color: $color-text-secondary; }
  }

  &__colors {
    display: flex; align-items: center; justify-content: center; gap: 12px;
    padding: 8px 16px 0;
  }
  &__color {
    width: 24px; height: 24px;
    border-radius: 50%;
    border: 1px solid rgba(0,0,0,.1);
    transition: transform .15s;
    &--white { border-color: $color-border; }
    &--active { transform: scale(1.2); box-shadow: 0 0 0 2px #fff, 0 0 0 4px $color-primary; }
  }

  &__stage {
    position: relative;
    margin: 8px 16px 0;
    background: #fff;
    border-radius: 16px;
    overflow: hidden;
    height: 420px;
  }
  &__canvas { position: absolute; inset: 0; }

  &__mockup {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    z-index: 1;
  }

  &__safezone {
    position: absolute;
    left: 28%; top: 22%;
    width: 44%; height: 50%;
    border: 1.5px dashed rgba(255,77,79,.3);
    border-radius: 6px;
    pointer-events: none;
    z-index: 2;
  }

  &__movable { position: absolute; inset: 20px; z-index: 3; }

  &__floats {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    display: flex; flex-direction: column; gap: 8px;
    z-index: 4;
  }
  &__history {
    position: absolute; left: 12px; bottom: 12px;
    display: flex; gap: 8px;
    z-index: 4;
  }

  &__toolbar {
    display: flex; justify-content: space-around;
    background: #fff;
    padding: 12px 0;
    margin-top: 8px;
  }

  &__cta {
    position: fixed; bottom: 0; left: 0; right: 0;
    height: 60px;
    background: #fff;
    border-top: 1px solid $color-divider;
    display: flex; align-items: center;
    padding: 0 16px;
    z-index: 9;
  }
  &__price { flex: 1; color: $color-primary; font-weight: 800; }
  &__price-label { font-size: 14px; }
  &__price-num { font-size: 24px; margin-left: 2px; font-weight: 900; }
  &__buy {
    height: 42px; padding: 0 24px; line-height: 42px;
    background: linear-gradient(135deg, #ff7a2a, #ff4d4f);
    color: #fff;
    border-radius: 999px;
    font-size: 14px; font-weight: 700;
    box-shadow: 0 4px 14px rgba(255,77,79,.35);
  }
}

.layer {
  position: absolute;            // 自实现拖拽：用 left/top 摆位
  background: transparent;
  display: flex; align-items: center; justify-content: center;
  // 阻止浏览器把触摸/鼠标手势当作滚动/缩放，确保事件全交给 JS
  touch-action: none;
  user-select: none;
  -webkit-user-select: none;
  -webkit-touch-callout: none;
  &--active { outline: 2px dashed $color-primary; outline-offset: 2px; }
  // 子元素事件透传到父级 .layer，避免原生 <img> drag 抢占触摸
  &__img {
    width: 100%; height: 100%;
    pointer-events: none;
    -webkit-user-drag: none;
    user-drag: none;
  }
  &__text {
    width: 100%; height: 100%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 22px;
    pointer-events: none;
  }
}

.float-btn {
  width: 56px;
  border-radius: 12px;
  background: rgba(255,255,255,.95);
  box-shadow: 0 4px 10px rgba(0,0,0,.08);
  padding: 8px 4px;
  display: flex; flex-direction: column; align-items: center; gap: 2px;
  &.is-dis { opacity: .4; }
  &__icon { font-size: 18px; line-height: 1; }
  &__label { font-size: 10px; color: $color-text-primary; font-weight: 500; }
}

.hist-btn {
  width: 36px; height: 36px; line-height: 36px; text-align: center;
  border-radius: 50%;
  background: rgba(255,255,255,.95);
  box-shadow: 0 4px 10px rgba(0,0,0,.08);
  font-size: 18px;
  &.is-dis { opacity: .35; }
}

.tool {
  display: flex; flex-direction: column; align-items: center; gap: 4px;
  font-size: 12px;
  color: $color-text-regular;
  &__icon { font-size: 22px; color: $color-text-primary; line-height: 1;
    &--accent { color: $color-primary; }
  }
  &__label { font-size: 11px;
    &--accent { color: $color-primary; font-weight: 700; }
  }
}

.popup {
  position: fixed; inset: 0;
  background: rgba(0,0,0,.4);
  z-index: 100;
  display: flex; align-items: flex-end;
  &__sheet {
    width: 100%;
    background: #fff;
    border-radius: 16px 16px 0 0;
    padding: 16px;
    max-height: 60vh;
    &--auto { max-height: 70vh; }
  }
  &__title { display: block; font-size: 16px; font-weight: 700; text-align: center; margin-bottom: 12px; }
  &__scroll { max-height: 50vh; }
  &__actions { display: flex; gap: 12px; justify-content: flex-end; margin-top: 14px; }
}

.picker__grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 8px;
}
.picker__item {
  background: #fafafa;
  border-radius: 8px;
  overflow: hidden;
  padding: 4px;
  text-align: center;
}
.picker__img { width: 100%; aspect-ratio: 1; }
.picker__name { display: block; padding: 4px 4px 2px; font-size: 11px; color: $color-text-regular; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }

.text-ta {
  border: 1px solid $color-border;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 14px;
  width: 100%; min-height: 70px;
  box-sizing: border-box;
  margin-bottom: 12px;
}
.text-colors { display: flex; align-items: center; gap: 8px; font-size: 13px; color: $color-text-secondary;
  &__label { flex-shrink: 0; }
}
.text-color {
  width: 22px; height: 22px;
  border-radius: 50%;
  border: 1px solid rgba(0,0,0,.05);
  &.on { box-shadow: 0 0 0 2px #fff, 0 0 0 4px $color-primary; }
}

.btn-ghost {
  padding: 8px 18px;
  background: $color-bg-tag;
  color: $color-text-primary;
  border-radius: 999px;
  font-size: 14px;
  font-weight: 600;
}
.btn-primary {
  padding: 10px 22px;
  background: linear-gradient(135deg, #ff7a2a, #ff4d4f);
  color: #fff;
  border-radius: 999px;
  font-size: 14px;
  font-weight: 700;
  text-align: center;
  box-shadow: 0 4px 12px rgba(255,77,79,.3);
}

.size-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}
.size-grid__item {
  height: 40px; line-height: 40px;
  text-align: center;
  border: 1px solid $color-border;
  border-radius: 8px;
  background: #fff;
  font-size: 14px;
  color: $color-text-primary;
  &.on { border-color: $color-primary; background: $color-primary-light; color: $color-primary; font-weight: 700; }
}
</style>
