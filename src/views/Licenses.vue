
<template>
  <main class="account-page">
    <div class="page-heading">
      <div>
        <p class="eyebrow">LICENSE CENTER</p>
        <h1>我的授权</h1>
        <p class="subtitle">管理 EA 授权码，查看授权状态并绑定 MT5 账户。</p>
      </div>
      <router-link class="back-link" to="/">返回首页</router-link>
    </div>

    <div class="summary-grid">
      <div class="summary-card">
        <span>全部授权</span>
        <strong>{{ licenses.length }}</strong>
      </div>
      <div class="summary-card">
        <span>有效授权</span>
        <strong>{{ licenses.filter(item => item.status === 'active').length }}</strong>
      </div>
      <div class="summary-card">
        <span>已绑定账户</span>
        <strong>{{ licenses.filter(item => item.account).length }}</strong>
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
      <button class="refresh-btn" :disabled="loading" @click="loadLicenses">
        {{ loading ? '加载中…' : '刷新授权' }}
      </button>
    </div>

    <div v-if="loading && !licenses.length" class="state-panel">
      <span class="loader"></span>
      正在加载授权…
    </div>

    <div v-else-if="loadError" class="state-panel error-panel">
      <p>{{ loadError }}</p>
      <button class="primary-btn" @click="loadLicenses">重新加载</button>
      <router-link v-if="isAuthError" to="/" class="text-link">
        返回首页重新登录
      </router-link>
    </div>

    <template v-else>
      <div v-if="!filteredLicenses.length" class="state-panel">
        <div class="empty-icon">◇</div>
        <h3>{{ licenses.length ? '没有符合条件的授权' : '暂时没有授权' }}</h3>
        <p>
          {{ licenses.length
            ? '请尝试切换授权状态筛选。'
            : '订单确认付款后，系统会为该订单生成授权。' }}
        </p>
        <router-link v-if="!licenses.length" class="primary-btn link-btn" to="/orders">
          查看我的订单
        </router-link>
      </div>

      <div v-else class="license-list">
        <article v-for="item in filteredLicenses" :key="item.license_key" class="license-card">
          <div class="license-head">
            <div class="product-mark">EA</div>
            <div class="license-product">
              <h2>{{ item.product_name || `EA 产品 #${item.product_id}` }}</h2>
              <p>授权类型：{{ licenseTypeLabel(item.license_type) }}</p>
            </div>
            <span class="status" :class="`status-${item.status}`">
              {{ statusLabel(item.status) }}
            </span>
          </div>

          <div class="license-key-block">
            <div>
              <span>授权码</span>
              <strong>{{ item.license_key }}</strong>
            </div>
            <button class="copy-btn" @click="copyKey(item.license_key)">复制授权码</button>
          </div>

          <div class="license-info">
            <div>
              <span>MT5 账户</span>
              <strong>{{ item.account || '尚未绑定' }}</strong>
            </div>
            <div>
              <span>授权创建时间</span>
              <strong>{{ formatDate(item.created_at) }}</strong>
            </div>
            <div>
              <span>有效期</span>
              <strong>{{ item.expires_at ? formatDate(item.expires_at) : '长期有效' }}</strong>
            </div>
            <div>
              <span>关联订单</span>
              <strong>{{ item.order_no || '—' }}</strong>
            </div>
          </div>

          <div class="license-actions">
            <button class="text-btn" @click="openDetails(item)">查看详情</button>
            <button
              v-if="item.status === 'active' && !item.account"
              class="primary-btn"
              @click="openBind(item)"
            >
              绑定 MT5 账户
            </button>
            <span v-else-if="item.account" class="bound-label">
              <span class="bound-dot"></span>
              已绑定账户
            </span>
          </div>
        </article>
      </div>
    </template>

    <p v-if="notice.text" class="notice" :class="notice.type">
      {{ notice.text }}
    </p>

    <div v-if="selectedLicense" class="modal-mask" @click.self="closeDetails">
      <section class="detail-modal">
        <button class="close-btn" aria-label="关闭" @click="closeDetails">×</button>
        <p class="eyebrow">LICENSE DETAILS</p>
        <h2>授权详情</h2>

        <div v-if="detailLoading" class="modal-state">正在加载授权详情…</div>
        <div v-else-if="detailError" class="modal-error">{{ detailError }}</div>
        <template v-else-if="detail">
          <div class="detail-rows">
            <div><span>产品名称</span><strong>{{ detail.product_name || `EA 产品 #${detail.product_id}` }}</strong></div>
            <div><span>授权状态</span><strong>{{ statusLabel(detail.status) }}</strong></div>
            <div class="key-row"><span>授权码</span><strong>{{ detail.license_key }}</strong></div>
            <div><span>授权类型</span><strong>{{ licenseTypeLabel(detail.license_type) }}</strong></div>
            <div><span>MT5 账户</span><strong>{{ detail.account || '尚未绑定' }}</strong></div>
            <div><span>创建时间</span><strong>{{ formatDate(detail.created_at) }}</strong></div>
            <div><span>有效期</span><strong>{{ detail.expires_at ? formatDate(detail.expires_at) : '长期有效' }}</strong></div>
            <div><span>关联订单</span><strong>{{ detail.order_no || '—' }}</strong></div>
          </div>

          <div class="modal-actions">
            <button class="secondary-btn" @click="copyKey(detail.license_key)">复制授权码</button>
            <button
              v-if="detail.status === 'active' && !detail.account"
              class="primary-btn"
              @click="openBind(detail)"
            >
              绑定 MT5 账户
            </button>
            <button class="secondary-btn" @click="closeDetails">关闭</button>
          </div>
        </template>
      </section>
    </div>

    <div v-if="bindTarget" class="modal-mask" @click.self="closeBind">
      <section class="detail-modal bind-modal">
        <button class="close-btn" aria-label="关闭" @click="closeBind">×</button>
        <p class="eyebrow">MT5 ACCOUNT BINDING</p>
        <h2>绑定 MT5 账户</h2>
        <p class="bind-description">
          绑定后，此授权码只能用于绑定的 MT5 账户。请确认账户号码准确无误。
        </p>

        <div class="bind-key">
          <span>授权码</span>
          <strong>{{ bindTarget.license_key }}</strong>
        </div>

        <form @submit.prevent="submitBinding">
          <label class="field">
            <span>MT5 账户号码</span>
            <input
              v-model="bindAccount"
              type="text"
              maxlength="100"
              autocomplete="off"
              placeholder="请输入 MT5 账户号码"
              required
            />
          </label>

          <p v-if="bindError" class="inline-error">{{ bindError }}</p>

          <div class="modal-actions">
            <button class="secondary-btn" type="button" @click="closeBind">取消</button>
            <button class="primary-btn" type="submit" :disabled="binding">
              {{ binding ? '绑定中…' : '确认绑定' }}
            </button>
          </div>
        </form>
      </section>
    </div>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import {
  fetchLicenses,
  fetchLicense,
  bindLicense
} from '../services/account'

const licenses = ref([])
const loading = ref(true)
const loadError = ref('')
const activeFilter = ref('all')

const selectedLicense = ref(null)
const detail = ref(null)
const detailLoading = ref(false)
const detailError = ref('')

const bindTarget = ref(null)
const bindAccount = ref('')
const bindError = ref('')
const binding = ref(false)

const notice = ref({ text: '', type: 'success' })

const filters = [
  { label: '全部', value: 'all' },
  { label: '有效', value: 'active' },
  { label: '已过期', value: 'expired' },
  { label: '已停用', value: 'disabled' }
]

const filteredLicenses = computed(() => {
  if (activeFilter.value === 'all') return licenses.value
  return licenses.value.filter(item => item.status === activeFilter.value)
})

const isAuthError = computed(() =>
  /登录已失效|请先登录|重新登录/.test(loadError.value)
)

function statusLabel(status) {
  return ({
    active: '有效',
    expired: '已过期',
    disabled: '已停用',
    revoked: '已撤销'
  })[status] || status || '未知状态'
}

function licenseTypeLabel(type) {
  return ({
    single_account: '单账户授权'
  })[type] || type || '—'
}

function formatDate(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '—'
  return date.toLocaleString('zh-CN', { hour12: false })
}

function showNotice(text, type = 'success') {
  notice.value = { text, type }
}

async function loadLicenses() {
  loading.value = true
  loadError.value = ''

  try {
    licenses.value = await fetchLicenses()
  } catch (error) {
    loadError.value = error.message || '授权列表加载失败'
  } finally {
    loading.value = false
  }
}

async function openDetails(item) {
  selectedLicense.value = item
  detail.value = null
  detailError.value = ''
  detailLoading.value = true

  try {
    detail.value = await fetchLicense(item.license_key)
  } catch (error) {
    detailError.value = error.message || '授权详情加载失败'
  } finally {
    detailLoading.value = false
  }
}

function closeDetails() {
  selectedLicense.value = null
  detail.value = null
  detailError.value = ''
}

function openBind(item) {
  bindTarget.value = item
  bindAccount.value = item.account || ''
  bindError.value = ''
}

function closeBind() {
  bindTarget.value = null
  bindAccount.value = ''
  bindError.value = ''
}

async function submitBinding() {
  if (!bindTarget.value || binding.value) return

  const account = bindAccount.value.trim()

  if (!account) {
    bindError.value = '请输入 MT5 账户号码'
    return
  }

  binding.value = true
  bindError.value = ''

  try {
    const updated = await bindLicense(
      bindTarget.value.license_key,
      account
    )

    licenses.value = licenses.value.map(item =>
      item.license_key === updated.license_key
        ? { ...item, ...updated }
        : item
    )

    if (detail.value?.license_key === updated.license_key) {
      detail.value = { ...detail.value, ...updated }
    }

    showNotice('MT5 账户绑定成功')
    closeBind()
  } catch (error) {
    bindError.value = error.message || '绑定失败'
  } finally {
    binding.value = false
  }
}

async function copyKey(key) {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(key)
    } else {
      const textarea = document.createElement('textarea')
      textarea.value = key
      textarea.style.position = 'fixed'
      textarea.style.opacity = '0'
      document.body.appendChild(textarea)
      textarea.select()
      const copied = document.execCommand('copy')
      textarea.remove()

      if (!copied) throw new Error('复制失败，请手动选择授权码')
    }

    showNotice('授权码已复制')
  } catch (error) {
    showNotice(error.message || '复制失败，请手动复制授权码', 'error')
  }
}

onMounted(loadLicenses)
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
.license-key-block span,
.license-info span {
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

.license-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.license-card {
  padding: 22px;
  background: #141722;
  border: 1px solid #222630;
  border-radius: 10px;
}

.license-head {
  display: flex;
  align-items: center;
  gap: 14px;
}

.product-mark {
  display: grid;
  width: 50px;
  height: 50px;
  flex-shrink: 0;
  place-items: center;
  color: #9fb1ff;
  background: #202c53;
  border: 1px solid #344778;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 700;
}

.license-product {
  min-width: 0;
  flex: 1;
}

.license-product h2 {
  margin: 0 0 7px;
  font-size: 15px;
  overflow-wrap: anywhere;
}

.license-product p {
  margin: 0;
  color: #848e9c;
  font-size: 11px;
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

.status-active {
  color: #83d8ae;
  background: #18352b;
  border-color: #285541;
}

.status-expired,
.status-disabled,
.status-revoked {
  color: #939baa;
  background: #242833;
  border-color: #353b48;
}

.license-key-block {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  margin-top: 22px;
  padding: 15px;
  background: #10131b;
  border: 1px solid #252b38;
  border-radius: 8px;
}

.license-key-block > div {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 9px;
}

.license-key-block strong {
  overflow-wrap: anywhere;
  color: #9fb1ff;
  font-size: 12px;
  font-weight: 600;
}

.copy-btn {
  min-height: 32px;
  flex-shrink: 0;
  padding: 0 10px;
  color: #9fb1ff;
  background: #202c53;
  border: 1px solid #344778;
  border-radius: 5px;
  cursor: pointer;
  font: inherit;
  font-size: 11px;
}

.copy-btn:hover {
  background: #283866;
}

.license-info {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 20px;
  padding: 22px 0;
}

.license-info > div {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 9px;
}

.license-info strong {
  overflow-wrap: anywhere;
  font-size: 12px;
  font-weight: 500;
}

.license-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 20px;
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

.primary-btn {
  display: inline-flex;
  min-height: 38px;
  align-items: center;
  justify-content: center;
  padding: 0 16px;
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

.bound-label {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  color: #83d8ae;
  font-size: 12px;
}

.bound-dot {
  width: 6px;
  height: 6px;
  background: #50c98b;
  border-radius: 50%;
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
  font-size: 34px;
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
  margin: 0 0 22px;
  font-size: 21px;
}

.detail-rows {
  display: flex;
  flex-direction: column;
  gap: 17px;
}

.detail-rows > div {
  display: flex;
  justify-content: space-between;
  gap: 18px;
}

.detail-rows span {
  flex-shrink: 0;
  color: #848e9c;
  font-size: 11px;
}

.detail-rows strong {
  max-width: 68%;
  overflow-wrap: anywhere;
  font-size: 12px;
  font-weight: 500;
  text-align: right;
}

.key-row strong {
  color: #9fb1ff;
}

.modal-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 26px;
}

.bind-description {
  color: #848e9c;
  font-size: 12px;
  line-height: 1.8;
}

.bind-key {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 18px 0;
  padding: 14px;
  background: #10131b;
  border: 1px solid #252b38;
  border-radius: 7px;
}

.bind-key span,
.field > span {
  color: #848e9c;
  font-size: 11px;
}

.bind-key strong {
  overflow-wrap: anywhere;
  color: #9fb1ff;
  font-size: 12px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.field input {
  width: 100%;
  height: 43px;
  padding: 0 13px;
  color: #e7eaf0;
  background: #1b1e26;
  border: 1px solid #303542;
  border-radius: 7px;
  outline: none;
  font: inherit;
  font-size: 13px;
}

.field input:focus {
  border-color: #315bff;
  box-shadow: 0 0 0 3px #315bff20;
}

.field input::placeholder {
  color: #626b79;
}

.inline-error,
.modal-error {
  color: #f08f8f;
  font-size: 12px;
}

.modal-state {
  padding: 20px 0;
  color: #848e9c;
  font-size: 13px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 760px) {
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

  .license-card {
    padding: 16px;
  }

  .license-head {
    flex-wrap: wrap;
  }

  .license-product {
    width: calc(100% - 70px);
    flex: none;
  }

  .license-head .status {
    margin-left: 64px;
  }

  .license-key-block {
    align-items: flex-start;
    flex-direction: column;
  }

  .license-info {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 18px;
  }

  .detail-modal {
    padding: 24px 18px;
  }
}
</style>

