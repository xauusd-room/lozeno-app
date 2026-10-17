<template>
  <section class="section">
    <div class="section-heading"><div><h2>策略介绍</h2><p>了解交易逻辑、适用环境与运行要求，再决定是否购买。</p></div></div>
    <div class="intro-grid">
      <article class="card">
        <h3>{{ product.type }} · 策略逻辑</h3>
        <p class="intro-text">{{ product.desc }} 策略表现会受到交易品种、周期、点差、滑点、服务器环境及参数设置影响。建议先使用历史数据进行回测，再在模拟账户中验证执行效果。</p>
        <div class="features">
          <div v-for="item in features" :key="item.title" class="feature"><div class="feature-icon"><svg viewBox="0 0 24 24"><path :d="item.path"/></svg></div><strong>{{ item.title }}</strong><p>{{ item.desc }}</p></div>
        </div>
        <div class="risk">风险提示：历史回测结果不代表未来收益。自动交易可能产生亏损，极端行情、点差扩大、滑点和连接中断均可能影响实际结果。请勿仅凭单一收益指标判断策略质量。</div>
      </article>
      <aside class="card"><h3>产品规格</h3><div class="specs"><div v-for="item in specs" :key="item[0]" class="spec"><span>{{ item[0] }}</span><span>{{ item[1] }}</span></div></div></aside>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ product: { type: Object, required: true } })
const features = [
  { title: '策略逻辑', desc: '围绕预设条件筛选潜在交易机会。', path: 'M3 17 9 11l4 4 8-9 M15 6h6v6' },
  { title: '风险参数', desc: '结合止损、止盈及订单风险限制。', path: 'M12 3 20 7v5c0 5-3.5 7.5-8 9-4.5-1.5-8-4-8-9V7z M9 12l2 2 4-4' },
  { title: '历史验证', desc: '建议结合回测和模拟交易评估。', path: 'M4 19V5m0 14h17 M7 15l4-4 3 2 5-7' },
  { title: '参数配置', desc: '按账户环境和风险偏好调整参数。', path: 'M3 4h18v16H3z M7 8h10 M7 12h6 M7 16h8' }
]
const specs = computed(() => [['产品类型', '自动交易 EA'], ['交易平台', props.product.platform], ['建议周期', props.product.period], ['支持品种', props.product.market], ['运行方式', '需保持终端运行'], ['最低资金', '需按回测与风险评估'], ['授权类型', props.product.license], ['技术支持', '产品购买后提供']])
</script>

<style scoped>
.section{margin-top:42px}.section-heading{margin-bottom:18px}h2{font-size:22px;font-weight:750}.section-heading p{margin-top:7px;color:var(--次要灰色文字);font-size:13px;line-height:1.7}
.intro-grid{display:grid;grid-template-columns:minmax(0,1.3fr) minmax(280px,.7fr);gap:16px}.card{min-width:0;padding:24px;background:var(--表面卡片背景色);border:1px solid var(--边框线条颜色);border-radius:var(--大圆角)}h3{font-size:15px;margin-bottom:14px}
.intro-text{font-size:13px;color:#bdc5d3;line-height:1.95}.features{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-top:22px}
.feature{padding:14px;background:var(--输入框背景色);border-radius:var(--中圆角)}.feature-icon{color:#6f8cff;margin-bottom:9px}.feature-icon svg{width:20px;height:20px;stroke:currentColor;fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}.feature strong{font-size:12px}.feature p{margin-top:6px;font-size:11px;line-height:1.7;color:var(--次要灰色文字)}
.risk{margin-top:16px;padding:13px 15px;background:#1b1d27;border:1px solid #34303a;border-radius:9px;color:#aeb6c5;font-size:11px;line-height:1.8}
.spec{display:flex;justify-content:space-between;gap:14px;padding:13px 0;border-bottom:1px solid var(--边框线条颜色);font-size:12px}.spec:last-child{border-bottom:0}.spec span:first-child{color:var(--次要灰色文字)}.spec span:last-child{text-align:right;color:#e0e5ee}
@media(max-width:900px){.intro-grid{grid-template-columns:1fr}}@media(max-width:700px){.section{margin-top:32px}h2{font-size:20px}.card{padding:18px}.features{gap:9px}.feature{padding:12px}}
</style>