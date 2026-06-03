import { defineConfig } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'
import Icons from 'unplugin-icons/vite'
import fs from 'node:fs'
import path from 'node:path'

const STATIC_DIR = path.resolve(__dirname, 'src/static')

/**
 * uniapp vite 默认不把 src/static 当作 publicDir 服务给 H5 dev，
 * 但 tabBar.iconPath 编译期就被写成 `static/...`、不支持网络图，
 * 所以 dev 阶段必须把 /static/* 映射到 src/static/，否则 tabBar 图标 404。
 */
function staticDirMiddleware() {
  return {
    name: 'aitee-static-dir',
    configureServer(server: any) {
      server.middlewares.use('/static', (req: any, res: any, next: any) => {
        try {
          const url = decodeURIComponent((req.url || '/').split('?')[0])
          const file = path.join(STATIC_DIR, url)
          // 防止 path traversal
          if (!file.startsWith(STATIC_DIR)) return next()
          if (!fs.existsSync(file) || !fs.statSync(file).isFile()) return next()
          const ext = path.extname(file).toLowerCase()
          const mime: Record<string, string> = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.webp': 'image/webp',
          }
          if (mime[ext]) res.setHeader('Content-Type', mime[ext])
          res.setHeader('Cache-Control', 'public, max-age=300')
          fs.createReadStream(file).pipe(res)
        } catch {
          next()
        }
      })
    },
  }
}

export default defineConfig({
  plugins: [
    uni(),
    Icons({ autoInstall: false, compiler: 'vue3' }),
    staticDirMiddleware(),
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
        additionalData: `@use "@/styles/variables.scss" as *;`,
      },
    },
  },
  server: {
    host: true,
    port: 8206,
    strictPort: true,
    proxy: {
      // 业务 API
      '/api': {
        target: process.env.VITE_API_TARGET || 'http://localhost:8200',
        changeOrigin: true,
      },
      // 共享 UI 资源（hero/entry/patterns 图）由 backend /cdn 提供，
      // 这样小程序不再把 30MB 图打进包里
      '/cdn': {
        target: process.env.VITE_API_TARGET || 'http://localhost:8200',
        changeOrigin: true,
      },
    },
  },
})
