
import { createRouter, createWebHistory } from 'vue-router'

import Home from '../views/Home.vue'
import Market from '../views/Market.vue'
import Ranking from '../views/Ranking.vue'
import ProductDetail from '../views/ProductDetail.vue'

import Profile from '../views/Profile.vue'
import Orders from '../views/Orders.vue'
import Licenses from '../views/Licenses.vue'
import LiveTrading from '../views/LiveTrading.vue'
import Stocks from '../views/Stocks.vue'
export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Home },
    { path: '/market', component: Market },
    { path: '/ranking', component: Ranking },
    { path: '/stocks', component: Stocks },
    { path: '/product', component: ProductDetail },

    { path: '/profile', component: Profile },
    { path: '/orders', component: Orders },
    { path: '/licenses', component: Licenses },
    { path: '/live', component: LiveTrading },
  ]
})
