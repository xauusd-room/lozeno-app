
<template>
  <main class="account-page">
    <div class="page-heading">
      <div>
        <p class="eyebrow">ACCOUNT CENTER</p>
        <h1>个人资料</h1>
        <p class="subtitle">管理你的 LOZENO 账户信息和登录安全。</p>
      </div>
      <router-link class="back-link" to="/">返回首页</router-link>
    </div>

    <div v-if="loading" class="state-panel">
      <span class="loader"></span>
      正在加载个人资料…
    </div>

    <div v-else-if="loadError" class="state-panel error-panel">
      <p>{{ loadError }}</p>
      <button class="primary-btn" @click="loadProfile">重新加载</button>
      <router-link v-if="isAuthError" to="/" class="text-link">
        返回首页重新登录
      </router-link>
    </div>

    <template v-else>
      <section class="profile-card">
        <div class="profile-top">
          <div class="avatar">{{ avatarText }}</div>
          <div class="profile-identity">
            <h2>{{ profile.display_name || 'LOZENO 用户' }}</h2>
            <p>{{ profile.email }}</p>
          </div>
          <span class="account-badge">账户已登录</span>
        </div>

        <div class="info-grid">
          <div class="info-item">
            <span>注册邮箱</span>
            <strong>{{ profile.email || '—' }}</strong>
            <small>邮箱暂不支持修改</small>
          </div>
          <div class="info-item">
            <span>注册时间</span>
            <strong>{{ formatDate(profile.created_at) }}</strong>
          </div>
          <div class="info-item">
            <span>邮箱验证状态</span>
            <strong :class="profile.email_verified ? 'verified' : 'unverified'">
              {{ profile.email_verified ? '已验证' : '尚未验证' }}
            </strong>
          </div>
        </div>
      </section>

      <section class="content-card">
        <div class="section-heading">
          <div>
            <h2>基本信息</h2>
            <p>更新你在 LOZENO 平台上的个人资料。</p>
          </div>
        </div>

        <form class="form-grid" @submit.prevent="saveProfile">
          <label class="field">
            <span>昵称</span>
            <input
              v-model="form.display_name"
              type="text"
              maxlength="80"
              placeholder="请输入昵称"
            />
            <small>最多 80 个字符</small>
          </label>

          <label class="field">
            <span>手机号</span>
            <input
              v-model="form.phone"
              type="tel"
              maxlength="30"
              placeholder="请输入手机号（选填）"
            />
            <small>最多 30 个字符</small>
          </label>

          <div class="form-actions">
            <button class="primary-btn" type="submit" :disabled="savingProfile">
              {{ savingProfile ? '保存中…' : '保存修改' }}
            </button>
          </div>
        </form>
      </section>

      <section class="content-card">
        <div class="section-heading">
          <div>
            <h2>修改密码</h2>
            <p>修改密码后，现有登录会话会被撤销，需要重新登录。</p>
          </div>
        </div>

        <form class="form-grid password-grid" @submit.prevent="savePassword">
          <label class="field">
            <span>当前密码</span>
            <input
              v-model="passwordForm.current_password"
              type="password"
              autocomplete="current-password"
              placeholder="输入当前密码"
              required
            />
          </label>

          <label class="field">
            <span>新密码</span>
            <input
              v-model="passwordForm.new_password"
              type="password"
              autocomplete="new-password"
              minlength="8"
              maxlength="256"
              placeholder="至少 8 位"
              required
            />
          </label>

          <label class="field">
            <span>确认新密码</span>
            <input
              v-model="passwordForm.confirm_password"
              type="password"
              autocomplete="new-password"
              minlength="8"
              maxlength="256"
              placeholder="再次输入新密码"
              required
            />
          </label>

          <div class="form-actions">
            <button class="primary-btn" type="submit" :disabled="savingPassword">
              {{ savingPassword ? '提交中…' : '修改密码' }}
            </button>
          </div>
        </form>
      </section>

      <p v-if="notice.text" class="notice" :class="notice.type">
        {{ notice.text }}
      </p>
    </template>
  </main>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  fetchProfile,
  updateProfile,
  changePassword
} from '../services/account'

const router = useRouter()

const loading = ref(true)
const loadError = ref('')
const savingProfile = ref(false)
const savingPassword = ref(false)

const profile = ref({
  id: null,
  email: '',
  display_name: '',
  phone: '',
  email_verified: false,
  created_at: null
})

const form = reactive({
  display_name: '',
  phone: ''
})

const passwordForm = reactive({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

const notice = reactive({
  text: '',
  type: 'success'
})

const isAuthError = computed(() =>
  /登录已失效|请先登录|重新登录/.test(loadError.value)
)

const avatarText = computed(() => {
  const value = profile.value.display_name || profile.value.email || 'L'
  return [...value][0]?.toUpperCase() || 'L'
})

function showNotice(text, type = 'success') {
  notice.text = text
  notice.type = type
}

function formatDate(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '—'
  return date.toLocaleString('zh-CN', { hour12: false })
}

async function loadProfile() {
  loading.value = true
  loadError.value = ''
  notice.text = ''

  try {
    const user = await fetchProfile()
    profile.value = { ...profile.value, ...user }
    form.display_name = user.display_name || ''
    form.phone = user.phone || ''
  } catch (error) {
    loadError.value = error.message || '个人资料加载失败'
  } finally {
    loading.value = false
  }
}

async function saveProfile() {
  if (savingProfile.value) return

  savingProfile.value = true
  notice.text = ''

  try {
    const user = await updateProfile({
      display_name: form.display_name.trim(),
      phone: form.phone.trim()
    })

    profile.value = { ...profile.value, ...user }
    form.display_name = user.display_name || ''
    form.phone = user.phone || ''
    showNotice('个人资料已保存')
  } catch (error) {
    showNotice(error.message || '保存失败', 'error')
  } finally {
    savingProfile.value = false
  }
}

async function savePassword() {
  if (savingPassword.value) return

  if (passwordForm.new_password.length < 8) {
    showNotice('新密码至少需要 8 位', 'error')
    return
  }

  if (passwordForm.new_password !== passwordForm.confirm_password) {
    showNotice('两次输入的新密码不一致', 'error')
    return
  }

  if (passwordForm.current_password === passwordForm.new_password) {
    showNotice('新密码不能与当前密码相同', 'error')
    return
  }

  savingPassword.value = true
  notice.text = ''

  try {
    const result = await changePassword(
      passwordForm.current_password,
      passwordForm.new_password
    )

    localStorage.removeItem('lozeno_access_token')

    Object.keys(passwordForm).forEach(key => {
      passwordForm[key] = ''
    })

    showNotice(result.message || '密码已修改，请重新登录')
    window.setTimeout(() => router.push('/'), 1200)
  } catch (error) {
    showNotice(error.message || '密码修改失败', 'error')
  } finally {
    savingPassword.value = false
  }
}

onMounted(loadProfile)
</script>

<style scoped>
.account-page {
  width: min(1100px, calc(100% - 32px));
  margin: 0 auto;
  padding: 44px 0 80px;
  color: #e7eaf0;
}

.page-heading,
.profile-top,
.section-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.page-heading {
  margin-bottom: 28px;
}

.eyebrow {
  margin: 0 0 10px;
  color: #6484ff;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 2px;
}

h1,
h2,
p {
  margin-top: 0;
}

h1 {
  margin-bottom: 10px;
  font-size: 30px;
  font-weight: 650;
}

.subtitle,
.section-heading p {
  margin-bottom: 0;
  color: #848e9c;
  font-size: 13px;
  line-height: 1.7;
}

.back-link,
.text-link {
  color: #8da4ff;
  font-size: 13px;
  text-decoration: none;
}

.back-link:hover,
.text-link:hover {
  color: #b3c2ff;
}

.profile-card,
.content-card {
  margin-bottom: 20px;
  padding: 26px;
  background: #141722;
  border: 1px solid #222630;
  border-radius: 12px;
}

.profile-top {
  justify-content: flex-start;
  padding-bottom: 24px;
  border-bottom: 1px solid #252936;
}

.avatar {
  display: grid;
  width: 58px;
  height: 58px;
  flex-shrink: 0;
  place-items: center;
  color: #fff;
  background: linear-gradient(135deg, #315bff, #233db3);
  border-radius: 14px;
  font-size: 23px;
  font-weight: 700;
}

.profile-identity {
  min-width: 0;
  flex: 1;
}

.profile-identity h2 {
  margin-bottom: 7px;
  font-size: 19px;
}

.profile-identity p {
  margin-bottom: 0;
  color: #848e9c;
  font-size: 13px;
  overflow-wrap: anywhere;
}

.account-badge {
  padding: 6px 10px;
  color: #83d8ae;
  background: #18352b;
  border: 1px solid #285541;
  border-radius: 6px;
  font-size: 11px;
  white-space: nowrap;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 24px;
  padding-top: 24px;
}

.info-item {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 9px;
}

.info-item span,
.field > span {
  color: #848e9c;
  font-size: 12px;
}

.info-item strong {
  overflow-wrap: anywhere;
  font-size: 13px;
  font-weight: 550;
}

.info-item small,
.field small {
  color: #687180;
  font-size: 11px;
}

.verified {
  color: #73d6a6;
}

.unverified {
  color: #e6b568;
}

.section-heading {
  margin-bottom: 24px;
}

.section-heading h2 {
  margin-bottom: 8px;
  font-size: 17px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 22px;
}

.password-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.field {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 10px;
}

.field input {
  width: 100%;
  height: 43px;
  padding: 0 13px;
  color: #e7eaf0;
  background: #1b1e26;
  border: 1px solid #303542;
  border-radius: 7px;
  outline: none;
  font: inherit;
  font-size: 13px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.field input:focus {
  border-color: #315bff;
  box-shadow: 0 0 0 3px #315bff20;
}

.field input::placeholder {
  color: #626b79;
}

.form-actions {
  display: flex;
  align-items: end;
  gap: 12px;
}

.primary-btn {
  min-height: 40px;
  padding: 0 20px;
  color: #fff;
  background: #315bff;
  border: 1px solid #315bff;
  border-radius: 7px;
  cursor: pointer;
  font: inherit;
  font-size: 13px;
  transition: background 0.2s;
}

.primary-btn:hover:not(:disabled) {
  background: #4169ff;
}

.primary-btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.state-panel {
  display: flex;
  min-height: 180px;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 24px;
  color: #848e9c;
  background: #141722;
  border: 1px solid #222630;
  border-radius: 12px;
  text-align: center;
}

.error-panel {
  color: #f08f8f;
}

.error-panel .text-link {
  margin-top: 2px;
}

.loader {
  width: 22px;
  height: 22px;
  border: 2px solid #303747;
  border-top-color: #315bff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.notice {
  margin: 0;
  padding: 13px 16px;
  border: 1px solid;
  border-radius: 8px;
  font-size: 13px;
}

.notice.success {
  color: #83d8ae;
  background: #18352b;
  border-color: #285541;
}

.notice.error {
  color: #f08f8f;
  background: #351e24;
  border-color: #5a2b36;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 680px) {
  .account-page {
    width: calc(100% - 24px);
    padding-top: 28px;
  }

  .page-heading {
    align-items: flex-start;
  }

  h1 {
    font-size: 25px;
  }

  .profile-card,
  .content-card {
    padding: 18px;
  }

  .profile-top {
    flex-wrap: wrap;
  }

  .account-badge {
    margin-left: 76px;
  }

  .info-grid,
  .form-grid,
  .password-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .info-grid {
    gap: 20px;
  }

  .form-actions .primary-btn {
    width: 100%;
  }
}
</style>
