<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showDialog, showLoadingToast, showToast } from 'vant'
import { storeToRefs } from 'pinia'
import EditorLayer from '@/components/EditorLayer.vue'
import { useEditorStore } from '@/store/editor'
import { useCartStore } from '@/store/cart'
import { fetchPatternById, fetchPatterns } from '@/api/pattern'
import { saveDesign, getDesign } from '@/api/design'
import { toteMockup, tshirtMockup } from '@/utils/placeholder'
import { uid } from '@/utils/id'
import type { DesignLayer, Pattern } from '@/types'

const route = useRoute()
const router = useRouter()
const editor = useEditorStore()
const cart = useCartStore()

const { product, color, side, layers, sideLayers, activeLayerId, canUndo, canRedo } = storeToRefs(editor)

const canvasRef = ref<HTMLElement | null>(null)
const showPatternPicker = ref(false)
const showTextEditor = ref(false)
const showSizePicker = ref(false)
const patternList = ref<Pattern[]>([])
const textInput = ref('')
const textColor = ref('#1F2937')
const sizeChosen = ref<string>('')
const fileInputRef = ref<HTMLInputElement | null>(null)

const mockupUrl = computed(() => {
  if (product.value.type === 'tote') return toteMockup(color.value)
  return tshirtMockup(color.value, side.value)
})

async function init() {
  const designId = route.query.designId as string | undefined
  const productId = Number(route.query.productId)
  const patternId = Number(route.query.patternId)
  if (designId) {
    const d = await getDesign(designId)
    if (d) editor.reset(d)
  } else {
    editor.reset()
  }
  if (productId) editor.setProduct(productId)
  if (patternId) {
    const p = await fetchPatternById(patternId)
    if (p) addPatternLayer(p)
  }
}

onMounted(async () => {
  await init()
  await nextTick()
})

// query 变化时（如从 product-picker 返回携带 productId）
watch(
  () => route.query,
  async (q, prev) => {
    if (q.productId && q.productId !== prev?.productId) {
      editor.setProduct(Number(q.productId))
    }
    if (q.patternId && q.patternId !== prev?.patternId) {
      const p = await fetchPatternById(Number(q.patternId))
      if (p) addPatternLayer(p)
    }
    if (q.aiUrl && q.aiUrl !== prev?.aiUrl) {
      editor.addLayer({ source: 'ai', data: q.aiUrl as string, x: 30, y: 25, width: 40, height: 40 })
    }
    if (q.uploadUrl && q.uploadUrl !== prev?.uploadUrl) {
      editor.addLayer({ source: 'upload', data: q.uploadUrl as string, x: 30, y: 25, width: 40, height: 40 })
    }
  },
  { deep: true },
)

function addPatternLayer(p: Pattern) {
  editor.addLayer({
    source: 'pattern',
    data: p.imageUrl,
    text: p.title,
    x: 30,
    y: 25,
    width: 40,
    height: 40,
  })
}

async function openPatternPicker() {
  showPatternPicker.value = true
  if (!patternList.value.length) {
    patternList.value = await fetchPatterns()
  }
}

function pickPattern(p: Pattern) {
  addPatternLayer(p)
  showPatternPicker.value = false
}

function onColorClick(c: string) {
  if (color.value === c) return
  editor.setColor(c)
}

function onSwitchProduct() {
  router.push('/product-picker?from=editor')
}

function onFlipSide() {
  editor.flipSide()
}

function onCanvasClick() {
  if (activeLayerId.value) editor.setActive('')
}

function onLayerUpdate(id: string, patch: Partial<DesignLayer>, commit = false) {
  editor.updateLayer(id, patch, commit)
}

function onLayerActivate(id: string) {
  editor.setActive(id)
}

function onLayerRemove(id: string) {
  editor.removeLayer(id)
}

function commitText() {
  const t = textInput.value.trim()
  if (!t) {
    showToast('请输入文字')
    return
  }
  editor.addLayer({
    source: 'text',
    data: t,
    text: t,
    textColor: textColor.value,
    fontSize: 32,
    x: 30,
    y: 30,
    width: 40,
    height: 18,
  })
  showTextEditor.value = false
  textInput.value = ''
}

function onUploadClick() {
  fileInputRef.value?.click()
}

function onFileChange(e: Event) {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => {
    editor.addLayer({
      source: 'upload',
      data: reader.result as string,
      x: 30,
      y: 25,
      width: 40,
      height: 40,
    })
  }
  reader.readAsDataURL(file)
  target.value = ''
}

async function onSave(silent = false) {
  if (!silent) {
    const t = showLoadingToast({ message: '保存中…', duration: 0, forbidClick: true })
    try {
      const design = await saveDesign(editor.dump())
      editor.reset(design)
      t.close()
      showToast({ type: 'success', message: '设计已保存' })
    } catch {
      t.close()
      showToast({ type: 'fail', message: '保存失败' })
    }
  } else {
    const design = await saveDesign(editor.dump())
    editor.reset(design)
  }
}

async function onAddToCart() {
  if (!layers.value.length) {
    showDialog({ title: '提示', message: '画布是空的，先加点印花再下单吧～' })
    return
  }
  showSizePicker.value = true
}

async function confirmAddToCart() {
  if (!sizeChosen.value) {
    showToast('请选择尺码')
    return
  }
  const t = showLoadingToast({ message: '加入购物车…', duration: 0, forbidClick: true })
  try {
    await onSave(true)
    await cart.add({
      id: uid('ci_'),
      designId: editor.designId,
      productId: product.value.id,
      productName: product.value.name,
      color: color.value,
      size: sizeChosen.value,
      qty: 1,
      price: product.value.basePrice,
      previewUrl: mockupUrl.value,
      selected: true,
    })
    t.close()
    showSizePicker.value = false
    sizeChosen.value = ''
    showToast({ type: 'success', message: '已加入购物车' })
  } catch {
    t.close()
    showToast({ type: 'fail', message: '加入失败' })
  }
}

function onAiCreate() {
  router.push('/ai-create?from=editor')
}
</script>

<template>
  <div class="editor">
    <!-- 顶部栏 -->
    <header class="editor__header">
      <button class="editor__back" @click="router.back()">
        <span class="i-material-symbols:arrow-back-ios-rounded" />
      </button>
      <button class="editor__switch" @click="onSwitchProduct">
        <span>切换款式</span>
        <span class="i-material-symbols:keyboard-arrow-down-rounded" />
      </button>
      <button class="editor__save" :disabled="!layers.length" @click="onSave(false)">保存设计</button>
    </header>

    <!-- 颜色色块 -->
    <div class="editor__colors">
      <button
        v-for="c in product.colors"
        :key="c"
        class="editor__color"
        :class="{ 'editor__color--active': color === c, 'editor__color--white': c.toUpperCase() === '#FFFFFF' }"
        :style="{ background: c }"
        @click="onColorClick(c)"
      />
    </div>

    <!-- 画布 -->
    <div class="editor__stage" @click="onCanvasClick">
      <div ref="canvasRef" class="editor__canvas">
        <img class="editor__mockup" :src="mockupUrl" alt="底图" />
        <!-- 印花区域虚线框（仅前景） -->
        <div class="editor__safezone" />
        <EditorLayer
          v-for="l in sideLayers"
          :key="l.id"
          :layer="l"
          :active="l.id === activeLayerId"
          :canvas-el="canvasRef"
          @activate="onLayerActivate(l.id)"
          @update="(patch, commit) => onLayerUpdate(l.id, patch, commit)"
          @remove="onLayerRemove(l.id)"
        />
      </div>

      <!-- 右侧浮按钮 -->
      <div class="editor__floats">
        <button class="float-btn" :disabled="!activeLayerId" @click="editor.bringForward(activeLayerId)">
          <span class="i-material-symbols:flip-to-front-rounded" />
          <span>上移</span>
        </button>
        <button class="float-btn" :disabled="!activeLayerId" @click="editor.sendBackward(activeLayerId)">
          <span class="i-material-symbols:flip-to-back-rounded" />
          <span>下移</span>
        </button>
        <button class="float-btn" @click="onFlipSide">
          <span class="i-material-symbols:cached-rounded" />
          <span>{{ side === 'front' ? '背面' : '正面' }}</span>
        </button>
      </div>

      <!-- 撤销 / 重做 -->
      <div class="editor__history">
        <button class="hist-btn" :disabled="!canUndo" @click="editor.undo">
          <span class="i-material-symbols:undo-rounded" />
        </button>
        <button class="hist-btn" :disabled="!canRedo" @click="editor.redo">
          <span class="i-material-symbols:redo-rounded" />
        </button>
      </div>
    </div>

    <!-- 底部工具栏 -->
    <nav class="editor__toolbar">
      <button class="tool" @click="openPatternPicker">
        <span class="i-material-symbols:palette-outline-rounded tool__icon" />
        <span>印花素材</span>
      </button>
      <button class="tool" @click="showTextEditor = true">
        <span class="i-material-symbols:format-size-rounded tool__icon" />
        <span>文字</span>
      </button>
      <button class="tool" @click="onUploadClick">
        <span class="i-material-symbols:image-outline-rounded tool__icon" />
        <span>来图定制</span>
      </button>
      <button class="tool" @click="onAiCreate">
        <span class="i-material-symbols:auto-awesome-rounded tool__icon tool__icon--accent" />
        <span class="tool--accent">AI 创作</span>
      </button>
    </nav>

    <!-- CTA 加入购物车 -->
    <div class="editor__cta">
      <div class="editor__price">
        <span class="editor__price-label">¥</span>
        <span class="editor__price-num">{{ product.basePrice }}</span>
      </div>
      <button class="editor__buy" @click="onAddToCart">
        <span class="i-material-symbols:shopping-bag-outline-rounded" />
        加入购物车
      </button>
    </div>

    <input ref="fileInputRef" type="file" accept="image/*" hidden @change="onFileChange" />

    <!-- 印花选择浮层 -->
    <van-popup v-model:show="showPatternPicker" round position="bottom" :style="{ height: '60%' }">
      <div class="picker">
        <div class="picker__title">选择印花</div>
        <div class="picker__grid">
          <button
            v-for="p in patternList"
            :key="p.id"
            class="picker__item"
            @click="pickPattern(p)"
          >
            <img :src="p.imageUrl" />
            <span class="picker__name text-ellipsis">{{ p.title }}</span>
          </button>
        </div>
      </div>
    </van-popup>

    <!-- 文字编辑浮层 -->
    <van-popup v-model:show="showTextEditor" round position="bottom" :style="{ padding: '20px' }">
      <div class="text-editor">
        <div class="text-editor__title">添加文字</div>
        <textarea v-model="textInput" rows="3" placeholder="输入要印的文字…" />
        <div class="text-editor__colors">
          <span>颜色：</span>
          <button
            v-for="c in ['#1F2937', '#FF4D4F', '#FACC15', '#10B981', '#3B82F6', '#A855F7']"
            :key="c"
            class="text-editor__color"
            :class="{ active: textColor === c }"
            :style="{ background: c }"
            @click="textColor = c"
          />
        </div>
        <div class="text-editor__actions">
          <button class="btn-ghost" @click="showTextEditor = false">取消</button>
          <button class="btn-primary" @click="commitText">确定</button>
        </div>
      </div>
    </van-popup>

    <!-- 加购：选尺码 -->
    <van-popup v-model:show="showSizePicker" round position="bottom" :style="{ padding: '20px' }">
      <div class="size-picker">
        <div class="size-picker__title">选择尺码</div>
        <div class="size-picker__grid">
          <button
            v-for="s in product.sizes"
            :key="s"
            class="size-picker__item"
            :class="{ active: sizeChosen === s }"
            @click="sizeChosen = s"
          >
            {{ s }}
          </button>
        </div>
        <button class="btn-primary" style="width: 100%; margin-top: 16px" @click="confirmAddToCart">
          确认加入购物车
        </button>
      </div>
    </van-popup>
  </div>
</template>

<style lang="scss" scoped>
.editor {
  min-height: 100vh;
  background: #f9fafb;
  display: flex;
  flex-direction: column;
  padding-bottom: calc(#{$tabbar-height} + 60px);

  &__header {
    height: 48px;
    padding: 0 12px;
    background: rgba(255, 255, 255, 0.92);
    backdrop-filter: blur(8px);
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 10;
  }

  &__back {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: $color-bg-tag;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
  }

  &__switch {
    height: 32px;
    padding: 0 12px;
    border-radius: $radius-pill;
    background: rgba(0, 0, 0, 0.04);
    color: $color-text-primary;
    font-size: 14px;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-weight: 600;
  }

  &__save {
    height: 32px;
    padding: 0 14px;
    border-radius: $radius-pill;
    background: $color-bg-tag;
    color: $color-text-secondary;
    font-size: 13px;
    font-weight: 600;

    &:disabled {
      opacity: 0.5;
    }
  }

  &__colors {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    padding: 8px 16px 0;
    background: #f9fafb;
  }

  &__color {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    border: 1px solid rgba(0, 0, 0, 0.1);
    transition: transform 0.15s;

    &--white {
      border: 1px solid $color-border;
    }

    &--active {
      transform: scale(1.2);
      box-shadow: 0 0 0 2px #fff, 0 0 0 4px $color-primary;
    }
  }

  &__stage {
    position: relative;
    margin: 8px 16px 0;
    flex: 1;
    background: #fff;
    border-radius: 16px;
    overflow: hidden;
    min-height: 380px;
  }

  &__canvas {
    position: absolute;
    inset: 0;
  }

  &__mockup {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: contain;
    pointer-events: none;
  }

  &__safezone {
    position: absolute;
    left: 28%;
    top: 24%;
    width: 44%;
    height: 50%;
    border: 1.5px dashed rgba(255, 77, 79, 0.35);
    border-radius: 6px;
    pointer-events: none;
    z-index: 2;
  }

  &__floats {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  &__history {
    position: absolute;
    left: 12px;
    bottom: 12px;
    display: flex;
    gap: 8px;
  }

  &__toolbar {
    display: flex;
    justify-content: space-around;
    background: #fff;
    padding: 10px 0;
    margin-top: 8px;
  }

  &__cta {
    position: fixed;
    left: 50%;
    transform: translateX(-50%);
    bottom: 0;
    width: 100%;
    max-width: 480px;
    height: 60px;
    background: #fff;
    display: flex;
    align-items: center;
    padding: 0 12px calc(env(safe-area-inset-bottom) / 2);
    border-top: 1px solid $color-divider;
    z-index: 9;
  }

  &__price {
    flex: 1;
    color: $color-primary;
    font-weight: 800;
  }

  &__price-label {
    font-size: 14px;
  }

  &__price-num {
    font-size: 24px;
    margin-left: 2px;
  }

  &__buy {
    height: 40px;
    padding: 0 24px;
    background: $color-primary;
    color: #fff;
    border-radius: $radius-pill;
    font-size: 14px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }
}

.float-btn {
  width: 56px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
  padding: 8px 4px;
  font-size: 10px;
  color: $color-text-primary;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  font-weight: 500;

  span:first-child {
    font-size: 22px;
  }

  &:disabled {
    opacity: 0.4;
  }
}

.hist-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: $color-text-primary;

  &:disabled {
    opacity: 0.35;
  }
}

.tool {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: $color-text-regular;

  &__icon {
    font-size: 24px;
    color: $color-text-primary;

    &--accent {
      color: $color-primary;
    }
  }

  &--accent {
    color: $color-primary;
    font-weight: 700;
  }
}

.picker {
  padding: 16px;

  &__title {
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 12px;
    text-align: center;
  }

  &__grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    max-height: 60vh;
    overflow-y: auto;
  }

  &__item {
    background: #fafafa;
    border-radius: 8px;
    overflow: hidden;
    padding: 0;

    img {
      width: 100%;
      aspect-ratio: 1;
      object-fit: cover;
      display: block;
    }
  }

  &__name {
    display: block;
    padding: 6px 8px;
    font-size: 11px;
    text-align: left;
  }
}

.text-editor {
  display: flex;
  flex-direction: column;
  gap: 12px;

  &__title {
    font-size: 16px;
    font-weight: 700;
    text-align: center;
  }

  textarea {
    border: 1px solid $color-border;
    border-radius: 8px;
    padding: 10px 12px;
    font-size: 14px;
    width: 100%;
    resize: none;
  }

  &__colors {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    color: $color-text-secondary;
  }

  &__color {
    width: 22px;
    height: 22px;
    border-radius: 50%;
    border: 1px solid rgba(0, 0, 0, 0.05);

    &.active {
      box-shadow: 0 0 0 2px #fff, 0 0 0 4px $color-primary;
    }
  }

  &__actions {
    display: flex;
    gap: 12px;
    justify-content: flex-end;
  }
}

.size-picker {
  &__title {
    font-size: 16px;
    font-weight: 700;
    text-align: center;
    margin-bottom: 16px;
  }

  &__grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
  }

  &__item {
    height: 40px;
    border: 1px solid $color-border;
    border-radius: 8px;
    background: #fff;
    font-size: 14px;
    color: $color-text-primary;

    &.active {
      border-color: $color-primary;
      background: $color-primary-light;
      color: $color-primary;
      font-weight: 700;
    }
  }
}
</style>
