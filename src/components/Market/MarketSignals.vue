
<template>
  <div class="signals-grid">
    <section class="signal-panel">
      <h3 class="up">▲ 利好信号 <span>{{ bullish.length }}</span></h3>
      <div v-if="!bullish.length" class="empty">暂无明显利好信号</div>
      <article v-for="(s, i) in bullish" :key="`${s.title}-${i}`" class="signal-item">
        <div class="signal-heading">
          <span class="strength up">{{ dots(s.strength) }}</span>
          <strong>{{ s.title }}</strong>
        </div>
        <p>{{ s.detail }}</p>
      </article>
    </section>

    <section class="signal-panel">
      <h3 class="down">▼ 利空信号 <span>{{ bearish.length }}</span></h3>
      <div v-if="!bearish.length" class="empty">暂无明显利空信号</div>
      <article v-for="(s, i) in bearish" :key="`${s.title}-${i}`" class="signal-item">
        <div class="signal-heading">
          <span class="strength down">{{ dots(s.strength) }}</span>
          <strong>{{ s.title }}</strong>
        </div>
        <p>{{ s.detail }}</p>
      </article>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ data: { type: Object, required: true } })
const bullish = computed(() => props.data.signals?.bullish || [])
const bearish = computed(() => props.data.signals?.bearish || [])
const dots = n => '●'.repeat(Math.max(0, Math.min(5, Number(n) || 0))) + '○'.repeat(Math.max(0, 5 - Math.min(5, Number(n) || 0)))
</script>

<style scoped>
.signals-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;min-width:0}
.signal-panel{min-width:0;padding:18px;background:var(--表面卡片背景色,#141722);border:1px solid var(--边框线条颜色,#334155);border-radius:var(--大圆角,12px)}
h3{font-size:14px;margin-bottom:10px}
h3 span{font-weight:500;font-size:12px;color:var(--次要灰色文字,#94a3b8);margin-left:5px}
.signal-item{min-width:0;padding:12px 0;border-bottom:1px solid var(--边框线条颜色,#334155)}
.signal-item:last-child{border-bottom:0}
.signal-heading{display:flex;align-items:flex-start;gap:8px;font-size:13px;min-width:0}
.signal-heading strong{min-width:0;font-weight:650;overflow-wrap:anywhere}
.strength{flex-shrink:0;font-size:11px;letter-spacing:1px;white-space:nowrap}
.signal-item p,.empty{margin-top:5px;font-size:12px;line-height:1.6;color:var(--次要灰色文字,#94a3b8);overflow-wrap:anywhere}
.up{color:var(--涨势绿色,#22c55e)}
.down{color:var(--跌势红色,#ef4444)}
@media(max-width:700px){.signals-grid{grid-template-columns:minmax(0,1fr)}}
@media(max-width:560px){.signal-panel{padding:16px}}
</style>
