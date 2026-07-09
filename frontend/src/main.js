import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import './assets/styles/main.css'

const app = createApp(App)
app.use(createPinia())

// 若已有 token，尝试静默拉取用户档案
const auth = useAuthStore()
if (auth.isAuthenticated) {
  auth.fetchProfile().catch(() => auth.logout())
}

app.use(router)
app.mount('#app')
