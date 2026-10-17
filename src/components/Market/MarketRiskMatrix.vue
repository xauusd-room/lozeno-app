
<template>
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>投资标的</th>
          <th>风险等级</th>
          <th>核心关注因子</th>
          <th>风险信号</th>
          <th>机会信号</th>
          <th>建议仓位</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="[key, v] in rows" :key="key">
          <td class="name">{{ names[key] || key }}</td>
          <td><span class="risk" :class="`risk-${v.risk}`">{{ riskLabel(v.risk) }}</span></td>
          <td>{{ (v.keyFactors || []).join(' · ') || '—' }}</td>
          <td>
            <span v-for="t in v.riskSignals || []" :key="t" class="tag risk-tag">{{ t }}</span>
            <span v-if="!(v.riskSignals || []).length">—</span>
          </td>
          <td>
            <span v-for="t in v.oppSignals || []" :key="t" class="tag opp-tag">{{ t }}</span>
            <span v-if="!(v.oppSignals || []).length">—</span>
          </td>
          <td class="position">{{ v.position || '—' }}</td>
        </tr>
        <tr v-if="!rows.length">
          <td colspan="6" class="empty">暂无风险矩阵数据</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ data: { type: Object, required: true } })
const rows = computed(() => Object.entries(props.data.riskMatrix || {}))
const names = {
  physical: '实物黄金',
  etf: '黄金 ETF（GLD）',
  futures: '黄金期货',
  miners: '金矿股（GDX）'
}
const riskLabel = r => r === 'low' ? '低' : r === 'high' ? '高' : '中'
</script>

<style scoped>
.table-wrap{width:100%;min-width:0;overflow-x:auto;overscroll-behavior-x:contain;border:1px solid var(--边框线条颜色,#334155);border-radius:var(--大圆角,12px)}
table{width:100%;min-width:760px;border-collapse:collapse;font-size:12px;background:var(--表面卡片背景色,#141722)}
th{background:var(--输入框背景色,#16213e);padding:12px;text-align:left;font-weight:700;color:var(--主要文字颜色,#e2e8f0);white-space:nowrap}
td{padding:12px;border-top:1px solid var(--边框线条颜色,#334155);vertical-align:top;line-height:1.6;color:var(--次要灰色文字,#94a3b8)}
tbody tr:hover td{background:rgba(49,91,255,.04)}
.name,.position{font-weight:650;color:var(--主要文字颜色,#e2e8f0);white-space:nowrap}
.risk{display:inline-block;padding:3px 9px;border-radius:12px;font-size:11px;font-weight:650;white-space:nowrap}
.risk-low{background:#22c55e20;color:#22c55e}
.risk-medium{background:#eab30820;color:#eab308}
.risk-high{background:#ef444420;color:#ef4444}
.tag{display:inline-block;margin:1px 3px 3px 0;padding:2px 6px;border-radius:4px;font-size:10px;overflow-wrap:anywhere}
.risk-tag{background:#ef444418;color:#fca5a5}
.opp-tag{background:#22c55e18;color:#86efac}
.empty{text-align:center}
@media(max-width:560px){th,td{padding:10px}}
</style>
