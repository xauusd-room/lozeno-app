
<template>
  <div class="outlook-grid">
    <article v-for="p in periods" :key="p.key" class="outlook-card">
      <h3>{{ p.title }}</h3>
      <div class="direction" :class="p.data?.direction">{{ icon(p.data?.direction) }} {{ label(p.data?.direction) }}</div>
      <div class="confidence">置信度：{{ p.data?.confidence ?? 'N/A' }}</div>
      <ul>
        <li v-for="(f, i) in p.data?.factors || []" :key="i">{{ f }}</li>
      </ul>
      <div v-if="p.data?.support?.length || p.data?.resistance?.length" class="levels">
        <span v-if="p.data?.support?.length">支撑：{{ p.data.support.map(x => '$' + fmt(x)).join(' / ') }}</span>
        <span v-if="p.data?.resistance?.length">阻力：{{ p.data.resistance.map(x => '$' + fmt(x)).join(' / ') }}</span>
      </div>
      <p class="summary">{{ p.data?.summary || '暂无走势说明' }}</p>
    </article>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { fmt } from '../../data/marketConfig'

const props = defineProps({ data: { type: Object, required: true } })
const periods = computed(() => [
  { key: 'shortTerm', title: '短期（1–4周）', data: props.data.outlook?.shortTerm },
  { key: 'midTerm', title: '中期（1–6个月）', data: props.data.outlook?.midTerm },
  { key: 'longTerm', title: '长期（1年以上）', data: props.data.outlook?.longTerm }
])
const icon = d => d === 'bullish' ? '↑' : d === 'bearish' ? '↓' : '→'
const label = d => d === 'bullish' ? '看多' : d === 'bearish' ? '看空' : '中性'
</script>

<style scoped>

.outlook-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;min-width:0;align-items:stretch}
.outlook-card{min-width:0;display:flex;flex-direction:column;padding:18px;background:var(--表面卡片背景色,#141722);border:1px solid var(--边框线条颜色,#222630);border-radius:var(--大圆角,16px)}
h3{font-size:13px;font-weight:650;color:var(--次要灰色文字,#848e9c);margin-bottom:12px}
.direction{font-size:25px;font-weight:800;overflow-wrap:anywhere}
.direction.bullish{color:var(--涨势绿色,#0ecb81)}
.direction.bearish{color:var(--跌势红色,#f6465d)}
.direction.neutral{color:#eab308}
.confidence{margin-top:4px;font-size:11px;color:var(--次要灰色文字,#848e9c);overflow-wrap:anywhere}
ul{margin-top:12px;list-style:none;font-size:12px;color:var(--次要灰色文字,#848e9c)}
li{margin:5px 0;line-height:1.5;overflow-wrap:anywhere}
li:before{content:'› ';color:var(--主色调蓝色,#315bff)}
.levels{display:flex;flex-direction:row;flex-wrap:wrap;align-items:center;gap:8px 16px;margin-top:14px;margin-bottom:18px;font-size:11px;line-height:1.8;color:var(--次要灰色文字,#848e9c);overflow-wrap:anywhere}
.levels span{white-space:nowrap}
.summary{margin-top:auto;padding:12px;background:var(--输入框背景色,#1b1e26);border-radius:var(--小圆角,6px);font-size:12px;line-height:1.8;overflow-wrap:anywhere}
@media(max-width:900px){.outlook-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.outlook-card:last-child{grid-column:1/-1}}
@media(max-width:600px){.outlook-grid{grid-template-columns:minmax(0,1fr)}.outlook-card:last-child{grid-column:auto}.outlook-card{padding:16px}}

</style>
