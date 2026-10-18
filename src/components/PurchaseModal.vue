
<template>
  <div class="modal-mask">
    <section class="purchase-modal">
      <button class="close-btn" @click="$emit('close')">×</button>

      <div class="modal-head">
        <div class="modal-icon">
          <img :src="`/images/ea/${product.id}.png`" :alt="product.name">
        </div>
        <div>
          <h2>购买 {{ product.name }}</h2>
          <p>{{ product.subtitle }}</p>
        </div>
      </div>

      <div class="price-row">
        <span>应付金额</span>
        <strong>{{ displayAmount }}</strong>
      </div>

      <div class="info-list">
        <div><span>授权方式</span><b>{{ product.license }}</b></div>
        <div><span>支持平台</span><b>{{ product.platform }}</b></div>
        <div><span>适用市场</span><b>{{ product.market }}</b></div>
      </div>

      <div v-if="!order" class="create-area">
        <div class="methods">
          <button
            v-for="(item, key) in paymentMethods"
            :key="key"
            class="method"
            :class="{ active: method === key }"
            @click="method = key"
          >
            <span>{{ item.icon }}</span>
            <strong>{{ item.name }}</strong>
          </button>
        </div>

        <div v-if="error" class="error">{{ error }}</div>

        <button class="pay-btn" :disabled="loading" @click="createOrder">
          {{ loading ? '正在创建订单...' : '立即支付' }}
        </button>
      </div>

      <div v-else class="payment-area">
        <div class="order-bar">
          <div>
            <span>订单号</span>
            <b>{{ order.order_no }}</b>
          </div>
          <div>
            <span>状态</span>
            <b :class="order.status">{{ statusText }}</b>
          </div>
        </div>

        <div v-if="order.status === 'pending'" class="countdown-row">
          <span>支付剩余时间</span>
          <strong :class="{ warning: remainingSeconds <= 60 }">
            {{ countdownText }}
          </strong>
        </div>

        <div class="payment-content">
          <template
            v-if="
              order.status !== 'paid' &&
              order.status !== 'expired' &&
              order.status !== 'cancelled' &&
              order.payment_method !== 'usdt'
            "
          >
            <p class="payment-title">
              请使用{{ paymentMethods[order.payment_method]?.name || order.payment_method }}扫码支付
            </p>
            <div class="qr-box">
              <img
                :src="paymentMethods[order.payment_method]?.qr"
                :alt="paymentMethods[order.payment_method]?.name || '支付二维码'"
              >
            </div>
          </template>

          <template
            v-else-if="
              order.status === 'pending' &&
              order.payment_method === 'usdt'
            "
          >
            <p class="payment-title">USDT 支付</p>

            <div class="network-row">
              <span>支付网络</span>
              <strong>TRC20</strong>
            </div>

            <div class="address-box">
              <span>{{ paymentConfig.usdt.address }}</span>
              <button @click="copyAddress">复制</button>
            </div>

            <p class="payment-tip warning">
              请务必使用 TRC20 网络转账，其他网络转账可能导致资产无法找回。
            </p>
          </template>

          <template v-else-if="order.status === 'expired'">
            <div class="expired-box">
              <strong>订单已过期</strong>
              <span>本订单支付时间已结束，请重新创建订单。</span>
            </div>
          </template>

          <template v-else-if="order.status === 'paid'">
            <div v-if="license" class="license-box">
              <div class="success-icon">✓</div>
              <strong>支付成功</strong>
              <span>EA 授权已自动生成</span>

              <div class="license-status">
                <span>授权状态</span>
                <b>已激活</b>
              </div>

              <div class="license-key">
                <div>
                  <span>EA 授权码</span>
                  <strong>{{ license.license_key }}</strong>
                </div>
                <button @click="copyLicense">复制</button>
              </div>

              <div class="license-info">
                <div>
                  <span>产品</span>
                  <b>{{ license.product_name }}</b>
                </div>
                <div>
                  <span>授权方式</span>
                  <b>单账户授权</b>
                </div>
                <div>
                  <span>支持平台</span>
                  <b>{{ product.platform }}</b>
                </div>
              </div>

              <p class="payment-tip">
                请保存授权码，安装 EA 后使用该授权码激活。
              </p>
            </div>

            <div v-else class="success-box">
              <strong>支付已确认</strong>
              <span>正在获取 EA 授权码...</span>
            </div>
          </template>

          <template v-else>
            <div class="expired-box">
              <strong>订单已取消</strong>
              <span>该订单无法继续支付。</span>
            </div>
          </template>
        </div>

        <div v-if="order.status !== 'paid'" class="status-row">
          <span class="status-dot" :class="order.status"></span>
          <span>{{ statusText }}</span>
        </div>

        <button
          v-if="order.status === 'pending'"
          class="check-btn"
          :disabled="checking"
          @click="checkPayment"
        >
          {{ checking ? '正在查询...' : '我已完成支付' }}
        </button>

        <button
          v-if="order.status === 'expired' || order.status === 'cancelled'"
          class="check-btn"
          @click="resetOrder"
        >
          重新创建订单
        </button>

        <button
          v-if="order.status === 'paid' && license"
          class="check-btn"
          @click="$emit('close')"
        >
          完成
        </button>

        <p v-if="error" class="error">{{ error }}</p>
        <p v-if="notice" class="notice">{{ notice }}</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, ref, onBeforeUnmount } from 'vue'
import { paymentConfig } from '../data/paymentConfig'
import { getToken } from '../services/auth'

const props = defineProps({
  product: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'created'])

const API = 'https://lozeno-api.aaa375750526.workers.dev'
const EXCHANGE_RATE = 7
const ORDER_DURATION = 24 * 60 * 60 * 1000

const loading = ref(false)
const checking = ref(false)
const error = ref('')
const notice = ref('')
const order = ref(null)
const license = ref(null)
const method = ref('wechat')
const remainingSeconds = ref(0)

const paymentMethods = paymentConfig

let timer = null
let noticeTimer = null

const displayAmount = computed(() => {
  const price = Number(
    String(props.product.price).replace(/[^0-9.]/g, '')
  )

  return `¥${(price * EXCHANGE_RATE).toFixed(2)}`
})

const statusText = computed(() => {
  if (order.value?.status === 'paid') return '支付成功'
  if (order.value?.status === 'cancelled') return '订单已取消'
  if (order.value?.status === 'expired') return '订单已过期'
  return '等待支付'
})

const countdownText = computed(() => {
  const hours = Math.floor(remainingSeconds.value / 3600)
    .toString()
    .padStart(2, '0')

  const minutes = Math.floor((remainingSeconds.value % 3600) / 60)
    .toString()
    .padStart(2, '0')

  const seconds = (remainingSeconds.value % 60)
    .toString()
    .padStart(2, '0')

  return `${hours}:${minutes}:${seconds}`
})

function authHeaders(json = false) {
  const token = getToken()

  if (!token) {
    throw new Error('请先登录后再购买 EA')
  }

  return {
    Accept: 'application/json',
    ...(json ? { 'Content-Type': 'application/json' } : {}),
    Authorization: `Bearer ${token}`
  }
}

async function apiRequest(path, options = {}) {
  const headers = authHeaders(Boolean(options.body))

  const res = await fetch(`${API}${path}`, {
    ...options,
    headers: {
      ...headers,
      ...(options.headers || {})
    }
  })

  const data = await res.json().catch(() => ({}))

  if (res.status === 401) {
    throw new Error('登录状态已失效，请重新登录后再操作')
  }

  if (!res.ok) {
    const detail =
      typeof data.detail === 'string'
        ? data.detail
        : typeof data.message === 'string'
          ? data.message
          : `请求失败（HTTP ${res.status}）`

    throw new Error(detail)
  }

  return data
}

function stopCountdown() {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

function startCountdown(expiresAt) {
  stopCountdown()

  const parsedTime = expiresAt
    ? new Date(expiresAt).getTime()
    : NaN

  const endTime = Number.isFinite(parsedTime)
    ? parsedTime
    : Date.now() + ORDER_DURATION

  function update() {
    remainingSeconds.value = Math.max(
      0,
      Math.ceil((endTime - Date.now()) / 1000)
    )

    // 倒计时结束只停止计时，不自动查询或修改订单状态。
    if (remainingSeconds.value <= 0) {
      stopCountdown()
    }
  }

  update()

  if (remainingSeconds.value > 0) {
    timer = setInterval(update, 1000)
  }
}

function showNotice(message) {
  notice.value = message

  if (noticeTimer) {
    clearTimeout(noticeTimer)
  }

  noticeTimer = setTimeout(() => {
    notice.value = ''
    noticeTimer = null
  }, 2500)
}

async function createOrder() {
  if (loading.value) return

  loading.value = true
  error.value = ''
  notice.value = ''
  license.value = null

  try {
    const data = await apiRequest('/api/orders', {
      method: 'POST',
      body: JSON.stringify({
        product_id: Number(props.product.id),
        product_name: props.product.name,
        amount: Number(
          String(props.product.price).replace(/[^0-9.]/g, '')
        ),
        currency: 'USD',
        payment_method: method.value
      })
    })

    const createdOrder = data.order || data

    if (!createdOrder.order_no) {
      throw new Error('服务器未返回有效订单号，请稍后重试')
    }

    order.value = createdOrder

    startCountdown(
      order.value.expires_at ||
      new Date(Date.now() + ORDER_DURATION).toISOString()
    )

    emit('created', order.value)

    // 订单创建后不启动轮询。
    // 只有用户主动点击“我已完成支付”才查询状态。
    if (order.value.status === 'paid') {
      stopCountdown()
      await getLicense()
    }
  } catch (e) {
    error.value = e.message || '订单创建失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

async function fetchOrderStatus() {
  if (
    !order.value?.order_no ||
    checking.value ||
    order.value.status === 'paid' ||
    order.value.status === 'expired' ||
    order.value.status === 'cancelled'
  ) {
    return
  }

  checking.value = true
  error.value = ''
  notice.value = ''

  try {
    const data = await apiRequest(
      `/api/orders/${encodeURIComponent(order.value.order_no)}`
    )

    const updatedOrder = data.order || data

    if (updatedOrder.order_no) {
      order.value = updatedOrder
    }

    if (order.value.status === 'paid') {
      stopCountdown()
      await getLicense()
      return
    }

    if (
      order.value.status === 'expired' ||
      order.value.status === 'cancelled'
    ) {
      stopCountdown()

      error.value = order.value.status === 'expired'
        ? '订单已过期，请重新创建订单'
        : '订单已取消，无法继续支付'

      return
    }

    showNotice('暂未查询到支付成功记录，请确认付款后重试')
  } catch (e) {
    error.value = e.message || '暂时无法查询订单状态，请稍后重试'
  } finally {
    checking.value = false
  }
}

async function checkPayment() {
  if (
    !order.value?.order_no ||
    checking.value ||
    order.value.status !== 'pending'
  ) {
    return
  }

  await fetchOrderStatus()
}

async function getLicense() {
  if (!order.value?.order_no) return

  try {
    const data = await apiRequest(
      `/api/orders/${encodeURIComponent(order.value.order_no)}/license`
    )

    license.value = data.license || data

    if (!license.value?.license_key) {
      license.value = null
      throw new Error('服务器暂未返回有效授权码，请稍后重试')
    }

    error.value = ''
  } catch (e) {
    license.value = null
    error.value = e.message || '授权码获取失败，请稍后重试'
  }
}

function resetOrder() {
  stopCountdown()

  order.value = null
  license.value = null
  remainingSeconds.value = 0
  error.value = ''
  notice.value = ''
}

async function copyAddress() {
  try {
    await navigator.clipboard.writeText(paymentConfig.usdt.address)
    showNotice('USDT-TRC20 收款地址已复制')
  } catch {
    error.value = '复制失败，请手动复制收款地址。'
  }
}

async function copyLicense() {
  if (!license.value?.license_key) return

  try {
    await navigator.clipboard.writeText(license.value.license_key)
    showNotice('EA 授权码已复制')
  } catch {
    error.value = '复制失败，请手动复制授权码。'
  }
}

onBeforeUnmount(() => {
  stopCountdown()

  if (noticeTimer) {
    clearTimeout(noticeTimer)
    noticeTimer = null
  }
})
</script>

<style scoped>
.modal-mask{position:fixed;inset:0;z-index:1000;display:flex;align-items:center;justify-content:center;padding:20px;background:rgba(0,0,0,.72);backdrop-filter:blur(8px)}
.purchase-modal{position:relative;width:min(500px,100%);max-height:90vh;overflow:auto;padding:28px;background:var(--表面卡片背景色,#141722);border:1px solid var(--边框线条颜色,#222630);border-radius:16px;box-shadow:0 24px 80px rgba(0,0,0,.5)}
.close-btn{position:absolute;top:14px;right:16px;width:32px;height:32px;border:0;background:transparent;color:var(--次要灰色文字,#848e9c);font-size:26px;line-height:1;cursor:pointer}
.close-btn:hover{color:#fff}
.modal-head{display:flex;gap:16px;align-items:center;padding-right:30px}
.modal-icon{width:68px;height:68px;flex-shrink:0;overflow:hidden;border-radius:12px;background:#1b1e26}
.modal-icon img{width:100%;height:100%;object-fit:cover;display:block}
.modal-head h2{font-size:20px;font-weight:800;color:var(--主要文字颜色,#fff)}
.modal-head p{margin-top:5px;font-size:12px;line-height:1.5;color:var(--次要灰色文字,#848e9c)}
.price-row{display:flex;align-items:center;justify-content:space-between;margin-top:26px;padding-bottom:18px;border-bottom:1px solid var(--边框线条颜色,#222630)}
.price-row span{font-size:13px;color:var(--次要灰色文字,#848e9c)}
.price-row strong{font-size:28px;font-weight:800;color:#f0c040}
.info-list{display:flex;flex-direction:column;gap:14px;padding:20px 0}
.info-list div{display:flex;justify-content:space-between;gap:16px;font-size:13px}
.info-list span{color:var(--次要灰色文字,#848e9c)}
.info-list b{font-weight:600;color:var(--主要文字颜色,#fff);text-align:right}
.methods{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:16px 0}
.method{height:52px;border:1px solid #2b3140;border-radius:9px;background:#11141b;color:#848e9c;cursor:pointer}
.method span{display:block;font-size:11px;margin-bottom:3px}
.method strong{font-size:12px}
.method.active{border-color:var(--主色调蓝色,#315bff);background:rgba(49,91,255,.1);color:#fff}
.order-bar{display:flex;justify-content:space-between;gap:16px;margin-top:4px;padding:12px 14px;background:var(--输入框背景色,#1b1e26);border-radius:8px}
.order-bar div{display:flex;flex-direction:column;gap:4px;min-width:0}
.order-bar span{font-size:10px;color:var(--次要灰色文字,#848e9c)}
.order-bar b{font-size:11px;color:#fff;overflow-wrap:anywhere}
.order-bar b.pending{color:#eab308}
.order-bar b.paid{color:#0ecb81}
.order-bar b.cancelled,.order-bar b.expired{color:#f6465d}
.countdown-row{display:flex;align-items:center;justify-content:space-between;margin-top:10px;padding:10px 14px;background:rgba(234,179,8,.07);border:1px solid rgba(234,179,8,.18);border-radius:8px}
.countdown-row span{font-size:12px;color:#848e9c}
.countdown-row strong{font-size:18px;font-weight:800;color:#eab308;font-variant-numeric:tabular-nums}
.countdown-row strong.warning{color:#f6465d}
.payment-content{margin-top:18px;text-align:center}
.payment-title{font-size:13px;color:#cbd2df}
.qr-box{width:210px;height:210px;margin:14px auto 10px;padding:9px;background:#fff;border-radius:9px}
.qr-box img{width:100%;height:100%;object-fit:contain;display:block}
.payment-tip{font-size:11px;line-height:1.6;color:var(--次要灰色文字,#848e9c)}
.warning{color:#eab308}
.network-row{display:flex;justify-content:space-between;margin-top:14px;padding:12px 14px;background:#11141b;border-radius:8px;font-size:12px}
.network-row span{color:#848e9c}
.network-row strong{color:#50e6d2}
.address-box{display:flex;align-items:center;gap:8px;margin-top:8px;padding:10px;background:#11141b;border:1px solid #2b3140;border-radius:8px;text-align:left}
.address-box span{flex:1;min-width:0;color:#dce2ec;font-size:11px;line-height:1.5;overflow-wrap:anywhere}
.address-box button{flex-shrink:0;padding:6px 9px;border:1px solid #343b4d;border-radius:6px;background:transparent;color:#b8c2d2;font-size:11px;cursor:pointer}
.address-box button:hover{border-color:#315bff;color:#315bff}
.status-row{display:flex;align-items:center;justify-content:center;gap:7px;margin-top:18px;color:#b8c2d2;font-size:12px}
.status-dot{width:7px;height:7px;border-radius:50%;background:#eab308}
.status-dot.paid{background:#0ecb81}
.status-dot.cancelled,.status-dot.expired{background:#f6465d}
.success-box,.expired-box{display:flex;flex-direction:column;align-items:center;gap:8px;padding:28px 20px;border-radius:10px;background:#11141b;border:1px solid #2b3140}
.success-box strong{font-size:16px;color:#0ecb81}
.success-box span,.expired-box span{font-size:12px;color:#848e9c}
.expired-box strong{font-size:16px;color:#f6465d}
.license-box{padding:22px 16px;border-radius:10px;background:#11141b;border:1px solid rgba(14,203,129,.35)}
.success-icon{display:flex;align-items:center;justify-content:center;width:38px;height:38px;margin:0 auto 10px;border-radius:50%;background:rgba(14,203,129,.12);border:1px solid rgba(14,203,129,.35);color:#0ecb81;font-size:22px;font-weight:800}
.license-box>strong{display:block;font-size:18px;color:#0ecb81}
.license-box>span{display:block;margin-top:5px;font-size:12px;color:#848e9c}
.license-status{display:flex;align-items:center;justify-content:space-between;margin-top:18px;padding:10px 12px;border-radius:7px;background:#151923}
.license-status span{font-size:11px;color:#848e9c}
.license-status b{font-size:11px;color:#0ecb81}
.license-key{display:flex;align-items:center;gap:8px;margin-top:8px;padding:12px;background:#0b0d12;border:1px solid #2b3140;border-radius:8px;text-align:left}
.license-key>div{flex:1;min-width:0}
.license-key span{display:block;font-size:10px;color:#848e9c;margin-bottom:5px}
.license-key strong{display:block;color:#fff;font-size:13px;line-height:1.5;overflow-wrap:anywhere}
.license-key button{flex-shrink:0;padding:7px 10px;border:1px solid #315bff;border-radius:6px;background:rgba(49,91,255,.1);color:#5f82ff;font-size:11px;cursor:pointer}
.license-key button:hover{background:rgba(49,91,255,.2);color:#fff}
.license-info{display:flex;flex-direction:column;gap:9px;margin-top:14px}
.license-info div{display:flex;justify-content:space-between;gap:10px;font-size:11px}
.license-info span{color:#848e9c}
.license-info b{color:#dce2ec;font-weight:600}
.pay-btn,.check-btn{width:100%;height:46px;border:0;border-radius:9px;background:var(--主色调蓝色,#315bff);color:#fff;font-size:14px;font-weight:700;cursor:pointer;transition:background .2s}
.pay-btn:hover,.check-btn:hover{background:var(--主色调悬停色,#4169ff)}
.pay-btn:disabled,.check-btn:disabled{opacity:.6;cursor:not-allowed}
.check-btn{margin-top:12px}
.error{margin-top:10px;padding:10px 12px;border-radius:7px;background:rgba(246,70,93,.1);color:#f6465d;font-size:12px}
.notice{margin-top:10px;padding:10px 12px;border-radius:7px;background:rgba(49,91,255,.1);color:#9eb2ff;font-size:12px;text-align:center}
.create-area{padding-top:2px}
@media(max-width:560px){
  .purchase-modal{padding:22px}
  .qr-box{width:190px;height:190px}
}
</style>
