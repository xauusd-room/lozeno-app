<template>
  <div class="breadcrumb"><router-link to="/">首页</router-link><span>/</span><router-link to="/ranking">EA排名</router-link><span>/</span><span>{{ product.name }}</span></div>
  <section class="hero">
    <div class="product-panel">
      <div class="product-top">
        <div class="product-icon"><img :src="`/images/ea/${product.id}.png`" :alt="product.name"></div>
        <div class="product-info"><h1>{{ product.name }}</h1><p class="subtitle">{{ product.subtitle }}</p><div class="tags"><span v-for="tag in product.tags" :key="tag">{{ tag }}</span></div></div>
      </div>
      <p class="desc">{{ product.desc }}</p>
      <div class="meta"><div><label>开发者</label><strong>LOZENO Labs</strong></div><div><label>支持平台</label><strong>{{ product.platform }}</strong></div><div><label>适用市场</label><strong>{{ product.market }}</strong></div><div><label>更新日期</label><strong>{{ product.update }}</strong></div></div>
    </div>
    <aside class="purchase-panel">
      <label>产品价格</label><div class="price">{{ product.price }}</div><small>一次性购买 · 示例价格</small><div class="divider"></div>
      <div class="detail"><span>授权方式</span><span>{{ product.license }}</span></div><div class="detail"><span>交付方式</span><span>数字下载</span></div><div class="detail"><span>平台要求</span><span>{{ product.platform }}</span></div>
      <button class="buy" @click="$emit('purchase')">立即购买</button><button class="secondary" @click="documentView">查看策略表现</button>
      <p class="footnote">购买前请确认交易平台、账户类型及运行环境符合要求。</p>
    </aside>
  </section>
</template>

<script setup>
defineProps({product:{type:Object,required:true}})
defineEmits(['purchase'])
function documentView(){document.getElementById('performance')?.scrollIntoView({behavior:'smooth'})}
</script>

<style scoped>
.breadcrumb{display:flex;gap:9px;align-items:center;margin-bottom:24px;color:var(--次要灰色文字);font-size:13px}.breadcrumb a:hover{color:var(--主色调悬停色)}
.hero{display:grid;grid-template-columns:minmax(0,1fr) 330px;gap:24px;align-items:stretch}
.product-panel,.purchase-panel{background:var(--表面卡片背景色);border:1px solid var(--边框线条颜色);border-radius:var(--大圆角)}
.product-panel{padding:28px}.product-top{display:flex;gap:20px;align-items:flex-start}
.product-icon{width:120px;height:120px;flex-shrink:0;overflow:hidden;border-radius:16px;background:#1b1e26}
.product-icon img{width:100%;height:100%;display:block;object-fit:cover}
.product-info{min-width:0}h1{font-size:30px;line-height:1.25;font-weight:800;overflow-wrap:anywhere}
.subtitle{margin-top:9px;color:var(--次要灰色文字);font-size:14px;line-height:1.8}
.tags{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}.tags span{padding:5px 9px;background:var(--输入框背景色);border:1px solid var(--边框线条颜色);border-radius:var(--小圆角);color:#b9c2d2;font-size:11px}
.desc{margin-top:24px;color:#c1c8d5;font-size:14px;line-height:1.9}
.meta{display:flex;flex-wrap:wrap;gap:22px;margin-top:22px;padding-top:20px;border-top:1px solid var(--边框线条颜色)}
.meta div{display:flex;flex-direction:column;gap:6px}.meta label,.purchase-panel>label{font-size:12px;color:var(--次要灰色文字)}.meta strong{font-size:13px;font-weight:600}
.purchase-panel{padding:24px;display:flex;flex-direction:column}.price{font-size:34px;font-weight:800;margin-top:8px}.purchase-panel small{margin-top:5px;color:var(--次要灰色文字);font-size:12px}
.divider{height:1px;background:var(--边框线条颜色);margin:22px 0}.detail{display:flex;justify-content:space-between;gap:12px;font-size:13px;margin-bottom:14px}.detail span:first-child{color:var(--次要灰色文字)}
.buy,.secondary{width:100%;min-height:44px;border-radius:9px;font-size:14px;font-weight:700;cursor:pointer}.buy{margin-top:5px;border:0;background:var(--主色调蓝色);color:#fff}.buy:hover{background:var(--主色调悬停色)}
.secondary{margin-top:10px;background:transparent;border:1px solid #343b4d;color:#e2e7f0}.secondary:hover{border-color:var(--主色调悬停色);color:var(--主色调悬停色)}
.footnote{margin-top:14px;color:var(--次要灰色文字);font-size:11px;line-height:1.7;text-align:center}
@media(max-width:900px){.hero{grid-template-columns:minmax(0,1fr) 285px}.product-panel{padding:22px}}
@media(max-width:680px){.breadcrumb{margin-bottom:18px}.hero{grid-template-columns:1fr;gap:14px}.product-panel{padding:18px}.product-top{gap:14px}.product-icon{width:80px;height:80px;border-radius:12px}.product-info h1{font-size:23px}.subtitle{font-size:12px}.desc{margin-top:18px;font-size:13px}.meta{gap:16px;margin-top:17px;padding-top:16px}.purchase-panel{padding:19px}.price{font-size:30px}}
</style>