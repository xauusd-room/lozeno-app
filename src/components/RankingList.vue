<template>
  <section class="rank-card">
    <table class="rank-table">
      <thead><tr><th>排名</th><th>策略机器人名称</th><th>历史总收益率</th><th>智能高光胜率</th><th>最大风控回撤</th><th>安全运行时间</th><th>状态</th></tr></thead>
      <tbody><tr v-for="ea in rankings" :key="ea.rank"><td><div class="num-tag">{{ ea.rank }}</div></td><td><div class="ea-info"><div class="ea-logo">{{ ea.logo }}</div><div><div class="ea-name">{{ ea.name }}</div><div class="ea-type">{{ ea.type }}</div></div></div></td><td><span class="txt-green">{{ ea.returnRate }}</span></td><td><span class="txt-bold">{{ ea.winRate }}</span></td><td><span class="txt-bold">{{ ea.drawdown }}</span></td><td>{{ ea.days }} 天</td><td><span class="active-badge">运行中</span></td></tr></tbody>
    </table>
  </section>
</template>
<script setup>
const rankings=[
{rank:1,logo:'G',name:'黄金超频波段王_EA',type:'XAUUSD 专属 / 高频剥头皮',returnRate:'+142.30%',winRate:'87.4%',drawdown:'3.8%',days:185},
{rank:2,logo:'T',name:'LOZENO_趋势追踪 3号',type:'多币种复合 / 趋势突破',returnRate:'+89.12%',winRate:'79.5%',drawdown:'5.2%',days:124},
{rank:3,logo:'M',name:'马丁对冲稳健守护者',type:'主流外汇 / 智能网格对冲',returnRate:'+45.71%',winRate:'71.2%',drawdown:'8.9%',days:310},
{rank:4,logo:'A',name:'AI 大数据多策略复合体',type:'全市场覆盖 / 机器学习',returnRate:'+31.20%',winRate:'68.8%',drawdown:'2.1%',days:45}
]
</script>
<style scoped>
.rank-card{background:#141722;border:1px solid #222630;border-radius:16px;padding:16px;overflow-x:auto}
.rank-table{width:100%;min-width:760px;border-collapse:collapse;text-align:left;font-size:14px;line-height:1.65}
.rank-table th{color:#848e9c;font-weight:600;padding:14px 16px;border-bottom:1px solid #222630;font-size:11px;white-space:nowrap}
.rank-table td{padding:16px;border-bottom:1px solid #222630;vertical-align:middle;white-space:nowrap}
.rank-table tbody tr:last-child td{border-bottom:0}
.rank-table tbody tr:hover{background:rgba(255,255,255,.02)}
.num-tag{font-weight:800;color:#848e9c;width:24px}
.rank-table tbody tr:nth-child(1) .num-tag{color:#ffd700}
.rank-table tbody tr:nth-child(2) .num-tag{color:#c0c0c0}
.rank-table tbody tr:nth-child(3) .num-tag{color:#cd7f32}
.ea-info{display:flex;align-items:center;gap:12px}
.ea-logo{width:32px;height:32px;flex:0 0 32px;background:#1b1e26;border:1px solid #222630;border-radius:8px;display:flex;align-items:center;justify-content:center;font-weight:800;color:#315bff}
.ea-name{font-weight:750;margin-bottom:2px}
.ea-type{font-size:11px;color:#848e9c}
.txt-green{color:#00c853;font-weight:800}
.txt-bold{font-weight:700}
.active-badge{display:inline-block;padding:4px 8px;background:rgba(0,200,83,.1);color:#00c853;border-radius:6px;font-size:12px;font-weight:700}
</style>