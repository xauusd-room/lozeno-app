<template>
  <section id="performance" class="section">
    <div class="section-heading"><div><h2>策略表现</h2><p>通过收益、风险与交易统计了解策略历史表现。</p></div><span>示例数据 · 最近 {{ range === '12M' ? '12' : range === '6M' ? '6' : '3' }} 个月</span></div>
    <div class="metrics">
      <div class="metric"><label>累计收益率</label><strong :class="positive ? 'positive' : 'negative'">{{ product.ret }}</strong><small>历史统计示例</small></div>
      <div class="metric"><label>最大回撤</label><strong>{{ product.dd }}</strong><small>历史统计示例</small></div>
      <div class="metric"><label>胜率</label><strong>{{ product.win }}</strong><small>盈利交易 / 总交易</small></div>
      <div class="metric"><label>盈利因子</label><strong>{{ product.pf }}</strong><small>总盈利 / 总亏损绝对值</small></div>
    </div>
    <div class="performance-panel">
      <div class="chart-head"><strong>{{ product.name }} · 账户净值曲线</strong><div class="tabs"><button v-for="item in ['12M','6M','3M']" :key="item" :class="{active:range===item}" @click="range=item">{{ item==='12M'?'12个月':item==='6M'?'6个月':'3个月' }}</button></div></div>
      <div class="chart"><svg viewBox="0 0 760 230" preserveAspectRatio="none" role="img" aria-label="示意净值曲线"><defs><linearGradient id="chartFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#6387ff" stop-opacity=".25"/><stop offset="100%" stop-color="#6387ff" stop-opacity="0"/></linearGradient></defs><path class="gridline" d="M0 25H760 M0 70H760 M0 115H760 M0 160H760 M0 205H760"/><path class="area" d="M0 190 L30 177 L60 184 L90 157 L120 169 L150 140 L180 149 L210 126 L240 137 L270 112 L300 124 L330 94 L360 105 L390 87 L420 101 L450 68 L480 81 L510 58 L540 70 L570 48 L600 59 L630 34 L660 46 L690 25 L720 34 L760 16 L760 220 L0 220 Z"/><path class="line" d="M0 190 L30 177 L60 184 L90 157 L120 169 L150 140 L180 149 L210 126 L240 137 L270 112 L300 124 L330 94 L360 105 L390 87 L420 101 L450 68 L480 81 L510 58 L540 70 L570 48 L600 59 L630 34 L660 46 L690 25 L720 34 L760 16"/></svg></div>
      <div class="legend"><i></i>账户净值 <span>曲线为布局示意，正式上线应替换为经验证的回测或实盘数据。</span></div>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
const props = defineProps({ product: { type: Object, required: true } })
const range = ref('12M')
const positive = computed(() => !String(props.product.ret).startsWith('-'))
</script>

<style scoped>
.section{margin-top:42px}.section-heading{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;margin-bottom:18px}
h2{font-size:22px;font-weight:750}.section-heading p{margin-top:7px;color:var(--次要灰色文字);font-size:13px;line-height:1.7}.section-heading>span{font-size:12px;color:var(--次要灰色文字)}
.metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-bottom:16px}
.metric,.performance-panel{background:var(--表面卡片背景色);border:1px solid var(--边框线条颜色);border-radius:var(--大圆角)}
.metric{padding:19px 20px;min-width:0}.metric label,.metric small{display:block;color:var(--次要灰色文字);font-size:12px}.metric strong{display:block;margin-top:12px;font-size:25px;font-weight:750;overflow-wrap:anywhere}.metric small{margin-top:7px;font-size:11px}
.positive{color:var(--涨势绿色)}.negative{color:var(--跌势红色)}
.performance-panel{padding:22px 24px}.chart-head{display:flex;justify-content:space-between;align-items:center;gap:14px;margin-bottom:16px;font-size:14px}
.tabs{display:flex;gap:5px}.tabs button{padding:6px 10px;border:1px solid transparent;border-radius:6px;background:transparent;color:var(--次要灰色文字);font-size:11px;cursor:pointer}.tabs button.active{background:#202b4d;border-color:#2d4078;color:#a8bbff}
.chart{width:100%;height:245px}.chart svg{width:100%;height:100%;overflow:visible}.gridline{stroke:#293041;stroke-width:1;stroke-dasharray:3 5}.line{stroke:#6f8cff;stroke-width:2.4;fill:none;stroke-linecap:round;stroke-linejoin:round}.area{fill:url(#chartFill)}
.legend{display:flex;align-items:center;gap:8px;margin-top:12px;color:var(--次要灰色文字);font-size:11px}.legend i{width:7px;height:7px;border-radius:50%;background:#6f8cff;flex-shrink:0}.legend span{margin-left:auto;text-align:right;max-width:58%;line-height:1.6}
@media(max-width:700px){.section{margin-top:32px}.section-heading{align-items:flex-start;flex-direction:column;gap:6px}h2{font-size:20px}.metrics{grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}.metric{padding:15px}.metric strong{font-size:22px}.performance-panel{padding:16px 12px}.chart{height:205px}.legend span{max-width:62%}.chart-head{align-items:flex-start;flex-direction:column}}
</style>