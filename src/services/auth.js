
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'https://lozeno-api.aaa375750526.workers.dev'

const TOKEN_KEY = 'lozeno_access_token'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

function saveToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
}

async function request(path, options = {}) {
  const token = getToken()
  const headers = { Accept: 'application/json', ...(options.body ? { 'Content-Type': 'application/json' } : {}), ...(options.headers || {}) }
  if (token) headers.Authorization = `Bearer ${token}`
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers })
  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    const detail = typeof data.detail === 'string' ? data.detail : data.message
    throw new Error(detail || `请求失败（HTTP ${response.status}）`)
  }
  return data
}

export async function register(email, password) {
  return request('/api/auth/register', { method: 'POST', body: JSON.stringify({ email, password }) })
}

export async function login(email, password) {
  const data = await request('/api/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) })
  if (data.access_token) saveToken(data.access_token)
  return data
}

export async function getCurrentUser() {
  const data = await request('/api/auth/me')
  return data.user || data
}

export async function logout() {
  try {
    return await request('/api/auth/logout', { method: 'POST' })
  } finally {
    clearToken()
  }
}
