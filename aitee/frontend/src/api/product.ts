import { products } from '@/mock/products'
import { mockCall } from './request'
import type { Product } from '@/types'

export async function fetchProducts(): Promise<Product[]> {
  return mockCall(() => products)
}

export async function fetchProductById(id: number): Promise<Product | undefined> {
  return mockCall(() => products.find((p) => p.id === id))
}
