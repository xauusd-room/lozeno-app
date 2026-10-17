
<template>
  <section class="summary-grid">
    <article v-for="c in cards" :key="c.label" class="summary-card" @click="expanded = expanded === c.label ? '' : c.label">
      <div class="label">{{ c.label }}</div>
      <div class="value" :class="c.cls">{{ c.value }}</div>
      <div class="sub" :class="c.cls">{{ c.sub }}</div>
      <div class="detail" :class="{ open: expanded === c.label }">{{ c.detail }}</div>
    </article>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import { fmt } from '../../data/marketConfig'

const props = defineProps({ data: { type: Object, required: true } })
const expanded = ref('')

const cards = computed(() => {
  const d = props.data, p = d.prices || {}, gold = p.gold || {}, ry = d.coreFactors?.realYield || {}, dx = d.coreFactors?.dollarIndex || {}, s = d.sentiment || {}, v = d.volatility || {}, sig = d.overallSignal || {}, sgr = d.silverGoldRatio || {}, gdx = d.gdx || {}
  const inv = t => t === 'declining' ? 'up' : t === 'rising' ? 'down' : 'neutral'
  const trend = t => t === 'declining' ? '↓ 下行' : t === 'rising' ? '↑ 上行' : '→ 持平'

  return [
    { label: '黄金价格', value: `$${fmt(gold.value, 2)}`, sub: `${Number(gold.changePct1d) > 0 ? '↑ +' : '↓ '}${fmt(gold.changePct1d, 2)}%`, cls: Number(gold.changePct1d) >= 0 ? 'gold up' : 'gold down', detail: '黄金期货参考价格及单日涨跌幅。不同数据源的期货价格与现货报价可能存在差异。' },
    { label: '10Y 实际利率', value: ry.current == null ? 'N/A' : `${fmt(ry.current, 2)}%`, sub: trend(ry.trend), cls: inv(ry.trend), detail: '10年期 TIPS 实际收益率。实际利率下行通常降低持有黄金的机会成本。' },
    { label: '美元指数', value: dx.current == null ? 'N/A' : fmt(dx.current, 2), sub: `${trend(dx.trend)} · 20日 ROC ${dx.roc20d == null ? 'N/A' : fmt(dx.roc20d, 1) + '%'}`, cls: inv(dx.trend), detail: '美元强弱指标。美元走弱通常对美元计价黄金形成支撑，但并非稳定的一对一关系。' },
    { label: '市场情绪', value: s.score == null ? 'N/A' : fmt(s.score, 0), sub: s.label || '暂无标签', cls: Number(s.score) <= 40 ? 'up' : Number(s.score) >= 60 ? 'down' : 'neutral', detail: '综合情绪指数，具体含义取决于数据生成程序所采用的因子和权重。' },
    { label: '综合信号', value: sig.label || 'N/A', sub: `多头 ${sig.bullScore ?? '--'} / 空头 ${sig.bearScore ?? '--'}`, cls: sig.direction === 'bullish' ? 'up' : sig.direction === 'bearish' ? 'down' : 'neutral', detail: '展示数据文件中的综合信号及多空分数，不代表收益保证。' },
    { label: '20日波动率', value: v.current20d == null ? 'N/A' : `${fmt(v.current20d, 1)}%`, sub: v.level === 'low' ? '低' : v.level === 'high' ? '高' : '中', cls: v.level === 'low' ? 'up' : v.level === 'high' ? 'down' : 'neutral', detail: '20日年化波动率。波动率越高，价格波动和仓位风险通常越大。' },
    { label: '金银比', value: sgr.current == null ? 'N/A' : fmt(sgr.current, 2), sub: sgr.signal === 'extreme_high' ? '极端偏高' : sgr.signal === 'extreme_low' ? '偏低' : '正常', cls: sgr.signal === 'extreme_high' ? 'down' : sgr.signal === 'extreme_low' ? 'up' : 'neutral', detail: `金价与银价之比。白银参考价格：$${fmt(sgr.silver_price, 2)}。` },
    { label: 'GDX 金矿 ETF', value: gdx.current == null ? 'N/A' : `$${fmt(gdx.current, 2)}`, sub: gdx.changePct1d == null ? '日涨跌 N/A' : `${gdx.changePct1d >= 0 ? '↑ +' : '↓ '}${fmt(gdx.changePct1d, 2)}%`, cls: Number(gdx.changePct1d) >= 0 ? 'up' : 'down', detail: `20日动量：${gdx.roc20d == null ? 'N/A' : fmt(gdx.roc20d, 1) + '%'}。金矿股不等同于黄金本身。` }
  ]
})
</script>

<style scoped>
.summary-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));grid-auto-flow:row;gap:14px;width:100%;min-width:0}
.summary-card{min-width:0;padding:16px 18px;background:var(--表面卡片背景色,#141722);border:1px solid var(--边框线条颜色,#334155);border-radius:var(--大圆角,12px);cursor:pointer;transition:transform .18s,border-color .18s}
.summary-card:hover{transform:translateY(-2px);border-color:var(--主色调蓝色,#315bff)}
.label{font-size:12px;color:var(--次要灰色文字,#94a3b8);margin-bottom:8px;letter-spacing:.3px}
.value{font-size:24px;font-weight:750;line-height:1.35;overflow-wrap:anywhere;font-variant-numeric:tabular-nums}
.sub{font-size:12px;margin-top:7px;line-height:1.5;overflow-wrap:anywhere}
.detail{max-height:0;overflow:hidden;color:var(--次要灰色文字,#94a3b8);font-size:12px;line-height:1.6;transition:max-height .25s,margin-top .25s}
.detail.open{max-height:100px;margin-top:12px}
.gold{color:#f0c040}.up{color:var(--涨势绿色,#22c55e)}.down{color:var(--跌势红色,#ef4444)}.neutral{color:#eab308}
@media(max-width:900px){.summary-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:560px){.summary-grid{gap:10px}.summary-card{padding:13px 12px}.value{font-size:20px}}
</style>
