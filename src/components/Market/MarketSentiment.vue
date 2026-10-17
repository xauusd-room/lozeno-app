
<template>
  <section class="panel">
    <div class="block">
      <div class="minor-title">黄金市场情绪指数</div>
      <div class="gauge-value" :class="sentClass">{{ score == null ? '--' : Math.round(score) }}</div>
      <div class="gauge-label" :class="sentClass">{{ data.sentiment?.label || '暂无数据' }}</div>
      <div class="gauge-bar">
        <i :style="{ left: `${Math.max(0, Math.min(100, Number(score) || 0))}%` }"></i>
      </div>
      <div class="gauge-labels">
        <span>极度恐惧</span>
        <span>恐惧</span>
        <span>中性</span>
        <span>贪婪</span>
        <span>极度贪婪</span>
      </div>
    </div>

    <div class="block radar-block">
      <div class="minor-title">驱动因子雷达图</div>
      <div class="radar-wrap">
        <canvas ref="canvas"></canvas>
        <div v-if="!radar.length" class="empty">暂无雷达数据</div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const props = defineProps({ data: { type: Object, required: true } })
const canvas = ref(null)
let chart

const score = computed(() => props.data.sentiment?.score)
const sentClass = computed(() => Number(score.value) <= 40 ? 'up' : Number(score.value) >= 60 ? 'down' : 'neutral')
const radar = computed(() => props.data.radar || [])

function draw() {
  if (!canvas.value) return
  chart?.destroy()
  chart = null
  if (!radar.value.length) return

  chart = new Chart(canvas.value, {
    type: 'radar',
    data: {
      labels: radar.value.map(x => x.axis),
      datasets: [{
        label: '因子支撑强度',
        data: radar.value.map(x => x.value),
        fill: true,
        backgroundColor: 'rgba(49,91,255,.18)',
        borderColor: '#4772ff',
        borderWidth: 2,
        pointBackgroundColor: '#4772ff',
        pointRadius: 3
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        r: {
          min: 0,
          max: 10,
          ticks: {
            stepSize: 2,
            color: '#64748b',
            backdropColor: 'transparent',
            font: { size: 9 }
          },
          grid: { color: 'rgba(51,65,85,.4)' },
          angleLines: { color: 'rgba(51,65,85,.4)' },
          pointLabels: { color: '#94a3b8', font: { size: 10 } }
        }
      }
    }
  })
}

watch(radar, async () => {
  await nextTick()
  draw()
}, { deep: true })

onMounted(draw)
onBeforeUnmount(() => chart?.destroy())
</script>

<style scoped>
.panel{display:flex;flex-direction:column;gap:24px;min-width:0;width:100%;padding:20px;background:var(--表面卡片背景色,#141722);border:1px solid var(--边框线条颜色,#334155);border-radius:var(--大圆角,12px)}
.block{min-width:0}
.minor-title{font-size:13px;color:var(--次要灰色文字,#94a3b8);margin-bottom:10px}
.gauge-value{font-size:44px;font-weight:850;text-align:center;line-height:1.2;font-variant-numeric:tabular-nums}
.gauge-label{text-align:center;font-size:15px;font-weight:700;margin-top:4px;overflow-wrap:anywhere}
.up{color:var(--涨势绿色,#22c55e)}
.down{color:var(--跌势红色,#ef4444)}
.neutral{color:#eab308}
.gauge-bar{height:11px;position:relative;margin-top:16px;border-radius:8px;background:linear-gradient(90deg,#22c55e,#86efac,#eab308,#fca5a5,#ef4444)}
.gauge-bar i{position:absolute;top:-4px;width:4px;height:19px;background:#fff;border-radius:2px;transform:translateX(-50%);box-shadow:0 0 6px #fff8}
.gauge-labels{display:flex;justify-content:space-between;gap:4px;margin-top:6px;font-size:9px;color:var(--次要灰色文字,#94a3b8)}
.gauge-labels span{text-align:center;min-width:0;white-space:nowrap}
.radar-wrap{position:relative;width:100%;min-width:0;height:220px}
.radar-wrap canvas{display:block;max-width:100%}
.empty{position:absolute;inset:0;display:grid;place-items:center;color:var(--次要灰色文字,#94a3b8);font-size:12px;pointer-events:none}
@media(max-width:600px){.panel{padding:16px;gap:20px}.gauge-value{font-size:38px}.gauge-labels{font-size:8px;gap:2px}.radar-wrap{height:210px}}
</style>
