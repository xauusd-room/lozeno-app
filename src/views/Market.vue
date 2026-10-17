
<template>
  <main class="market-page page-container">
    <header class="market-header">
      <div>
        <h1>黄金投资行情</h1>
        <p>宏观驱动 · 市场情绪 · 风险矩阵 · 技术面</p>
      </div>
      <span class="update-time">{{ updateTime }}</span>
    </header>

    <div v-if="loading" class="state-panel">
      <span class="spinner"></span>
      <p>正在加载行情数据…</p>
    </div>

    <div v-else-if="error" class="state-panel error">
      <strong>行情数据加载失败</strong>
      <p>{{ error }}</p>
      <p>请确认 public/data/dashboard.json 已生成，并且可以通过 /data/dashboard.json 访问。</p>
      <button @click="loadData">重新加载</button>
    </div>

    <template v-else>
      <MarketSummary :data="data" />
      <h2 class="section-title">核心驱动因子与市场情绪</h2>
      <div class="main-grid">
        <MarketCharts :data="data" />
        <MarketSentiment :data="data" />
      </div>
      <h2 class="section-title">利好 / 利空信号</h2>
      <MarketSignals :data="data" />
      <h2 class="section-title">投资标的风险矩阵</h2>
      <MarketRiskMatrix :data="data" />
      <h2 class="section-title">走势预期</h2>
      <MarketOutlook :data="data" />
      <h2 class="section-title">技术面快照</h2>
      <MarketTechnicals :data="data" />
      <footer class="market-footer">
        数据来源：
        <a href="https://fred.stlouisfed.org" target="_blank" rel="noreferrer">FRED</a>、
        <a href="https://finance.yahoo.com" target="_blank" rel="noreferrer">Yahoo Finance</a>、
        <a href="https://www.cftc.gov" target="_blank" rel="noreferrer">CFTC</a>。
        本页面仅供信息参考，不构成投资建议；数据可能存在延迟或误差，历史表现不代表未来结果。
      </footer>
    </template>
  </main>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import MarketSummary from '../components/Market/MarketSummary.vue'
import MarketCharts from '../components/Market/MarketCharts.vue'
import MarketSentiment from '../components/Market/MarketSentiment.vue'
import MarketSignals from '../components/Market/MarketSignals.vue'
import MarketRiskMatrix from '../components/Market/MarketRiskMatrix.vue'
import MarketOutlook from '../components/Market/MarketOutlook.vue'
import MarketTechnicals from '../components/Market/MarketTechnicals.vue'

const data = ref(null)
const loading = ref(true)
const error = ref('')

const updateTime = computed(() => {
  if (!data.value?.lastUpdated) return '更新时间：--'
  const d = new Date(data.value.lastUpdated)
  return Number.isNaN(d.getTime()) ? '更新时间：--' : `最后更新：${d.toLocaleDateString('zh-CN')} ${d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}`
})

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    const r = await fetch('/data/dashboard.json', { cache: 'no-store' })
    if (!r.ok) throw new Error(`HTTP ${r.status}：未找到 /data/dashboard.json`)
    const json = await r.json()
    if (!json || !json.prices || !json.history) throw new Error('dashboard.json 缺少 prices 或 history 数据')
    data.value = json
  } catch (e) {
    error.value = e.message || '未知错误'
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>

.market-page{
  width:100%;
  min-width:0;
  padding-top:28px;
  padding-bottom:36px;
  color:var(--主要文字颜色,#fff);
  font-size:var(--正文常规字号,14px);
}
.market-header{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:20px}
.market-header h1{font-size:var(--页面大标题字号,32px);font-weight:800;letter-spacing:-.5px}
.market-header p{margin-top:6px;color:var(--次要灰色文字,#848e9c);font-size:var(--辅助副文本字号,13px)}
.update-time{font-size:var(--辅助副文本字号,13px);color:var(--次要灰色文字,#848e9c);white-space:nowrap}
.section-title{font-size:16px;font-weight:750;color:var(--主要文字颜色,#fff);margin:24px 0 12px;padding-bottom:9px;border-bottom:1px solid var(--边框线条颜色,#222630)}
.section-title:before{content:'';display:inline-block;width:3px;height:15px;margin-right:9px;vertical-align:-2px;background:var(--主色调蓝色,#315bff);border-radius:2px}
.main-grid{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);gap:16px;align-items:stretch;min-width:0}
.main-grid>*{min-width:0}
.state-panel{min-height:280px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;border:1px solid var(--边框线条颜色,#222630);border-radius:var(--大圆角,16px);background:var(--表面卡片背景色,#141722);color:var(--次要灰色文字,#848e9c);text-align:center;padding:22px}
.state-panel p{font-size:var(--辅助副文本字号,13px)}
.state-panel.error{color:var(--主要文字颜色,#fff)}
.state-panel.error strong{color:var(--跌势红色,#f6465d)}
.state-panel button{border:1px solid var(--边框线条颜色,#222630);border-radius:var(--小圆角,6px);padding:8px 16px;background:var(--输入框背景色,#1b1e26);color:var(--主要文字颜色,#fff);cursor:pointer}
.spinner{width:30px;height:30px;border:3px solid var(--边框线条颜色,#222630);border-top-color:var(--主色调蓝色,#315bff);border-radius:50%;animation:spin .8s linear infinite}
.market-footer{margin-top:30px;padding:18px 0;border-top:1px solid var(--边框线条颜色,#222630);text-align:center;font-size:var(--最纤细徽章字号,11px);line-height:1.8;color:var(--次要灰色文字,#848e9c)}
.market-footer a{color:var(--主色调蓝色,#315bff);text-decoration:none}
.market-footer a:hover{text-decoration:underline}








@keyframes spin{to{transform:rotate(360deg)}}
@media(max-width:900px){.main-grid{grid-template-columns:minmax(0,1fr)}.market-page{padding-top:24px}}
@media(max-width:560px){.market-page{padding-top:20px;padding-bottom:28px}.market-header{align-items:flex-start;flex-direction:column;gap:10px}.market-header h1{font-size:24px}.update-time{white-space:normal}}

</style>
