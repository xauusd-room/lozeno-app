
<template>
  <main class="page page-container">
    <h1>发现优质 EA 自动交易产品</h1>
    <p class="page-subtitle">浏览 EA 排名、探索实用插件，寻找适合自己的自动交易工具。</p>

    <div class="ea-card-grid">
      <EaCard v-for="item in eaList" :key="item.id" v-bind="item" />
    </div>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import EaCard from '../components/EaCard.vue'

const eaList = ref([
  { id: 1, title: 'TrendMaster Pro', tag: '趋势追踪', platform: 'MT5', platformClass: 'text-mt5', rate: 24.5, installs: 23, winRate: 48.2 },
  { id: 2, title: 'GridScalper X', tag: '网格震荡', platform: 'MT4', platformClass: 'text-mt4', rate: 112.8, installs: 332, winRate: 91.45 },
  { id: 3, title: 'NeuralArbitrage', tag: '高频套利', platform: 'AI', platformClass: 'text-ai', rate: -1.2, installs: 169, winRate: 54.1 }
])
</script>

<style scoped>
.page{min-width:0;padding-top:32px;padding-bottom:32px}
h1{font-size:var(--页面大标题字号);font-weight:800;margin-bottom:12px}
.page-subtitle{color:var(--次要灰色文字);font-size:var(--正文常规字号);margin-bottom:32px}
.ea-card-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}
@media(max-width:1024px){.ea-card-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:680px){.ea-card-grid{grid-template-columns:minmax(0,1fr)}}
@media(max-width:560px){.page{padding-top:20px;padding-bottom:24px}h1{font-size:26px}.page-subtitle{margin-bottom:24px}}
</style>
