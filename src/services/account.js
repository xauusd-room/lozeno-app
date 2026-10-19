
const API_BASE = 'https://lozeno-api.aaa375750526.workers.dev'
const TOKEN_KEY = 'lozeno_access_token'

async function request(path, options = {}) {
  const token = localStorage.getItem(TOKEN_KEY)

  const headers = {
    Accept: 'application/json',
    ...(options.body ? { 'Content-Type': 'application/json' } : {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {})
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers
  })

  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('登录已失效，请重新登录')
    }

    const detail = typeof data.detail === 'string'
      ? data.detail
      : data.message

    throw new Error(detail || `请求失败（HTTP ${response.status}）`)
  }

  return data
}

function jsonBody(data) {
  return JSON.stringify(data)
}

// 个人资料
export async function fetchProfile() {
  const data = await request('/api/auth/me')
  return data.user || data
}

export async function updateProfile(profile) {
  const data = await request('/api/auth/profile', {
    method: 'PATCH',
    body: jsonBody({
      display_name: profile.display_name,
      phone: profile.phone
    })
  })

  return data.user || data
}

export async function changePassword(currentPassword, newPassword) {
  return request('/api/auth/change-password', {
    method: 'POST',
    body: jsonBody({
      current_password: currentPassword,
      new_password: newPassword
    })
  })
}

// 我的订单
export async function fetchOrders() {
  const data = await request('/api/orders')
  return data.orders || []
}

export async function fetchOrder(orderNo) {
  const data = await request(`/api/orders/${encodeURIComponent(orderNo)}`)
  return data.order || data
}

export async function cancelOrder(orderNo) {
  return request(`/api/orders/${encodeURIComponent(orderNo)}/status`, {
    method: 'PATCH',
    body: jsonBody({ status: 'cancelled' })
  })
}

export async function fetchOrderLicense(orderNo) {
  const data = await request(
    `/api/orders/${encodeURIComponent(orderNo)}/license`
  )
  return data.license || data
}

// 我的授权
export async function fetchLicenses() {
  const data = await request('/api/licenses')
  return data.licenses || []
}

export async function fetchLicense(licenseKey) {
  const data = await request(
    `/api/licenses/${encodeURIComponent(licenseKey)}`
  )
  return data.license || data
}

export async function bindLicense(licenseKey, account) {
  const data = await request(
    `/api/licenses/${encodeURIComponent(licenseKey)}/bind`,
    {
      method: 'POST',
      body: jsonBody({ account })
    }
  )

  return data.license || data
}
