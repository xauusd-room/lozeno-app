
import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Market from '../views/Market.vue'
import Ranking from '../views/Ranking.vue'
import ProductDetail from '../views/ProductDetail.vue'
import Account from '../views/Account.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Home },
    { path: '/market', component: Market },
    { path: '/ranking', component: Ranking },
    { path: '/product', component: ProductDetail },
    { path: '/account', component: Account }
  ]
})
