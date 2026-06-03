import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import {
  addToCart as apiAdd,
  clearCart as apiClear,
  listCart,
  removeCartItem,
  updateCartItem,
} from '@/api/cart'
import type { CartItem } from '@/types'

export const useCartStore = defineStore('cart', () => {
  const items = ref<CartItem[]>([])
  const loading = ref(false)

  const totalCount = computed(() => items.value.reduce((s, i) => s + i.qty, 0))
  const selectedItems = computed(() => items.value.filter((i) => i.selected))
  const selectedAmount = computed(() =>
    selectedItems.value.reduce((s, i) => s + i.price * i.qty, 0),
  )

  async function reload() {
    loading.value = true
    try {
      items.value = await listCart()
    } finally {
      loading.value = false
    }
  }

  async function add(item: CartItem) {
    items.value = await apiAdd(item)
  }

  async function setQty(id: string, qty: number) {
    if (qty <= 0) {
      items.value = await removeCartItem([id])
    } else {
      items.value = await updateCartItem(id, { qty })
    }
  }

  async function toggleSelected(id: string) {
    const it = items.value.find((i) => i.id === id)
    if (!it) return
    items.value = await updateCartItem(id, { selected: !it.selected })
  }

  async function selectAll(value: boolean) {
    await Promise.all(items.value.map((i) => updateCartItem(i.id, { selected: value })))
    items.value = items.value.map((i) => ({ ...i, selected: value }))
  }

  async function remove(ids: string[]) {
    items.value = await removeCartItem(ids)
  }

  async function clear() {
    await apiClear()
    items.value = []
  }

  return {
    items,
    loading,
    totalCount,
    selectedItems,
    selectedAmount,
    reload,
    add,
    setQty,
    toggleSelected,
    selectAll,
    remove,
    clear,
  }
})
