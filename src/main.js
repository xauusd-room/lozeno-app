import { createApp } from 'vue'
import './assets/css/tokens.css'
import App from './App.vue'
import router from './router'
import { loadEaProductPrices } from './data/eaProducts'

const app = createApp(App)

app.use(router)
app.mount('#app')

loadEaProductPrices()
