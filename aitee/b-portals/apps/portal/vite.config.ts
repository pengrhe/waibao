import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'node:path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: { '@': path.resolve(__dirname, 'src') },
  },
  server: {
    port: 8203,
    strictPort: true,
    host: '0.0.0.0',
    proxy: {
      '/api': { target: 'http://127.0.0.1:8200', changeOrigin: true },
      '/static': { target: 'http://127.0.0.1:8200', changeOrigin: true },
    },
  },
})
