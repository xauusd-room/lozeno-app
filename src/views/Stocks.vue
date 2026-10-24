
<template>
  <section class="stocks-page">
    <div v-if="loading" class="loading-overlay">
      <div class="loading-content">
        <span class="loading-spinner"></span>
        <span class="loading-title">正在加载股票分析系统</span>
        <span class="loading-description">正在连接 DSA 前端</span>
      </div>
    </div>

    <div v-if="loadError" class="error-overlay">
      <div class="error-card">
        <div class="error-icon">!</div>
        <h2>股票分析系统暂时无法加载</h2>
        <p>请确认 DSA 前端服务仍可访问。</p>
        <p class="error-address">https://lozeno-stocks.pages.dev/</p>
        <button class="retry-button" @click="reloadDSA">
          重新加载
        </button>
      </div>
    </div>

    <iframe
      :key="frameKey"
      ref="dsaFrame"
      class="dsa-frame"
      :src="DSA_URL"
      title="LOZENO DSA 股票分析系统"
      allow="clipboard-read; clipboard-write"
      referrerpolicy="strict-origin-when-cross-origin"
      @load="handleLoad"
    />
  </section>
</template>

<script setup>
import { ref } from 'vue'

const DSA_URL = 'https://lozeno-stocks.pages.dev/'

const loading = ref(true)
const loadError = ref(false)
const frameKey = ref(0)

let loadTimeout = null

function clearLoadTimeout() {
  if (loadTimeout !== null) {
    clearTimeout(loadTimeout)
    loadTimeout = null
  }
}

function startLoadTimeout() {
  clearLoadTimeout()

  loadTimeout = setTimeout(() => {
    if (loading.value) {
      loading.value = false
      loadError.value = true
    }
  }, 20000)
}

function handleLoad() {
  clearLoadTimeout()
  loading.value = false
  loadError.value = false
}

function reloadDSA() {
  clearLoadTimeout()
  loading.value = true
  loadError.value = false
  frameKey.value += 1
  startLoadTimeout()
}

startLoadTimeout()
</script>

<style scoped>
.stocks-page {
  position: relative;
  width: 100%;
  height: calc(100vh - 74px);
  min-height: calc(100vh - 74px);
  overflow: hidden;
  background: #0b0d12;
}

.dsa-frame {
  display: block;
  width: 100%;
  height: 100%;
  border: 0;
  background: #0b0d12;
}

.loading-overlay,
.error-overlay {
  position: absolute;
  z-index: 2;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0b0d12;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.loading-spinner {
  width: 30px;
  height: 30px;
  border: 3px solid #222630;
  border-top-color: #315bff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.loading-title {
  color: #e8eaf0;
  font-size: 15px;
  font-weight: 600;
}

.loading-description {
  color: #848e9c;
  font-size: 13px;
}

.error-card {
  width: min(420px, calc(100% - 40px));
  padding: 32px 24px;
  text-align: center;
  border: 1px solid #222630;
  border-radius: 14px;
  background: #141722;
}

.error-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  margin: 0 auto 16px;
  border: 1px solid #f6465d;
  border-radius: 50%;
  color: #f6465d;
  font-size: 22px;
  font-weight: 700;
}

.error-card h2 {
  margin: 0 0 12px;
  color: #e8eaf0;
  font-size: 17px;
}

.error-card p {
  margin: 8px 0;
  color: #848e9c;
  font-size: 13px;
  line-height: 1.6;
}

.error-address {
  color: #9bb0ff !important;
  overflow-wrap: anywhere;
}

.retry-button {
  margin-top: 18px;
  padding: 10px 22px;
  border: 0;
  border-radius: 8px;
  color: #fff;
  background: #315bff;
  cursor: pointer;
  transition: background 0.2s ease;
}

.retry-button:hover {
  background: #4169ff;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 768px) {
  .stocks-page {
    height: calc(100dvh - 64px);
    min-height: calc(100dvh - 64px);
  }
}
</style>
