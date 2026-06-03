<script setup lang="ts">
import { computed, ref } from 'vue'
import type { DesignLayer } from '@/types'

interface Props {
  layer: DesignLayer
  active: boolean
  canvasEl: HTMLElement | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  activate: []
  update: [patch: Partial<DesignLayer>, commit?: boolean]
  remove: []
}>()

type DragMode = 'move' | 'scale' | 'rotate' | null

const dragMode = ref<DragMode>(null)

interface DragState {
  startX: number
  startY: number
  startW: number
  startH: number
  startRot: number
  pointerX: number
  pointerY: number
  centerX: number
  centerY: number
  distance: number
  angle: number
}

let dragState: DragState | null = null

function getCanvasRect(): DOMRect | null {
  return props.canvasEl?.getBoundingClientRect() ?? null
}

function clientToPercent(cx: number, cy: number): { x: number; y: number } {
  const rect = getCanvasRect()
  if (!rect) return { x: 0, y: 0 }
  return {
    x: ((cx - rect.left) / rect.width) * 100,
    y: ((cy - rect.top) / rect.height) * 100,
  }
}

function startDrag(mode: DragMode, e: PointerEvent) {
  if (!mode) return
  e.stopPropagation()
  e.preventDefault()
  emit('activate')
  dragMode.value = mode
  const { x, y } = clientToPercent(e.clientX, e.clientY)
  const rect = getCanvasRect()
  const cxPct = props.layer.x + props.layer.width / 2
  const cyPct = props.layer.y + props.layer.height / 2
  const cxPx = rect ? rect.left + (cxPct / 100) * rect.width : 0
  const cyPx = rect ? rect.top + (cyPct / 100) * rect.height : 0
  const dx = e.clientX - cxPx
  const dy = e.clientY - cyPx
  dragState = {
    startX: props.layer.x,
    startY: props.layer.y,
    startW: props.layer.width,
    startH: props.layer.height,
    startRot: props.layer.rotation,
    pointerX: x,
    pointerY: y,
    centerX: cxPct,
    centerY: cyPct,
    distance: Math.sqrt(dx * dx + dy * dy),
    angle: (Math.atan2(dy, dx) * 180) / Math.PI,
  }
  window.addEventListener('pointermove', onMove)
  window.addEventListener('pointerup', onUp, { once: true })
  window.addEventListener('pointercancel', onUp, { once: true })
}

function onMove(e: PointerEvent) {
  if (!dragMode.value || !dragState) return
  const { x, y } = clientToPercent(e.clientX, e.clientY)
  const dx = x - dragState.pointerX
  const dy = y - dragState.pointerY

  if (dragMode.value === 'move') {
    const nx = clamp(dragState.startX + dx, -dragState.startW + 5, 100 - 5)
    const ny = clamp(dragState.startY + dy, -dragState.startH + 5, 100 - 5)
    emit('update', { x: nx, y: ny }, false)
  } else if (dragMode.value === 'scale') {
    const rect = getCanvasRect()
    if (!rect) return
    const cxPx = rect.left + (dragState.centerX / 100) * rect.width
    const cyPx = rect.top + (dragState.centerY / 100) * rect.height
    const dxPx = e.clientX - cxPx
    const dyPx = e.clientY - cyPx
    const dist = Math.sqrt(dxPx * dxPx + dyPx * dyPx)
    const ratio = dist / Math.max(1, dragState.distance)
    const nw = clamp(dragState.startW * ratio, 8, 90)
    const nh = clamp(dragState.startH * ratio, 8, 90)
    const nx = dragState.centerX - nw / 2
    const ny = dragState.centerY - nh / 2
    emit('update', { width: nw, height: nh, x: nx, y: ny }, false)
  } else if (dragMode.value === 'rotate') {
    const rect = getCanvasRect()
    if (!rect) return
    const cxPx = rect.left + (dragState.centerX / 100) * rect.width
    const cyPx = rect.top + (dragState.centerY / 100) * rect.height
    const dxPx = e.clientX - cxPx
    const dyPx = e.clientY - cyPx
    const ang = (Math.atan2(dyPx, dxPx) * 180) / Math.PI
    const next = dragState.startRot + (ang - dragState.angle)
    emit('update', { rotation: ((next % 360) + 360) % 360 }, false)
  }
}

function onUp() {
  if (dragMode.value) {
    emit('update', {}, true)
  }
  dragMode.value = null
  dragState = null
  window.removeEventListener('pointermove', onMove)
}

function clamp(v: number, min: number, max: number) {
  return Math.min(max, Math.max(min, v))
}

const layerStyle = computed(() => {
  const l = props.layer
  return {
    left: `${l.x}%`,
    top: `${l.y}%`,
    width: `${l.width}%`,
    aspectRatio: '1 / 1',
    transform: `rotate(${l.rotation}deg)`,
    opacity: l.opacity,
  }
})

function onLayerPointerDown(e: PointerEvent) {
  startDrag('move', e)
}

function onRemove(e: Event) {
  e.stopPropagation()
  emit('remove')
}
</script>

<template>
  <div
    class="layer"
    :class="{ 'layer--active': active }"
    :style="layerStyle"
    @pointerdown="onLayerPointerDown"
  >
    <template v-if="layer.source === 'text'">
      <span
        class="layer__text"
        :style="{ color: layer.textColor, fontSize: `${layer.fontSize ?? 28}px` }"
      >{{ layer.text }}</span>
    </template>
    <template v-else>
      <img class="layer__img" :src="layer.data" :alt="layer.text || 'layer'" draggable="false" />
    </template>

    <template v-if="active">
      <span class="layer__handle layer__handle--tl" @pointerdown.stop="onRemove" @click="onRemove">
        <span class="i-material-symbols:close-rounded" />
      </span>
      <span
        class="layer__handle layer__handle--tr"
        @pointerdown.stop="(e) => startDrag('rotate', e)"
      >
        <span class="i-material-symbols:rotate-right-rounded" />
      </span>
      <span
        class="layer__handle layer__handle--br"
        @pointerdown.stop="(e) => startDrag('scale', e)"
      >
        <span class="i-material-symbols:open-in-full-rounded" />
      </span>
    </template>
  </div>
</template>

<style lang="scss" scoped>
.layer {
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
  user-select: none;
  touch-action: none;
  cursor: grab;
  &:active {
    cursor: grabbing;
  }

  &--active {
    outline: 1.5px dashed $color-primary;
    outline-offset: 2px;
    z-index: 5;
  }

  &__img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    pointer-events: none;
  }

  &__text {
    font-weight: 800;
    line-height: 1;
    text-align: center;
    white-space: nowrap;
    pointer-events: none;
  }

  &__handle {
    position: absolute;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: $color-primary;
    color: #fff;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
    cursor: pointer;
    touch-action: none;

    &--tl {
      top: -12px;
      left: -12px;
      background: #1f2937;
    }

    &--tr {
      top: -12px;
      right: -12px;
      background: #3b82f6;
    }

    &--br {
      bottom: -12px;
      right: -12px;
      background: #10b981;
    }
  }
}
</style>
