<template>
  <header class="header">
    <div class="header-inner page-container">
      <router-link to="/" class="logo" aria-label="LOZENO 首页"><span class="logo-icon">L</span><span class="logo-text">LOZENO</span></router-link>
      <div class="search-wrap">
        <form class="search" id="searchForm" @submit.prevent role="search"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="m16 16 4 4"/></svg><input id="searchInput" v-model="searchKeyword" @input="handleSearch" type="search" placeholder="搜索 EA / 插件..." autocomplete="off" aria-label="搜索 EA 或插件"/><span class="search-key">/</span></form>
        <div class="search-results" :class="{show:searchResults.length>0}"><a v-for="(item,index) in searchResults" :key="index" :href="item.url" @click="searchKeyword='';searchResults=[]">{{item.name}}</a></div>
      </div>
      <nav class="nav" :class="{'mobile-open':mobileMenuOpen}" aria-label="主导航">
        <router-link to="/" @click="mobileMenuOpen=false"><svg viewBox="0 0 24 24"><path d="m3 10 9-7 9 7"/><path d="M5 9v12h14V9M9 21v-7h6v7"/></svg><span>首页</span></router-link>
        <router-link to="/market" @click="mobileMenuOpen=false"><svg viewBox="0 0 24 24"><path d="M3 3v18h18"/><path d="m7 14 4-4 4 3 6-7"/></svg><span>黄金行情</span></router-link>
        <router-link to="/live" @click="mobileMenuOpen=false"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="m10 8 6 4-6 4z"/></svg><span>实盘直播</span></router-link>
        <router-link to="/ranking" @click="mobileMenuOpen=false"><svg viewBox="0 0 24 24"><path d="M8 21h8M12 17v4M7 4h10v5a5 5 0 0 1-10 0z"/><path d="M7 6H3v2a5 5 0 0 0 5 5M17 6h4v2a5 5 0 0 1-5 5"/></svg><span>EA排名</span></router-link>
        <router-link to="/stocks" @click="mobileMenuOpen=false"><svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg><span>股票专区</span></router-link>
        <router-link to="/events" @click="mobileMenuOpen=false"><svg viewBox="0 0 24 24"><rect x="3" y="8" width="18" height="13" rx="2"/><path d="M12 8v13M3 12h18M12 8H7a3 3 0 1 1 3-3c0 2 2 3 2 3Zm0 0h5a3 3 0 1 0-3-3c0 2-2 3-2 3Z"/></svg><span>活动</span></router-link>
      </nav>
      <div class="actions">
        <template v-if="!currentUser"><button class="btn login" type="button" @click="openAuth('login')">登录</button><button class="btn register" type="button" @click="openAuth('register')">注册</button></template>
        <template v-else>
          <button class="user-trigger" type="button" :aria-expanded="userMenuOpen" aria-label="打开账号菜单" @click.stop="userMenuOpen=!userMenuOpen"><span class="user-avatar"><img v-if="currentUser.avatar_data_url" :src="currentUser.avatar_data_url" alt="用户头像"/><svg v-else viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></svg></span><span class="user-trigger-info"><span class="user-trigger-title">{{currentUser.display_name||'我的账号'}}</span><span class="user-trigger-status"><span class="status-dot"></span>已登录</span></span><svg class="user-chevron" :class="{rotated:userMenuOpen}" viewBox="0 0 24 24"><path d="m7 10 5 5 5-5"/></svg></button>
          <div v-if="userMenuOpen" class="user-menu" @click.stop>
            <div class="user-menu-profile"><span class="user-avatar user-avatar-large"><img v-if="currentUser.avatar_data_url" :src="currentUser.avatar_data_url" alt="用户头像"/><svg v-else viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></svg></span><div class="user-menu-info"><span class="user-menu-title">{{currentUser.display_name||'我的账号'}}</span><span class="user-menu-email">{{currentUser.email}}</span></div></div>
            <div class="user-menu-divider"></div>
            <router-link class="user-menu-item" to="/profile" @click="userMenuOpen=false"><svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></svg><span>个人资料</span><svg class="menu-item-arrow" viewBox="0 0 24 24"><path d="m9 18 6-6-6-6"/></svg></router-link>
            <router-link class="user-menu-item" to="/orders" @click="userMenuOpen=false"><svg viewBox="0 0 24 24"><path d="M6 3h12l2 4v14H4V7z"/><path d="M4 7h16M9 11h6M9 15h6"/></svg><span>我的订单</span><svg class="menu-item-arrow" viewBox="0 0 24 24"><path d="m9 18 6-6-6-6"/></svg></router-link>
            <router-link class="user-menu-item" to="/licenses" @click="userMenuOpen=false"><svg viewBox="0 0 24 24"><circle cx="8" cy="15" r="4"/><path d="m11 12 8-8 2 2-2 2 2 2-3 3-2-2-2 2"/></svg><span>我的授权</span><svg class="menu-item-arrow" viewBox="0 0 24 24"><path d="m9 18 6-6-6-6"/></svg></router-link>
            <div class="user-menu-divider"></div>
            <button class="user-logout" type="button" @click="handleLogout"><svg viewBox="0 0 24 24"><path d="M10 17l5-5-5-5M15 12H3"/><path d="M12 3h6a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-6"/></svg>退出登录</button>
          </div>
        </template>
      </div>
      <button class="menu-toggle" type="button" :aria-expanded="mobileMenuOpen" aria-label="展开导航菜单" @click="mobileMenuOpen=!mobileMenuOpen;userMenuOpen=false"><span></span><span></span><span></span></button>
      <AuthModal v-if="authModalOpen" :initial-mode="authMode" @close="authModalOpen=false" @authenticated="handleAuthenticated"/>
    </div>
  </header>
</template>

<script setup>
import {onMounted,onBeforeUnmount,ref} from 'vue'
import AuthModal from './AuthModal.vue'
import {getCurrentUser,getToken,logout} from '../services/auth'
import {currentUser,setCurrentUser} from '../services/userStore'

const authModalOpen=ref(false),authMode=ref('login'),userMenuOpen=ref(false),mobileMenuOpen=ref(false),searchKeyword=ref(''),searchResults=ref([])
function openAuth(mode){authMode.value=mode;authModalOpen.value=true;mobileMenuOpen.value=false}
function handleAuthenticated(user){setCurrentUser(user);userMenuOpen.value=false}
function handleDocumentClick(event){if(!event.target.closest('.actions'))userMenuOpen.value=false}
function handleDocumentKeydown(event){if(event.key==='Escape'){userMenuOpen.value=false;mobileMenuOpen.value=false}}
onMounted(()=>{document.addEventListener('click',handleDocumentClick);document.addEventListener('keydown',handleDocumentKeydown)})
onBeforeUnmount(()=>{document.removeEventListener('click',handleDocumentClick);document.removeEventListener('keydown',handleDocumentKeydown)})
async function handleLogout(){try{await logout()}catch(error){console.error('退出登录请求失败：',error)}setCurrentUser(null);userMenuOpen.value=false}
onMounted(async()=>{if(!getToken()){setCurrentUser(null);return}try{setCurrentUser(await getCurrentUser())}catch{setCurrentUser(null)}})
const items=[{name:'EA排名',url:'/ranking',keywords:'EA 自动交易 机器人 排名 策略'},{name:'插件',url:'/plugins',keywords:'插件 工具 扩展 指标'},{name:'活动',url:'/events',keywords:'活动 优惠 公告'},{name:'黄金行情',url:'/market',keywords:'行情 黄金 XAUUSD 价格'},{name:'实盘直播',url:'/live',keywords:'实盘 直播 MT5 黄金 XAUUSD M5 实时交易 AI 分析'},{name:'首页',url:'/',keywords:'首页 LOZENO'}]
function handleSearch(){const query=searchKeyword.value.trim().toLowerCase();searchResults.value=query?items.filter(i=>(i.name+' '+i.keywords).toLowerCase().includes(query)):[]}
</script>

<style scoped>
.header{position:sticky;top:0;z-index:1000;width:100%;height:74px;background:var(--主页面背景色,#0b0d12);border-bottom:0;backdrop-filter:blur(8px);isolation:isolate}
.header::after{content:"";position:absolute;bottom:0;left:0;width:100%;height:1px;background:linear-gradient(90deg,transparent,rgba(49,91,255,.015) 15%,rgba(49,91,255,.06) 28%,rgba(49,91,255,.2) 38%,rgba(49,91,255,.55) 46%,var(--主色调蓝色,#315bff) 50%,rgba(49,91,255,.55) 54%,rgba(49,91,255,.2) 62%,rgba(49,91,255,.06) 72%,rgba(49,91,255,.015) 85%,transparent);pointer-events:none}
.header-inner{height:73px;display:flex;align-items:center;min-width:0}
.logo{display:flex;align-items:center;gap:10px;color:var(--主要文字颜色,#fff);text-decoration:none;white-space:nowrap;flex-shrink:0}
.logo-icon{width:32px;height:32px;display:flex;align-items:center;justify-content:center;background:var(--主色调蓝色,#315bff);border-radius:8px;color:#fff;font-size:20px;font-weight:800;box-shadow:0 0 12px var(--主色发光特效,rgba(49,91,255,.2))}
.logo-text{font-size:var(--logo标志字号,21px);font-weight:800;letter-spacing:.5px}
.search-wrap{position:relative;width:260px;min-width:0;margin-left:24px;flex-shrink:1}
.search{height:40px;width:100%;display:flex;align-items:center;gap:10px;padding:0 12px;background:var(--输入框背景色,#1b1e26);border:1px solid transparent;border-radius:11px;transition:all .2s}
.search:focus-within,.search:hover{border-color:var(--主色调蓝色,#315bff);box-shadow:0 0 10px var(--主色发光特效,rgba(49,91,255,.2))}
.search svg{width:18px;height:18px;stroke:var(--次要灰色文字,#848e9c);fill:none;stroke-width:2;flex-shrink:0}
.search input{width:100%;min-width:0;border:0;outline:0;background:transparent;color:var(--主要文字颜色,#fff);font-size:13px}
.search input::placeholder{color:#5e6673}
.search-key{color:var(--次要灰色文字,#848e9c);background:#2b2f3a;border-radius:4px;padding:2px 6px;font-size:11px;font-weight:600}
.nav{display:flex;align-items:center;gap:24px;margin-left:auto;margin-right:24px}
.nav a{display:flex;align-items:center;gap:8px;padding:10px 0;color:var(--次要灰色文字,#848e9c);font-size:14px;font-weight:600;text-decoration:none;transition:color .18s}
.nav a svg{width:18px;height:18px;stroke:currentColor;fill:none;stroke-width:2;flex-shrink:0}
.nav a.router-link-active,.nav a:hover{color:var(--主色调悬停色,#4169ff)}
.actions{display:flex;align-items:center;gap:10px;position:relative;flex-shrink:0}
.btn{height:36px;padding:0 16px;display:flex;align-items:center;justify-content:center;border-radius:10px;font-family:inherit;font-size:13px;font-weight:600;transition:all .18s;cursor:pointer;border-style:solid;white-space:nowrap}
.login{color:var(--主要文字颜色,#fff);border:1px solid var(--边框线条颜色,#222630);background:transparent}
.login:hover{color:var(--主色调悬停色,#4169ff);border-color:var(--主色调悬停色,#4169ff)}
.register{color:#fff;background:var(--主色调蓝色,#315bff);border-color:var(--主色调蓝色,#315bff);box-shadow:0 4px 12px var(--主色发光特效,rgba(49,91,255,.2))}
.register:hover{background:var(--主色调悬停色,#4169ff);border-color:var(--主色调悬停色,#4169ff);transform:translateY(-1px)}
.menu-toggle{display:none}
.search-results{display:none;position:absolute;top:46px;left:0;right:0;padding:6px;background:var(--表面卡片背景色,#141722);border:1px solid var(--边框线条颜色,#222630);border-radius:10px;box-shadow:0 12px 30px #0009;z-index:20}
.search-results.show{display:block}
.search-results a{display:block;padding:10px;border-radius:6px;color:#c3cada;font-size:13px;text-decoration:none}
.search-results a:hover{color:#fff;background:var(--主色调蓝色,#315bff)}
.user-trigger{height:42px;display:flex;align-items:center;gap:10px;padding:4px 10px 4px 5px;background:transparent;border:1px solid transparent;border-radius:10px;color:var(--主要文字颜色,#fff);cursor:pointer;transition:background .18s,border-color .18s}
.user-trigger:hover,.user-trigger[aria-expanded=true]{background:var(--表面卡片背景色,#141722);border-color:var(--边框线条颜色,#222630)}
.user-avatar{width:32px;height:32px;flex-shrink:0;display:flex;align-items:center;justify-content:center;border-radius:9px;background:linear-gradient(145deg,#4169ff,#2444bd);color:#fff}
.user-avatar img{width:100%;height:100%;object-fit:cover;border-radius:inherit}
.user-avatar svg{width:19px;height:19px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.user-trigger-info{display:flex;flex-direction:column;align-items:flex-start;gap:3px}
.user-trigger-title{color:var(--主要文字颜色,#fff);font-size:12px;font-weight:600;line-height:1.2}
.user-trigger-status{display:flex;align-items:center;gap:5px;color:var(--次要灰色文字,#848e9c);font-size:11px;line-height:1.2}
.status-dot{width:6px;height:6px;flex-shrink:0;border-radius:50%;background:#35c98a;box-shadow:0 0 7px #35c98a4d}
.user-chevron{width:15px;height:15px;margin-left:3px;fill:none;stroke:var(--次要灰色文字,#848e9c);stroke-width:1.8;transition:transform .18s}
.user-chevron.rotated{transform:rotate(180deg)}
.user-menu{position:absolute;top:calc(100% + 12px);right:0;z-index:1100;width:260px;max-width:calc(100vw - 24px);padding:8px;background:var(--表面卡片背景色,#141722);border:1px solid var(--边框线条颜色,#222630);border-radius:13px;box-shadow:0 16px 42px #0006;animation:user-menu-in .16s ease-out}
.user-menu-profile{display:flex;align-items:center;gap:12px;padding:12px 10px}
.user-avatar-large{width:40px;height:40px;border-radius:11px}
.user-avatar-large img{width:100%;height:100%;object-fit:cover;border-radius:inherit}
.user-avatar-large svg{width:23px;height:23px}
.user-menu-info{min-width:0;display:flex;flex-direction:column;gap:6px}
.user-menu-title{color:var(--主要文字颜色,#fff);font-size:13px;font-weight:600}
.user-menu-email{max-width:185px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--次要灰色文字,#848e9c);font-size:12px}
.user-menu-divider{height:1px;margin:4px 2px;background:var(--边框线条颜色,#222630)}
.user-menu-item{height:42px;display:flex;align-items:center;gap:11px;padding:0 10px;border-radius:8px;color:#c3cada;text-decoration:none;font-size:13px;transition:background .18s,color .18s}
.user-menu-item>svg:first-child{width:17px;height:17px;flex-shrink:0;fill:none;stroke:currentColor;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}
.user-menu-item span{flex:1}
.user-menu-item .menu-item-arrow{width:14px;height:14px;fill:none;stroke:var(--次要灰色文字,#848e9c);stroke-width:1.8}
.user-menu-item:hover,.user-menu-item.router-link-active{background:#315bff1f;color:var(--主色调悬停色,#4169ff)}
.user-logout{width:100%;height:38px;display:flex;align-items:center;gap:9px;padding:0 10px;border:0;border-radius:8px;background:transparent;color:#e18b8b;font-family:inherit;font-size:13px;text-align:left;cursor:pointer}
.user-logout svg{width:16px;height:16px;fill:none;stroke:currentColor;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}
.user-logout:hover{background:#e15d5d17;color:#ff7777}
@keyframes user-menu-in{from{opacity:0;transform:translateY(-5px)}to{opacity:1;transform:translateY(0)}}
@media(max-width:1100px) and (min-width:769px){.search-wrap{width:200px;margin-left:16px}.nav{gap:14px;margin-right:16px}.nav a{gap:5px}.btn{padding:0 12px}}
@media(max-width:768px){
  .header{height:auto;min-height:74px}
  .header-inner{position:relative;height:auto;min-height:73px;flex-wrap:wrap;column-gap:10px;padding-top:12px;padding-bottom:12px}
  .logo{gap:7px}
  .logo-icon{width:30px;height:30px;font-size:19px}
  .logo-text{font-size:19px}
  .actions{margin-left:auto;gap:6px}
  .btn{height:34px;padding:0 10px;font-size:12px;border-radius:8px}
  .menu-toggle{width:34px;height:34px;flex-shrink:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px;padding:0;border:1px solid var(--边框线条颜色,#222630);border-radius:8px;background:transparent;cursor:pointer}
  .menu-toggle span{display:block;width:17px;height:2px;border-radius:2px;background:#fff;transition:transform .2s,opacity .2s}
  .menu-toggle[aria-expanded=true] span:first-child{transform:translateY(7px) rotate(45deg)}
  .menu-toggle[aria-expanded=true] span:nth-child(2){opacity:0}
  .menu-toggle[aria-expanded=true] span:last-child{transform:translateY(-7px) rotate(-45deg)}
  .search-wrap{order:3;width:100%;flex:0 0 100%;margin:10px 0 0}
  .search{height:38px}
  .search-results{top:43px}
  .nav{display:none;position:absolute;top:calc(100% + 12px);left:0;right:0;z-index:1200;flex-direction:column;align-items:stretch;gap:2px;margin:0;padding:8px;background:var(--表面卡片背景色,#141722);border:1px solid var(--边框线条颜色,#222630);border-radius:12px;box-shadow:0 16px 35px #0008}
  .nav.mobile-open{display:flex}
  .nav a{min-height:42px;padding:0 12px;gap:10px;border-radius:8px}
  .nav a:hover,.nav a.router-link-active{background:#315bff1c}
  .nav a svg{width:18px;height:18px}
  .user-trigger{height:36px;padding:2px 4px}
  .user-trigger-info,.user-chevron{display:none}
  .user-avatar{width:28px;height:28px}
  .user-menu{top:calc(100% + 8px)}
}
@media(max-width:360px){.header-inner{column-gap:6px}.logo{gap:5px}.logo-text{font-size:17px}.logo-icon{width:28px;height:28px}.actions{gap:4px}.btn{padding:0 8px}.menu-toggle{width:31px;height:34px}}
</style>
