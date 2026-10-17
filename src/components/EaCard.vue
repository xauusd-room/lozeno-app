
<template>
  <div class="ea-card" @click="goDetail" role="link" tabindex="0" @keydown.enter="goDetail" @keydown.space.prevent="goDetail">
    <button class="fav-btn" :class="{active:isFav}" @click.stop="isFav=!isFav" aria-label="收藏 EA"><svg viewBox="0 0 24 24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg></button>
    <div class="card-img-wrap">
      <img :src="`/images/ea/${id}.png`" :alt="title" class="card-img">
      <span class="platform-badge" :class="platformClass">{{platform}}</span>
    </div>
    <div class="card-content">
      <div class="card-header">
        <div class="title-wrap"><h2 class="ea-title">{{title}}</h2><span class="ea-tag">{{tag}}</span></div>
        <span class="rate-badge" :class="rate>0?'rate-up':'rate-down'">{{rate>0?'+'+rate+'%':rate+'%'}}</span>
      </div>
      <div class="ea-details">
        <div class="detail-item"><span class="label">激活数:</span><span class="value">{{installs}}</span></div>
        <div class="detail-item"><span class="label">胜率:</span><span class="value highlight">{{winRate}}%</span></div>
      </div>
      <div class="progress-container"><div class="progress-bar" :style="{width:winRate+'%'}"></div></div>
    </div>
  </div>
</template>

<script setup>
import {ref} from 'vue'
import {useRouter} from 'vue-router'

const props=defineProps({id:Number,title:String,tag:String,platform:String,platformClass:String,rate:Number,installs:Number,winRate:Number})
const router=useRouter(),isFav=ref(false)
function goDetail(){router.push({path:'/product',query:{id:props.id}})}
</script>

<style scoped>
.ea-card{position:relative;min-height:160px;width:100%;min-width:0;background:var(--表面卡片背景色,#141722);border:1px solid var(--边框线条颜色,#222630);border-radius:var(--大圆角,16px);padding:20px;display:flex;gap:20px;align-items:center;transition:all .25s;cursor:pointer}
.ea-card:hover{border-color:var(--主色调蓝色,#315bff);box-shadow:0 0 14px var(--主色发光特效);transform:translateY(-2px)}
.card-img-wrap{position:relative;width:120px;height:120px;flex-shrink:0;border-radius:var(--小圆角,6px);background:#1e2230;overflow:hidden}
.card-img{display:block;width:100%;height:100%;object-fit:cover}
.platform-badge{position:absolute;right:8px;bottom:8px;display:inline-flex;align-items:center;justify-content:center;height:24px;min-width:42px;padding:0 9px;border:1px solid currentColor;border-radius:5px;background:rgba(11,13,18,.88);font-size:10px;font-weight:700;letter-spacing:.5px;line-height:1;backdrop-filter:blur(8px)}
.text-mt5{color:#ffb454;border-color:rgba(255,180,84,.35)}
.text-mt4{color:#58b7ff;border-color:rgba(88,183,255,.35)}
.text-ai{color:#50e6d2;border-color:rgba(80,230,210,.35)}
.card-content{flex:1;display:flex;flex-direction:column;gap:12px;min-width:0}
.card-header{display:flex;justify-content:space-between;align-items:flex-start;gap:8px;min-width:0}
.title-wrap{display:flex;flex-direction:column;align-items:flex-start;gap:7px;min-width:0}
.ea-title{font-size:16px;font-weight:700;color:var(--主要文字颜色,#fff);overflow-wrap:anywhere}
.ea-tag{font-size:11px;padding:3px 8px;background:var(--输入框背景色,#1b1e26);color:var(--次要灰色文字,#848e9c);border-radius:var(--小圆角,6px)}
.rate-badge{font-size:13px;font-weight:700;padding:4px 8px;border-radius:var(--小圆角,6px);white-space:nowrap}
.rate-up{background:rgba(14,203,129,.15);color:var(--涨势绿色,#0ecb81)}
.rate-down{background:rgba(246,70,93,.15);color:var(--跌势红色,#f6465d)}
.ea-details{display:flex;flex-direction:column;gap:5px;font-size:12px}
.detail-item{display:flex;justify-content:space-between;gap:8px}
.detail-item .label{color:var(--次要灰色文字,#848e9c)}
.detail-item .value{color:var(--主要文字颜色,#fff)}
.detail-item .highlight{font-weight:600}
.progress-container{width:100%;height:6px;background:var(--输入框背景色,#1b1e26);border-radius:100px;overflow:hidden}
.progress-bar{height:100%;background:var(--涨势绿色,#0ecb81);border-radius:100px}
.fav-btn{position:absolute;top:10px;left:10px;z-index:10;background:rgba(0,0,0,.4);border:none;width:26px;height:26px;border-radius:4px;cursor:pointer;display:flex;align-items:center;justify-content:center}
.fav-btn svg{width:15px;height:15px;fill:none;stroke:var(--次要灰色文字,#848e9c);stroke-width:2}
.fav-btn.active svg{fill:#ffbc0a;stroke:#ffbc0a}
@media(max-width:600px){.ea-card{min-height:130px;padding:14px;gap:12px}.card-img-wrap{width:88px;height:100px}.card-content{gap:9px}.ea-title{font-size:14px}.rate-badge{font-size:11px;padding:3px 5px}}
</style>
