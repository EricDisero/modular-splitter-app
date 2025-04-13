import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

import './assets/css/styles.css'
import './assets/css/modern_styles.css'
import './assets/css/particles.css'
import './assets/js/particle_animation.js'  // Optional: If not yet included


const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')