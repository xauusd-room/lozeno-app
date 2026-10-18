
<template>
  <div class="mask" @click.self="emit('close')">
    <section class="modal">
      <button class="close" @click="emit('close')">×</button>
      <h2>{{ order ? '订单详情' : `购买 ${product.name}` }}</h2>
      <div class="price">{{ displayPrice }}</div>

      <template v-if="!order">
        <div class="methods">
          <button v-for="m in methods" :key="m.value" :class="{active:method===m.value}" @click="method=m.value">{{ m.label }}</button>
        </div>
        <div v-if="method==='usdt'" class="usdt-preview">
          <p>网络：TRC20</p>
          <p class="address">{{ usdtAddress }}</p>
          <button class="secondary" @click="copy(usdtAddress)">复制收款地址</button>
        </div>
        <button class="primary" :disabled="loading" @click="createOrder">{{ loading ? '正在创建订单…' : '创建订单' }}</button>
      </template>

      <template v-else>
        <div class="order-info">
          <p>订单号：<span>{{ order.order_no }}</span></p>
          <p>支付方式：<span>{{ methodLabel(order.payment_method) }}</span></p>
          <p>订单状态：<span :class="order.status">{{ statusText }}</span></p>
          <p v-if="order.status==='pending'">剩余时间：<span>{{ countdown }}</span></p>
        </div>

        <div v-if="order.status==='pending' && order.payment_method==='wechat'" class="payment-content">
          <h3>微信支付</h3>
          <img class="qr" :src="paymentConfig.wechat.qr" alt="微信收款二维码">
        </div>
        <div v-else-if="order.status==='pending' && order.payment_method==='alipay'" class="payment-content">
          <h3>支付宝</h3>
          <img class="qr" :src="paymentConfig.alipay.qr" alt="支付宝收款二维码">
        </div>
        <div v-else-if="order.status==='pending' && order.payment_method==='usdt'" class="payment-content">
          <h3>USDT TRC20</h3>
          <p class="amount">{{ order.amount }} USDT</p>
          <p class="address">{{ order.payment?.address || usdtAddress }}</p>
          <button class="secondary" @click="copy(order.payment?.address || usdtAddress)">复制收款地址</button>
        </div>

        <div v-if="order.status==='paid'" class="success">
          <h3>付款已确认</h3>
          <button class="primary" @click="getLicense">获取授权</button>
          <pre v-if="license">{{ license }}</pre>
        </div>
        <button v-if="order.status==='pending'" class="secondary refresh" :disabled="loading" @click="checkOrder">查询订单状态</button>
        <button class="secondary refresh" @click="emit('close')">关闭</button>
      </template>

      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="notice" class="notice">{{ notice }}</p>
    </section>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref } from 'vue'
import paymentConfig from '../data/paymentConfig.js'

const props = defineProps({ product: { type: Object, required: true } })
const emit = defineEmits(['close', 'created'])
const API = 'https://lozeno-api.aaa375750526.workers.dev'
const USDT_ADDRESS = 'TLuLF3VibWGjdVWpue9huxbgvkx2YWgzky'
const USDT_TO_CNY_RATE = 7
const methods = [
  { value: 'wechat', label: '微信支付' },
  { value: 'alipay', label: '支付宝' },
  { value: 'usdt', label: 'USDT TRC20' }
]
const method = ref('wechat')
const order = ref(null)
const loading = ref(false)
const error = ref('')
const notice = ref('')
const license = ref('')
const countdown = ref('24:00:00')
let pollTimer = null
let countdownTimer = null
let expiresAt = 0

const usdtAddress = paymentConfig.usdt?.address || USDT_ADDRESS
const displayPrice = computed(() => {
  const currentMethod = order.value?.payment_method || method.value
  return currentMethod === 'usdt'
    ? `${Number(props.product.price).toFixed(2)} USDT`
    : `¥${(Number(props.product.price) * USDT_TO_CNY_RATE).toFixed(2)}`
})
const statusText = computed(() => ({
  pending: '等待复核',
  paid: '已确认付款',
  cancelled: '已取消',
  expired: '已过期'
}[order.value?.status] || order.value?.status || '未知'))

function methodLabel(value) {
  return methods.find(m => m.value === value)?.label || value
}

async function request(path, options = {}) {
  const response = await fetch(`${API}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) }
  })
  const data = await response.json().catch(() => ({}))
  if (!response.ok || data.error) throw new Error(data.error || data.detail || '请求失败，请稍后重试')
  return data
}

async function createOrder() {
  loading.value = true
  error.value = ''
  notice.value = ''
  try {
    const data = await request('/api/orders', {
      method: 'POST',
      body: JSON.stringify({
        product_id: props.product.id,
        product_name: props.product.name,
        payment_method: method.value
      })
    })
    order.value = data.order || data
    emit('created', order.value)
    startTimers()
  } catch (e) {
    error.value = e.message || '创建订单失败'
  } finally {
    loading.value = false
  }
}

async function checkOrder() {
  if (!order.value?.order_no) return
  loading.value = true
  error.value = ''
  try {
    const data = await request(`/api/orders/${encodeURIComponent(order.value.order_no)}`)
    order.value = data.order || data
    if (order.value.status !== 'pending') stopTimers()
    if (order.value.status === 'paid') notice.value = '付款已由管理员确认。'
  } catch (e) {
    error.value = e.message || '查询订单失败'
  } finally {
    loading.value = false
  }
}

function startTimers() {
  stopTimers()
  const expiry = order.value?.expires_at ? new Date(order.value.expires_at).getTime() : Date.now() + 24 * 60 * 60 * 1000
  expiresAt = expiry
  updateCountdown()
  countdownTimer = setInterval(updateCountdown, 1000)
  pollTimer = setInterval(checkOrder, 10000)
}

function updateCountdown() {
  const seconds = Math.max(0, Math.floor((expiresAt - Date.now()) / 1000))
  const h = String(Math.floor(seconds / 3600)).padStart(2, '0')
  const m = String(Math.floor(seconds % 3600 / 60)).padStart(2, '0')
  const s = String(seconds % 60).padStart(2, '0')
  countdown.value = `${h}:${m}:${s}`
  if (!seconds) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
}

function stopTimers() {
  if (pollTimer) clearInterval(pollTimer)
  if (countdownTimer) clearInterval(countdownTimer)
  pollTimer = null
  countdownTimer = null
}

async function getLicense() {
  if (!order.value?.order_no) return
  loading.value = true
  error.value = ''
  try {
    const data = await request(`/api/orders/${encodeURIComponent(order.value.order_no)}/license`)
    license.value = typeof data === 'string' ? data : JSON.stringify(data, null, 2)
  } catch (e) {
    error.value = e.message || '获取授权失败'
  } finally {
    loading.value = false
  }
}

async function copy(value) {
  try {
    await navigator.clipboard.writeText(value)
    notice.value = '已复制'
  } catch {
    notice.value = `请手动复制：${value}`
  }
}

onBeforeUnmount(stopTimers)
</script>

<style scoped>
.mask{position:fixed;inset:0;z-index:1000;display:flex;align-items:center;justify-content:center;padding:20px;background:#000b;backdrop-filter:blur(5px)}.modal{position:relative;width:100%;max-width:440px;max-height:90vh;overflow:auto;padding:30px;background:#141722;border:1px solid #222630;border-radius:14px;color:#eef1f8;box-shadow:0 20px 70px #0008}.close{position:absolute;right:16px;top:12px;border:0;background:none;color:#848e9c;font-size:28px;cursor:pointer}.modal h2{margin:0 25px 14px 0;font-size:20px}.price{margin:10px 0 22px;color:#fff;font-size:28px;font-weight:700}.methods{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin-bottom:18px}.methods button,.secondary{padding:10px 8px;border:1px solid #303544;border-radius:7px;background:#1b1e26;color:#c7ccda;cursor:pointer}.methods button.active{border-color:#315bff;color:#fff;background:#202b4d}.primary{width:100%;padding:12px;border:0;border-radius:7px;background:#315bff;color:#fff;font-size:15px;font-weight:600;cursor:pointer}.primary:hover{background:#4169ff}.primary:disabled,.secondary:disabled{opacity:.6;cursor:not-allowed}.usdt-preview,.order-info{margin:16px 0;padding:14px;background:#1b1e26;border-radius:8px}.usdt-preview p,.order-info p{margin:7px 0;font-size:13px;color:#aab2c2;overflow-wrap:anywhere}.order-info span{color:#eef1f8}.pending{color:#f0b94b!important}.paid{color:#43d49a!important}.cancelled,.expired{color:#f07878!important}.payment-content{display:flex;flex-direction:column;align-items:center;gap:12px;margin:18px 0}.payment-content h3,.success h3{margin:0;font-size:16px}.qr{display:block;width:220px;height:220px;max-width:100%;object-fit:contain;background:#fff;border-radius:6px}.address{max-width:100%;overflow-wrap:anywhere;color:#aeb8cb;font-size:12px;line-height:1.6}.amount{font-size:20px;font-weight:700;color:#fff}.secondary{width:100%;margin-top:8px}.refresh{margin-top:12px}.error{margin-top:14px;color:#ff7777;font-size:13px;overflow-wrap:anywhere}.notice{margin-top:12px;color:#8eafff;font-size:13px;overflow-wrap:anywhere}.success{margin:18px 0}.success .primary{margin-top:12px}pre{white-space:pre-wrap;overflow-wrap:anywhere;padding:12px;background:#1b1e26;border-radius:7px;font-size:12px}@media(max-width:480px){.modal{padding:24px 18px}.qr{width:200px;height:200px}}
</style>
