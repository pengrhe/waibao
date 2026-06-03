import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { bootstrapSeed } from './store/bootstrap'
import 'vant/lib/index.css'
import './assets/styles/global.scss'

bootstrapSeed()

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
