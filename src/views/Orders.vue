
<template>
  <main class="account-page">
    <div class="page-heading">
      <div>
        <p class="eyebrow">ORDER CENTER</p>
        <h1>我的订单</h1>
        <p class="subtitle">查看购买记录、订单状态和支付信息。</p>
      </div>
      <router-link class="back-link" to="/">返回首页</router-link>
    </div>

    <div class="summary-grid">
      <div class="summary-card">
        <span>全部订单</span>
        <strong>{{ orders.length }}</strong>
      </div>
      <div class="summary-card">
        <span>待付款</span>
        <strong>{{ countStatus('pending') }}</strong>
      </div>
      <div class="summary-card">
        <span>已付款</span>
        <strong>{{ countStatus('paid') }}</strong>
      </div>
    </div>

    <div class="toolbar">
      <div class="filters">
        <button
          v-for="item in filters"
          :key="item.value"
          class="filter-btn"
          :class="{ active: activeFilter === item.value }"
          @click="activeFilter = item.value"
        >
          {{ item.label }}
        </button>
      </div>
      <button class="refresh-btn" :disabled="loading" @click="loadOrders">
        {{ loading ? '加载中…' : '刷新订单' }}
      </button>
    </div>

    <div v-if="loading && !orders.length" class="state-panel">
      <span class="loader"></span>
      正在加载订单…
    </div>

    <div v-else-if="loadError" class="state-panel error-panel">
      <p>{{ loadError }}</p>
      <button class="primary-btn" @click="loadOrders">重新加载</button>
      <router-link v-if="isAuthError" to="/" class="text-link">
        返回首页重新登录
      </router-link>
    </div>

    <template v-else>
      <div v-if="!filteredOrders.length" class="state-panel">
        <div class="empty-icon">▤</div>
        <h3>{{ orders.length ? '没有符合条件的订单' : '还没有订单' }}</h3>
        <p>{{ orders.length ? '请尝试切换状态筛选。' : '购买 EA 后，订单会显示在这里。' }}</p>
        <router-link v-if="!orders.length" class="primary-btn link-btn" to="/market">
          浏览 EA 产品
        </router-link>
      </div>

      <div v-else class="order-list">
        <article v-for="order in filteredOrders" :key="order.order_no" class="order-card">
          <div class="order-head">
            <div class="order-number">
              <span>订单编号</span>
              <strong>{{ order.order_no }}</strong>
            </div>
            <span class="status" :class="`status-${order.status}`">
              {{ statusLabel(order.status) }}
            </span>
          </div>

          <div class="order-main">
            <div class="product-mark">EA</div>
            <div class="product-info">
              <h2>{{ order.product_name || `EA 产品 #${order.product_id}` }}</h2>
              <p>订单创建时间：{{ formatDate(order.created_at) }}</p>
              <p>支付方式：{{ paymentLabel(order.payment_method) }}</p>
            </div>
            <div class="order-amount">
              <span>订单金额</span>
              <strong>{{ formatAmount(order.amount, order.currency) }}</strong>
            </div>
          </div>

          <div class="order-foot">
            <button class="text-btn" @click="openDetails(order)">
              查看详情
            </button>
            <button
              v-if="order.status === 'pending'"
              class="text-btn danger-btn"
              :disabled="busyOrder === order.order_no"
              @click="handleCancel(order)"
            >
              {{ busyOrder === order.order_no ? '处理中…' : '取消订单' }}
            </button>
            <button
              v-if="order.status === 'paid'"
              class="text-btn"
              :disabled="busyOrder === order.order_no"
              @click="viewLicense(order)"
            >
              {{ busyOrder === order.order_no ? '查询中…' : '查看授权' }}
            </button>
          </div>
        </article>
      </div>
    </template>

    <p v-if="notice.text" class="notice" :class="notice.type">
      {{ notice.text }}
    </p>

    <div v-if="selectedOrder" class="modal-mask" @click.self="closeDetails">
      <section class="detail-modal">
        <button class="close-btn" aria-label="关闭" @click="closeDetails">×</button>
        <p class="eyebrow">ORDER DETAILS</p>
        <h2>订单详情</h2>

        <div v-if="detailLoading" class="modal-state">正在加载订单详情…</div>
        <div v-else-if="detailError" class="modal-error">{{ detailError }}</div>
        <template v-else-if="detail">
          <div class="detail-product">
            <div>
              <span>商品名称</span>
              <strong>{{ detail.product_name || `EA 产品 #${detail.product_id}` }}</strong>
            </div>
            <span class="status" :class="`status-${detail.status}`">
              {{ statusLabel(detail.status) }}
            </span>
          </div>

          <div class="detail-rows">
            <div><span>订单编号</span><strong>{{ detail.order_no }}</strong></div>
            <div><span>订单金额</span><strong>{{ formatAmount(detail.amount, detail.currency) }}</strong></div>
            <div><span>支付方式</span><strong>{{ paymentLabel(detail.payment_method) }}</strong></div>
            <div><span>创建时间</span><strong>{{ formatDate(detail.created_at) }}</strong></div>
            <div><span>付款时间</span><strong>{{ formatDate(detail.paid_at) }}</strong></div>
            <div><span>订单过期时间</span><strong>{{ formatDate(detail.expires_at) }}</strong></div>
          </div>

          <div v-if="license" class="license-result">
            <span>关联授权码</span>
            <strong>{{ license.license_key }}</strong>
            <router-link to="/licenses" class="text-link">前往我的授权</router-link>
          </div>

          <div class="modal-actions">
            <button
              v-if="detail.status === 'paid' && !license"
              class="primary-btn"
              :disabled="licenseLoading"
              @click="loadOrderLicense(detail.order_no)"
            >
              {{ licenseLoading ? '查询中…' : '查询关联授权' }}
            </button>
            <button
              v-if="detail.status === 'pending'"
              class="primary-btn"
              :disabled="busyOrder === detail.order_no"
              @click="handleCancel(detail)"
            >
              取消订单
            </button>
            <button class="secondary-btn" @click="closeDetails">关闭</button>
          </div>
        </template>
      </section>
    </div>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import {
  fetchOrders,
  fetchOrder,
  cancelOrder,
  fetchOrderLicense
} from '../services/account'

const orders = ref([])
const loading = ref(true)
const loadError = ref('')
const activeFilter = ref('all')
const busyOrder = ref('')

const selectedOrder = ref(null)
const detail = ref(null)
const detailLoading = ref(false)
const detailError = ref('')
const license = ref(null)
const licenseLoading = ref(false)

const notice = ref({ text: '', type: 'success' })

const filters = [
  { label: '全部', value: 'all' },
  { label: '待付款', value: 'pending' },
  { label: '已付款', value: 'paid' },
  { label: '已取消', value: 'cancelled' },
  { label: '已过期', value: 'expired' }
]

const filteredOrders = computed(() => {
  if (activeFilter.value === 'all') return orders.value
  return orders.value.filter(order => order.status === activeFilter.value)
})

const isAuthError = computed(() =>
  /登录已失效|请先登录|重新登录/.test(loadError.value)
)

function statusLabel(status) {
  return ({
    pending: '待付款',
    paid: '已付款',
    cancelled: '已取消',
    expired: '已过期'
  })[status] || status || '未知状态'
}

function paymentLabel(method) {
  return ({
    wechat: '微信支付',
    alipay: '支付宝',
    usdt: 'USDT · TRC20'
  })[method] || method || '—'
}

function formatAmount(amount, currency) {
  if (amount == null) return '—'
  const value = Number(amount)
  if (!Number.isFinite(value)) return `${amount} ${currency || ''}`.trim()
  return `${currency === 'USDT' ? '₮' : '¥'}${value.toFixed(2)}`
}

function formatDate(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '—'
  return date.toLocaleString('zh-CN', { hour12: false })
}

function countStatus(status) {
  return orders.value.filter(order => order.status === status).length
}

function showNotice(text, type = 'success') {
  notice.value = { text, type }
}

async function loadOrders() {
  loading.value = true
  loadError.value = ''

  try {
    orders.value = await fetchOrders()
  } catch (error) {
    loadError.value = error.message || '订单加载失败'
  } finally {
    loading.value = false
  }
}

async function openDetails(order) {
  selectedOrder.value = order
  detail.value = null
  detailError.value = ''
  license.value = null
  detailLoading.value = true

  try {
    detail.value = await fetchOrder(order.order_no)
  } catch (error) {
    detailError.value = error.message || '订单详情加载失败'
  } finally {
    detailLoading.value = false
  }
}

function closeDetails() {
  selectedOrder.value = null
  detail.value = null
  detailError.value = ''
  license.value = null
}

async function handleCancel(order) {
  if (order.status !== 'pending' || busyOrder.value) return

  if (!window.confirm(`确定取消订单 ${order.order_no} 吗？`)) return

  busyOrder.value = order.order_no
  notice.value = { text: '', type: 'success' }

  try {
    await cancelOrder(order.order_no)
    showNotice('订单已取消')
    await loadOrders()

    if (selectedOrder.value?.order_no === order.order_no) {
      await openDetails(order)
    }
  } catch (error) {
    showNotice(error.message || '取消订单失败', 'error')
  } finally {
    busyOrder.value = ''
  }
}

async function loadOrderLicense(orderNo) {
  licenseLoading.value = true

  try {
    license.value = await fetchOrderLicense(orderNo)
  } catch (error) {
    detailError.value = error.message || '授权查询失败'
  } finally {
    licenseLoading.value = false
  }
}

async function viewLicense(order) {
  busyOrder.value = order.order_no

  try {
    await fetchOrderLicense(order.order_no)
    window.location.href = '/EA/licenses'
  } catch (error) {
    showNotice(error.message || '授权查询失败', 'error')
  } finally {
    busyOrder.value = ''
  }
}

onMounted(loadOrders)
</script>

<style scoped>
.account-page {
  width: min(1100px, calc(100% - 32px));
  margin: 0 auto;
  padding: 44px 0 80px;
  color: #e7eaf0;
}

.page-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 28px;
}

.eyebrow {
  margin: 0 0 10px;
  color: #6484ff;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 2px;
}

h1 {
  margin: 0 0 10px;
  font-size: 30px;
  font-weight: 650;
}

.subtitle {
  margin: 0;
  color: #848e9c;
  font-size: 13px;
  line-height: 1.7;
}

.back-link,
.text-link {
  color: #8da4ff;
  font-size: 13px;
  text-decoration: none;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 26px;
}

.summary-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 20px;
  background: #141722;
  border: 1px solid #222630;
  border-radius: 10px;
}

.summary-card span,
.order-number span,
.order-amount span {
  color: #848e9c;
  font-size: 12px;
}

.summary-card strong {
  font-size: 27px;
  font-weight: 650;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-btn,
.refresh-btn,
.secondary-btn {
  min-height: 35px;
  padding: 0 13px;
  color: #9aa3b2;
  background: #141722;
  border: 1px solid #292e3a;
  border-radius: 6px;
  cursor: pointer;
  font: inherit;
  font-size: 12px;
}

.filter-btn:hover,
.refresh-btn:hover,
.secondary-btn:hover {
  color: #e7eaf0;
  border-color: #46516a;
}

.filter-btn.active {
  color: #fff;
  background: #315bff;
  border-color: #315bff;
}

.refresh-btn:disabled {
  cursor: wait;
  opacity: 0.6;
}

.order-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.order-card {
  padding: 22px;
  background: #141722;
  border: 1px solid #222630;
  border-radius: 10px;
}

.order-head,
.order-main,
.order-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
}

.order-head {
  padding-bottom: 17px;
  border-bottom: 1px solid #252936;
}

.order-number {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 7px;
}

.order-number strong {
  overflow-wrap: anywhere;
  font-size: 12px;
  font-weight: 550;
}

.status {
  display: inline-flex;
  flex-shrink: 0;
  align-items: center;
  padding: 5px 9px;
  border: 1px solid;
  border-radius: 5px;
  font-size: 11px;
}

.status-pending {
  color: #e6b568;
  background: #382d1c;
  border-color: #59472b;
}

.status-paid {
  color: #83d8ae;
  background: #18352b;
  border-color: #285541;
}

.status-cancelled,
.status-expired {
  color: #939baa;
  background: #242833;
  border-color: #353b48;
}

.order-main {
  justify-content: flex-start;
  padding: 22px 0;
}

.product-mark {
  display: grid;
  width: 54px;
  height: 54px;
  flex-shrink: 0;
  place-items: center;
  color: #9fb1ff;
  background: #202c53;
  border: 1px solid #344778;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 700;
}

.product-info {
  min-width: 0;
  flex: 1;
}

.product-info h2 {
  margin: 0 0 10px;
  font-size: 15px;
}

.product-info p {
  margin: 0 0 6px;
  color: #848e9c;
  font-size: 11px;
  line-height: 1.5;
  overflow-wrap: anywhere;
}

.order-amount {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.order-amount strong {
  color: #e7eaf0;
  font-size: 19px;
  white-space: nowrap;
}

.order-foot {
  justify-content: flex-end;
  padding-top: 15px;
  border-top: 1px solid #252936;
}

.text-btn {
  padding: 4px 0;
  color: #8da4ff;
  background: transparent;
  border: 0;
  cursor: pointer;
  font: inherit;
  font-size: 12px;
}

.text-btn:hover {
  color: #b3c2ff;
}

.text-btn:disabled {
  cursor: wait;
  opacity: 0.5;
}

.danger-btn {
  color: #e98c8c;
}

.danger-btn:hover {
  color: #ffb0b0;
}

.primary-btn {
  display: inline-flex;
  min-height: 39px;
  align-items: center;
  justify-content: center;
  padding: 0 18px;
  color: #fff;
  background: #315bff;
  border: 1px solid #315bff;
  border-radius: 7px;
  cursor: pointer;
  font: inherit;
  font-size: 12px;
  text-decoration: none;
}

.primary-btn:hover {
  background: #4169ff;
}

.primary-btn:disabled {
  cursor: wait;
  opacity: 0.6;
}

.link-btn {
  margin-top: 5px;
}

.state-panel {
  display: flex;
  min-height: 190px;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  padding: 24px;
  color: #848e9c;
  background: #141722;
  border: 1px solid #222630;
  border-radius: 10px;
  text-align: center;
}

.state-panel h3 {
  margin: 0;
  color: #e7eaf0;
  font-size: 16px;
}

.state-panel p {
  margin: 0;
  font-size: 13px;
}

.empty-icon {
  color: #6879a8;
  font-size: 32px;
}

.error-panel {
  color: #f08f8f;
}

.loader {
  width: 22px;
  height: 22px;
  border: 2px solid #303747;
  border-top-color: #315bff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.notice {
  margin-top: 16px;
  padding: 12px 15px;
  border: 1px solid;
  border-radius: 7px;
  font-size: 12px;
}

.notice.success {
  color: #83d8ae;
  background: #18352b;
  border-color: #285541;
}

.notice.error {
  color: #f08f8f;
  background: #351e24;
  border-color: #5a2b36;
}

.modal-mask {
  position: fixed;
  z-index: 2000;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: #05070bd9;
  backdrop-filter: blur(5px);
}

.detail-modal {
  position: relative;
  width: min(540px, 100%);
  max-height: min(85vh, 760px);
  overflow: auto;
  padding: 28px;
  color: #e7eaf0;
  background: #141722;
  border: 1px solid #303543;
  border-radius: 12px;
  box-shadow: 0 24px 80px #0008;
}

.close-btn {
  position: absolute;
  top: 14px;
  right: 16px;
  color: #848e9c;
  background: transparent;
  border: 0;
  cursor: pointer;
  font-size: 25px;
}

.detail-modal > h2 {
  margin: 0 0 24px;
  font-size: 21px;
}

.detail-product {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding-bottom: 18px;
  border-bottom: 1px solid #292e3a;
}

.detail-product > div {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 8px;
}

.detail-product > div span,
.detail-rows span,
.license-result > span {
  color: #848e9c;
  font-size: 11px;
}

.detail-product strong {
  overflow-wrap: anywhere;
  font-size: 14px;
}

.detail-rows {
  display: flex;
  flex-direction: column;
  gap: 17px;
  padding: 20px 0;
}

.detail-rows > div {
  display: flex;
  justify-content: space-between;
  gap: 18px;
}

.detail-rows strong {
  max-width: 68%;
  overflow-wrap: anywhere;
  font-size: 12px;
  font-weight: 500;
  text-align: right;
}

.license-result {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 15px;
  background: #101b18;
  border: 1px solid #285541;
  border-radius: 7px;
}

.license-result strong {
  overflow-wrap: anywhere;
  color: #83d8ae;
  font-size: 12px;
}

.modal-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 24px;
}

.modal-state,
.modal-error {
  padding: 24px 0;
  color: #848e9c;
  font-size: 13px;
}

.modal-error {
  color: #f08f8f;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 680px) {
  .account-page {
    width: calc(100% - 24px);
    padding-top: 28px;
  }

  .page-heading {
    align-items: flex-start;
  }

  h1 {
    font-size: 25px;
  }

  .summary-grid {
    gap: 8px;
  }

  .summary-card {
    padding: 14px 12px;
  }

  .summary-card strong {
    font-size: 23px;
  }

  .toolbar {
    align-items: flex-start;
    flex-direction: column;
  }

  .order-card {
    padding: 16px;
  }

  .order-main {
    flex-wrap: wrap;
    gap: 12px;
  }

  .product-info {
    width: calc(100% - 70px);
  }

  .order-amount {
    width: 100%;
    align-items: flex-start;
  }

  .order-foot {
    gap: 18px;
  }

  .detail-modal {
    padding: 24px 18px;
  }

  .detail-rows > div {
    align-items: flex-start;
  }
}
</style>

