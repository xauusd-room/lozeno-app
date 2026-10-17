<template>
  <Teleport to="body">
  <div class="auth-mask" @click.self="$emit('close')" @keydown.esc="$emit('close')">
    <section class="auth-modal" role="dialog" aria-modal="true" :aria-label="mode === 'login' ? '登录 LOZENO' : '注册 LOZENO'">
      <button class="close-btn" type="button" aria-label="关闭" @click="$emit('close')">×</button>
      <div class="brand-mark">L</div>
      <h2>{{ mode === 'login' ? '欢迎回来' : '创建 LOZENO 账号' }}</h2>
      <p class="subtitle">{{ mode === 'login' ? '登录以继续使用 LOZENO' : '使用邮箱注册你的账号' }}</p>
      <form @submit.prevent="submit">
        <label for="auth-email">邮箱</label>
        <input id="auth-email" v-model.trim="email" type="email" autocomplete="email" placeholder="name@example.com" required maxlength="254" />
        <label for="auth-password">密码</label>
        <input id="auth-password" v-model="password" :type="showPassword ? 'text' : 'password'" :autocomplete="mode === 'login' ? 'current-password' : 'new-password'" placeholder="请输入密码" required minlength="8" maxlength="128" />
        <label v-if="mode === 'register'" for="auth-confirm">确认密码</label>
        <input v-if="mode === 'register'" id="auth-confirm" v-model="confirmPassword" type="password" autocomplete="new-password" placeholder="请再次输入密码" required minlength="8" maxlength="128" />
        <button class="show-password" type="button" @click="showPassword = !showPassword">{{ showPassword ? '隐藏密码' : '显示密码' }}</button>
        <p v-if="error" class="message error">{{ error }}</p>
        <p v-if="notice" class="message notice">{{ notice }}</p>
        <button class="submit-btn" type="submit" :disabled="loading">{{ loading ? '请稍候…' : mode === 'login' ? '登录' : '注册' }}</button>
      </form>
      <p class="switch-mode">
        {{ mode === 'login' ? '还没有账号？' : '已经有账号？' }}
        <button type="button" @click="switchMode">{{ mode === 'login' ? '立即注册' : '返回登录' }}</button>
      </p>
      <p v-if="mode === 'register'" class="verify-note">注册后可先登录；邮箱验证功能将在接入邮件服务后启用。</p>
    </section>
  </div>
  </Teleport>
</template>

<script setup>
import { ref, watch } from 'vue'
import { login, register, getCurrentUser } from '../services/auth'

const props = defineProps({ initialMode: { type: String, default: 'login' } })
const emit = defineEmits(['close', 'authenticated'])
const mode = ref(props.initialMode === 'register' ? 'register' : 'login')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)
const loading = ref(false)
const error = ref('')
const notice = ref('')

watch(() => props.initialMode, value => { mode.value = value === 'register' ? 'register' : 'login' })

function switchMode() {
  mode.value = mode.value === 'login' ? 'register' : 'login'
  password.value = ''
  confirmPassword.value = ''
  error.value = ''
  notice.value = ''
}

async function submit() {
  error.value = ''
  notice.value = ''
  if (mode.value === 'register' && password.value !== confirmPassword.value) {
    error.value = '两次输入的密码不一致'
    return
  }
  loading.value = true
  try {
    if (mode.value === 'register') {
      await register(email.value, password.value)
      notice.value = '注册成功，请登录'
      mode.value = 'login'
      password.value = ''
      confirmPassword.value = ''
      return
    }
    const result = await login(email.value, password.value)
    const currentUser = result.user || await getCurrentUser()
    emit('authenticated', currentUser)
    emit('close')
  } catch (e) {
    error.value = e.message || '操作失败，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-mask{position:fixed;inset:0;z-index:3000;display:flex;align-items:center;justify-content:center;padding:20px;background:rgba(3,5,10,.76);backdrop-filter:blur(8px)}
.auth-modal{position:relative;width:100%;max-width:420px;padding:32px;background:var(--表面卡片背景色,#141722);border:1px solid var(--边框线条颜色,#222630);border-radius:16px;box-shadow:0 24px 80px rgba(0,0,0,.5);color:var(--主要文字颜色,#fff)}
.close-btn{position:absolute;top:14px;right:16px;width:32px;height:32px;border:0;border-radius:8px;background:transparent;color:var(--次要灰色文字,#848e9c);font-size:25px;cursor:pointer}
.close-btn:hover{background:rgba(255,255,255,.06);color:#fff}
.brand-mark{display:flex;align-items:center;justify-content:center;width:42px;height:42px;margin-bottom:20px;border-radius:11px;background:var(--主色调蓝色,#315bff);font-size:25px;font-weight:800;box-shadow:0 0 22px rgba(49,91,255,.25)}
h2{font-size:24px;font-weight:800;letter-spacing:-.4px}
.subtitle{margin-top:8px;margin-bottom:26px;color:var(--次要灰色文字,#848e9c);font-size:13px}
form{display:flex;flex-direction:column}
label{margin:0 0 8px;font-size:13px;font-weight:600;color:#dce1eb}
input{width:100%;height:44px;margin-bottom:17px;padding:0 13px;border:1px solid var(--边框线条颜色,#222630);border-radius:9px;outline:none;background:var(--输入框背景色,#1b1e26);color:#fff;font:inherit;font-size:13px}
input:focus{border-color:var(--主色调蓝色,#315bff);box-shadow:0 0 0 3px rgba(49,91,255,.12)}
input::placeholder{color:#687181}
.show-password{align-self:flex-end;margin-top:-8px;margin-bottom:18px;padding:4px 0;border:0;background:transparent;color:var(--次要灰色文字,#848e9c);font-size:12px;cursor:pointer}
.submit-btn{height:44px;border:1px solid var(--主色调蓝色,#315bff);border-radius:9px;background:var(--主色调蓝色,#315bff);color:#fff;font-size:14px;font-weight:700;cursor:pointer;transition:background .18s}
.submit-btn:hover{background:var(--主色调悬停色,#4169ff)}
.submit-btn:disabled{opacity:.65;cursor:wait}
.message{margin:0 0 14px;font-size:12px;line-height:1.6}
.error{color:#ff697a}
.notice{color:#0ecb81}
.switch-mode{margin-top:22px;text-align:center;color:var(--次要灰色文字,#848e9c);font-size:13px}
.switch-mode button{padding:0;border:0;background:transparent;color:#6d8aff;font:inherit;font-weight:700;cursor:pointer}
.verify-note{margin-top:16px;color:#687181;text-align:center;font-size:11px;line-height:1.7}
@media(max-width:480px){.auth-modal{padding:26px 22px}h2{font-size:22px}}
</style>
