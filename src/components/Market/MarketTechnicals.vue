 <template>
  <div class="tech-grid">
    <article v-for="it in items" :key="it.label" class="tech-item">
      <div class="label">{{ it.label }}</div>
      <div class="detail">
        <div class="value" :class="it.cls">{{ it.value }}</div>
        <div class="note" :class="it.cls">{{ it.note || '\u00a0' }}</div>
      </div>
    </article>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { fmt } from '../../data/marketConfig'

const props = defineProps({ data: { type: Object, required: true } })

const items = computed(() => {
  const d = props.data, t = d.technicals || {}, gold = d.prices?.gold?.value
  const has = v => v != null && Number.isFinite(Number(v))
  const pos = (p, m) => p > m ? '上方 ✓' : '下方 ✗'
  const clsPos = (p, m) => p > m ? 'up' : 'down'
  const rsiLabel = r => r > 70 ? '超买' : r < 30 ? '超卖' : '中性'
  const cross = c => c === 'golden' ? '金叉 ✓' : c === 'death' ? '死叉 ✗' : '无信号'
  const a = [
    { label: '当前价格', value: has(gold) ? '$' + fmt(gold, 2) : 'N/A', note: '', cls: 'gold' },
    { label: '50日均线', value: has(t.ma50) ? '$' + fmt(t.ma50, 2) : 'N/A', note: has(t.ma50) && has(gold) ? pos(Number(gold), Number(t.ma50)) : '', cls: has(t.ma50) && has(gold) ? clsPos(Number(gold), Number(t.ma50)) : '' },
    { label: '200日均线', value: has(t.ma200) ? '$' + fmt(t.ma200, 2) : 'N/A', note: has(t.ma200) && has(gold) ? pos(Number(gold), Number(t.ma200)) : '', cls: has(t.ma200) && has(gold) ? clsPos(Number(gold), Number(t.ma200)) : '' },
    { label: 'RSI（14）', value: has(t.rsi14) ? fmt(t.rsi14, 1) : 'N/A', note: has(t.rsi14) ? rsiLabel(Number(t.rsi14)) : '', cls: !has(t.rsi14) ? '' : Number(t.rsi14) > 70 ? 'down' : Number(t.rsi14) < 30 ? 'up' : 'neutral' },
    { label: '20日波动率', value: has(d.volatility?.current20d) ? fmt(d.volatility.current20d, 1) + '%' : 'N/A', note: d.volatility?.level === 'low' ? '低' : d.volatility?.level === 'high' ? '高' : '中', cls: d.volatility?.level === 'low' ? 'up' : d.volatility?.level === 'high' ? 'down' : 'neutral' },
    { label: '支撑位', value: (t.support || []).length ? t.support.map(x => '$' + fmt(x, 2)).join(' / ') : 'N/A', note: '', cls: '' },
    { label: '阻力位', value: (t.resistance || []).length ? t.resistance.map(x => '$' + fmt(x, 2)).join(' / ') : 'N/A', note: '', cls: '' },
    { label: 'MA 交叉', value: cross(t.maCrossover), note: '', cls: t.maCrossover === 'golden' ? 'up' : t.maCrossover === 'death' ? 'down' : 'neutral' },
    { label: '利率-金价背离', value: has(d.divergence?.zScore) ? fmt(d.divergence.zScore, 2) : 'N/A', note: d.divergence?.signal === 'overbought' ? '超买' : d.divergence?.signal === 'oversold' ? '超卖' : '正常', cls: d.divergence?.signal === 'overbought' ? 'down' : d.divergence?.signal === 'oversold' ? 'up' : 'neutral' }
  ]
  const yc = d.yieldCurve
  if (has(yc?.current)) a.push({ label: '收益率曲线', value: fmt(yc.current, 2) + '%', note: yc.inverted ? '倒挂' : yc.signal === 'steepening' ? '急陡化' : yc.signal === 'flattening' ? '平坦化' : '正常', cls: yc.inverted ? 'down' : 'up' })
  return a
})
</script>

<style scoped>

.tech-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px;width:100%;min-width:0;align-items:stretch}
.tech-item{width:100%;min-width:0;display:flex;flex-direction:column;align-items:center;justify-content:flex-start;text-align:center;padding:15px 8px;background:var(--表面卡片背景色,#141722);border:1px solid var(--边框线条颜色,#222630);border-radius:var(--中圆角,10px)}
.label{width:100%;min-width:0;font-size:12px;line-height:18px;font-weight:500;color:var(--次要灰色文字,#848e9c);white-space:normal;overflow-wrap:anywhere}
.detail{width:100%;min-width:0;display:flex;flex-direction:column;align-items:center;gap:4px;margin-top:8px}
.value{width:100%;min-width:0;font-size:16px;line-height:22px;font-weight:700;overflow-wrap:anywhere;word-break:break-word;font-variant-numeric:tabular-nums}
.note{min-height:16px;font-size:12px;line-height:16px;font-weight:500;overflow-wrap:anywhere}
.gold{color:#f0c040}.up{color:var(--涨势绿色,#0ecb81)}.down{color:var(--跌势红色,#f6465d)}.neutral{color:#eab308}
@media(max-width:560px){.tech-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.tech-item{padding:12px 6px}}

</style>