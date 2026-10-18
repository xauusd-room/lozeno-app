
<template>
  <main class="page page-container">
    <ProductHero :product="product" @purchase="handlePurchase" />
    <ProductPerformance :product="product" />
    <ProductStrategy :product="product" />

    <AuthModal
      v-if="showAuth"
      initial-mode="login"
      @close="showAuth = false"
      @authenticated="onAuthenticated"
    />

    <PurchaseModal
      v-if="showPurchase"
      :product="product"
      @close="showPurchase = false"
      @created="orderCreated"
    />
  </main>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { eaProducts } from '../data/eaProducts.js'
import { getCurrentUser } from '../services/auth'
import ProductHero from '../components/ProductHero.vue'
import ProductPerformance from '../components/ProductPerformance.vue'
import ProductStrategy from '../components/ProductStrategy.vue'
import AuthModal from '../components/AuthModal.vue'
import PurchaseModal from '../components/PurchaseModal.vue'

const route = useRoute()
const showAuth = ref(false)
const showPurchase = ref(false)
const checkingAuth = ref(false)

const product = computed(
  () => eaProducts[route.query.id || '1'] || eaProducts[1]
)

document.title = `${product.value.name} | LOZENO`

async function handlePurchase() {
  if (checkingAuth.value) return

  checkingAuth.value = true

  try {
    const user = await getCurrentUser()

    if (user) {
      showPurchase.value = true
    } else {
      showAuth.value = true
    }
  } catch {
    showAuth.value = true
  } finally {
    checkingAuth.value = false
  }
}

function onAuthenticated(user) {
  if (!user) return

  showAuth.value = false
  showPurchase.value = true
}

function orderCreated(order) {
  // 订单创建成功后保留购买弹窗，
  // 由 PurchaseModal 显示订单号和支付界面。
  console.log('订单创建成功:', order)
}
</script>

<style scoped>
.page{min-width:0;padding-top:34px;padding-bottom:72px}
@media(max-width:680px){.page{padding-top:24px;padding-bottom:48px}}
</style>
