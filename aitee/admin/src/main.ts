import { createApp } from 'vue'
import { createPinia } from 'pinia'
import 'element-plus/dist/index.css'
import * as ElementPlusIcons from '@element-plus/icons-vue'
import './styles/index.scss'

import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(createPinia())
app.use(router)

for (const [name, component] of Object.entries(ElementPlusIcons)) {
  app.component(name, component as never)
}

app.mount('#app')
