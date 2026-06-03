import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import Components from 'unplugin-vue-components/vite'
import { VantResolver } from 'unplugin-vue-components/resolvers'
import Icons from 'unplugin-icons/vite'
import IconsResolver from 'unplugin-icons/resolver'
import path from 'node:path'
import pxToViewport from 'postcss-px-to-viewport-8-plugin'

export default defineConfig({
  plugins: [
    vue(),
    Components({
      resolvers: [
        VantResolver(),
        IconsResolver({ prefix: 'icon' }),
      ],
      dts: 'src/components.d.ts',
    }),
    Icons({ autoInstall: false, compiler: 'vue3' }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  css: {
    preprocessorOptions: {
      scss: {
        api: 'modern-compiler',
        additionalData: `@use "@/assets/styles/variables.scss" as *;`,
      },
    },
    postcss: {
      plugins: [
        pxToViewport({
          unitToConvert: 'px',
          viewportWidth: 375,
          unitPrecision: 5,
          propList: ['*'],
          viewportUnit: 'vw',
          fontViewportUnit: 'vw',
          selectorBlackList: ['.no-vw'],
          minPixelValue: 1,
          mediaQuery: false,
          replace: true,
          exclude: [/node_modules\/vant/i],
        }),
      ],
    },
  },
  server: {
    host: true,
    port: 8201,
    strictPort: true,
    proxy: {
      '/api': {
        target: process.env.VITE_API_TARGET || 'http://localhost:8200',
        changeOrigin: true,
      },
    },
  },
})
