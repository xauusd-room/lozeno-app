
<template>
  <main class="page page-container">
    <h1>发现优质 EA 自动交易产品</h1>
    <p class="page-subtitle">浏览 EA 排名、探索实用插件，寻找适合自己的自动交易工具。</p>

    <div class="ea-card-grid">
      <EaCard
        v-for="item in eaList"
        :key="item.id"
        v-bind="item"
      />
    </div>
  </main>
</template>

<script setup>
import { computed } from 'vue'
import EaCard from '../components/EaCard.vue'
import { eaProducts } from '../data/eaProducts.js'

const eaList = computed(() =>
  Object.values(eaProducts).map(product => ({
    id: product.id,
    title: product.name,
    tag: product.type,
    platform: product.platformTag,
    platformClass: {
      MT4: 'text-mt4',
      MT5: 'text-mt5',
      AI: 'text-ai'
    }[product.platformTag] || '',
    rate: Number(String(product.ret).replace('%', '').replace('+', '')),
    installs: product.installs ?? 0,
    winRate: Number(String(product.win).replace('%', '').replace('+', ''))
  }))
)
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
