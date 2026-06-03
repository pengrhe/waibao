import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { uid } from '@/utils/id'
import { products } from '@/mock/products'
import type { Design, DesignLayer, LayerSide } from '@/types'

interface Snapshot {
  productId: number
  color: string
  side: LayerSide
  layers: DesignLayer[]
}

const HISTORY_LIMIT = 30

function defaultSnapshot(): Snapshot {
  return {
    productId: products[0].id,
    color: products[0].colors[0],
    side: 'front',
    layers: [],
  }
}

export const useEditorStore = defineStore('editor', () => {
  const designId = ref<string>('')
  const productId = ref<number>(products[0].id)
  const color = ref<string>(products[0].colors[0])
  const side = ref<LayerSide>('front')
  const layers = ref<DesignLayer[]>([])
  const activeLayerId = ref<string>('')

  const undoStack = ref<Snapshot[]>([])
  const redoStack = ref<Snapshot[]>([])

  const product = computed(() => products.find((p) => p.id === productId.value) ?? products[0])
  const sideLayers = computed(() => layers.value.filter((l) => l.side === side.value))
  const activeLayer = computed(() => layers.value.find((l) => l.id === activeLayerId.value))

  function snapshot(): Snapshot {
    return {
      productId: productId.value,
      color: color.value,
      side: side.value,
      layers: JSON.parse(JSON.stringify(layers.value)),
    }
  }

  function applySnapshot(s: Snapshot) {
    productId.value = s.productId
    color.value = s.color
    side.value = s.side
    layers.value = JSON.parse(JSON.stringify(s.layers))
  }

  function pushHistory() {
    undoStack.value.push(snapshot())
    if (undoStack.value.length > HISTORY_LIMIT) undoStack.value.shift()
    redoStack.value = []
  }

  function undo() {
    if (!undoStack.value.length) return
    redoStack.value.push(snapshot())
    const s = undoStack.value.pop()!
    applySnapshot(s)
  }

  function redo() {
    if (!redoStack.value.length) return
    undoStack.value.push(snapshot())
    const s = redoStack.value.pop()!
    applySnapshot(s)
  }

  const canUndo = computed(() => undoStack.value.length > 0)
  const canRedo = computed(() => redoStack.value.length > 0)

  function reset(design?: Partial<Design>) {
    const base = defaultSnapshot()
    if (design) {
      base.productId = design.productId ?? base.productId
      base.color = design.color ?? base.color
      base.layers = (design.layers ?? []).map((l) => ({ ...l }))
    }
    designId.value = design?.id ?? uid('d_')
    applySnapshot(base)
    undoStack.value = []
    redoStack.value = []
    activeLayerId.value = ''
  }

  function setProduct(id: number) {
    const next = products.find((p) => p.id === id)
    if (!next) return
    pushHistory()
    productId.value = id
    if (!next.colors.includes(color.value)) color.value = next.colors[0]
  }

  function setColor(c: string) {
    pushHistory()
    color.value = c
  }

  function flipSide() {
    side.value = side.value === 'front' ? 'back' : 'front'
  }

  function addLayer(input: Omit<DesignLayer, 'id' | 'side' | 'rotation' | 'opacity'> & Partial<DesignLayer>) {
    pushHistory()
    const layer: DesignLayer = {
      id: uid('l_'),
      source: input.source,
      data: input.data,
      text: input.text,
      textColor: input.textColor ?? '#1F2937',
      fontSize: input.fontSize ?? 32,
      x: input.x ?? 50,
      y: input.y ?? 30,
      width: input.width ?? 30,
      height: input.height ?? 30,
      rotation: input.rotation ?? 0,
      opacity: input.opacity ?? 1,
      side: input.side ?? side.value,
    }
    layers.value.push(layer)
    activeLayerId.value = layer.id
  }

  function updateLayer(id: string, patch: Partial<DesignLayer>, withHistory = false) {
    const idx = layers.value.findIndex((l) => l.id === id)
    if (idx < 0) return
    if (withHistory) pushHistory()
    layers.value[idx] = { ...layers.value[idx], ...patch }
  }

  function removeLayer(id: string) {
    pushHistory()
    layers.value = layers.value.filter((l) => l.id !== id)
    if (activeLayerId.value === id) activeLayerId.value = ''
  }

  function setActive(id: string) {
    activeLayerId.value = id
  }

  function bringForward(id: string) {
    const idx = layers.value.findIndex((l) => l.id === id)
    if (idx < 0 || idx === layers.value.length - 1) return
    pushHistory()
    const [it] = layers.value.splice(idx, 1)
    layers.value.splice(idx + 1, 0, it)
  }

  function sendBackward(id: string) {
    const idx = layers.value.findIndex((l) => l.id === id)
    if (idx <= 0) return
    pushHistory()
    const [it] = layers.value.splice(idx, 1)
    layers.value.splice(idx - 1, 0, it)
  }

  function dump(): Design {
    const now = Date.now()
    return {
      id: designId.value || uid('d_'),
      productId: productId.value,
      color: color.value,
      layers: JSON.parse(JSON.stringify(layers.value)),
      status: 'draft',
      createdAt: now,
      updatedAt: now,
    }
  }

  reset()

  return {
    designId,
    productId,
    color,
    side,
    layers,
    activeLayerId,
    product,
    sideLayers,
    activeLayer,
    canUndo,
    canRedo,
    reset,
    setProduct,
    setColor,
    flipSide,
    undo,
    redo,
    addLayer,
    updateLayer,
    removeLayer,
    setActive,
    bringForward,
    sendBackward,
    dump,
    pushHistory,
  }
})
