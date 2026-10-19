const API_BASE = 'https://lozeno-api.aaa375750526.workers.dev'

async function request(path, options = {}) {
  const token = localStorage.getItem('lozeno_access_token')
  const headers = {
    Accept: 'application/json',
    ...(options.body ? { 'Content-Type': 'application/json' } : {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {})
  }
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers })
  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    const detail = typeof data.detail === 'string' ? data.detail : data.message
    throw new Error(detail || `请求失败（HTTP ${response.status}）`)
  }
  return data
}

export async function fetchProfile() {
  const data = await request('/api/auth/me')
  return data.user || data
}

export async function updateProfile(profile) {
  const data = await request('/api/auth/profile', {
    method: 'PATCH',
    body: JSON.stringify(profile)
  })
  return data.user || data
}

export async function changePassword(current_password, new_password) {
  return request('/api/auth/change-password', {
    method: 'POST',
    body: JSON.stringify({ current_password, new_password })
  })
}
