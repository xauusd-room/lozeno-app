
<template>
  <section class="panel">
    <div class="tabs">
      <button v-for="(c, i) in CHART_CONFIGS" :key="c.label" :class="{ active: tab === i }" @click="tab = i">{{ c.label }}</button>
    </div>
    <div class="chart-wrap">
      <canvas ref="canvas"></canvas>
      <div v-if="!hasValues" class="chart-empty">当前图表暂无可用历史数据</div>
    </div>
    <div class="ranges">
      <button v-for="r in TIME_RANGES" :key="r.days" :class="{ active: days === r.days }" @click="days = r.days">{{ r.label }}</button>
    </div>
  </section>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { Chart, registerables } from 'chart.js'
import { CHART_CONFIGS, TIME_RANGES, KEY_LABELS } from '../../data/marketConfig'

Chart.register(...registerables)

const props = defineProps({ data: { type: Object, required: true } })
const canvas = ref(null)
const tab = ref(0)
const days = ref(365)
let chart

const config = computed(() => CHART_CONFIGS[tab.value])
const hasValues = computed(() => config.value.keys.some(k => (props.data.history?.[k] || []).length))

function draw() {
  if (!canvas.value) return
  chart?.destroy()

  const cfg = config.value
  const all = new Set()
  const slicedByKey = {}

  cfg.keys.forEach(k => {
    const a = (props.data.history?.[k] || []).slice(-days.value)
    slicedByKey[k] = a
    a.forEach(x => all.add(x.date))
  })

  const dates = [...all].sort()
  const datasets = cfg.keys.map((k, i) => {
    const map = Object.fromEntries((slicedByKey[k] || []).map(x => [x.date, x.value]))
    return {
      label: KEY_LABELS[k] || k,
      data: dates.map(d => map[d] ?? null),
      borderColor: cfg.colors[i],
      backgroundColor: cfg.colors[i] + '20',
      borderWidth: i === 0 ? 2 : 1.5,
      pointRadius: 0,
      tension: 0.25,
      fill: cfg.keys.length === 1,
      yAxisID: cfg.singleAxis ? 'y' : i === 0 ? 'y' : 'y1',
      borderDash: cfg.singleAxis && i > 0 ? [6, 4] : [],
      spanGaps: true
    }
  })

  const scales = {
    x: {
      ticks: { color: '#94a3b8', maxTicksLimit: 8, font: { size: 10 } },
      grid: { color: 'rgba(51,65,85,.3)' }
    },
    y: {
      position: 'left',
      reverse: !!cfg.invertLeft,
      ticks: { color: cfg.colors[0], font: { size: 10 } },
      grid: { color: 'rgba(51,65,85,.3)' }
    }
  }

  if (cfg.keys.length > 1 && !cfg.singleAxis) {
    scales.y1 = {
      position: 'right',
      ticks: { color: cfg.colors[1], font: { size: 10 } },
      grid: { drawOnChartArea: false }
    }
  }

  chart = new Chart(canvas.value, {
    type: 'line',
    data: { labels: dates, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: {
          display: true,
          labels: { color: '#94a3b8', font: { size: 11 }, boxWidth: 18 }
        },
        tooltip: {
          backgroundColor: 'rgba(15,15,26,.96)',
          titleColor: '#f0c040',
          bodyColor: '#e2e8f0',
          borderColor: '#334155',
          borderWidth: 1
        }
      },
      scales
    }
  })
}

watch([tab, days, () => props.data], async () => {
  await nextTick()
  draw()
}, { deep: false })

onMounted(draw)
onBeforeUnmount(() => chart?.destroy())
</script>

<style scoped>
.panel{min-width:0;width:100%;padding:18px;background:var(--表面卡片背景色,#141722);border:1px solid var(--边框线条颜色,#334155);border-radius:var(--大圆角,12px)}
.tabs{display:flex;gap:5px;flex-wrap:wrap;margin-bottom:14px;min-width:0}
.tabs button,.ranges button{flex-shrink:0;border:1px solid var(--边框线条颜色,#334155);background:transparent;color:var(--次要灰色文字,#94a3b8);cursor:pointer;border-radius:6px}
.tabs button{padding:7px 10px;font-size:12px}
.tabs button:hover,.tabs button.active{border-color:#c9a020;color:var(--主要文字颜色,#e2e8f0)}
.tabs button.active{background:#c9a020;color:#111827;font-weight:700}
.chart-wrap{position:relative;width:100%;min-width:0;height:340px}
.chart-wrap canvas{display:block;max-width:100%}
.chart-empty{position:absolute;inset:0;display:grid;place-items:center;color:var(--次要灰色文字,#94a3b8);font-size:12px;pointer-events:none}
.ranges{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:5px;margin-top:12px}
.ranges button{padding:4px 10px;font-size:11px}
.ranges button.active,.ranges button:hover{background:var(--输入框背景色,#16213e);border-color:#c9a020;color:var(--主要文字颜色,#e2e8f0)}
@media(max-width:600px){.panel{padding:12px}.chart-wrap{height:280px}.tabs button{font-size:11px;padding:6px 8px}}
</style>
