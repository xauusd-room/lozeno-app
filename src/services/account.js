
const API_BASE = 'https://lozeno-api.aaa375750526.workers.dev'

async function request(path, options = {}) {
  const token = localStorage.getItem('lozeno_access_token')

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
    const detail =
      typeof data.detail === 'string'
        ? data.detail
        : data.message

    throw new Error(detail || `请求失败（HTTP ${response.status}）`)
  }

  return data
}

// ==================== 个人资料 ====================

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
    body: JSON.stringify({
      current_password,
      new_password
    })
  })
}

// ==================== 订单管理 ====================

export async function fetchOrders() {
  const data = await request('/api/orders')
  return data.orders || []
}

export async function fetchOrder(orderNo) {
  const data = await request(
    `/api/orders/${encodeURIComponent(orderNo)}`
  )

  return data.order || data
}

export async function cancelOrder(orderNo) {
  const data = await request(
    `/api/orders/${encodeURIComponent(orderNo)}/status`,
    {
      method: 'PATCH',
      body: JSON.stringify({
        status: 'cancelled'
      })
    }
  )

  return data.order || data
}

export async function fetchOrderLicense(orderNo) {
  const data = await request(
    `/api/orders/${encodeURIComponent(orderNo)}/license`
  )

  return data.license || data
}

// ==================== 授权管理 ====================

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
      body: JSON.stringify({
        account: String(account || '').trim()
      })
    }
  )

  if (data.success === false) {
    throw new Error(data.message || '授权绑定失败')
  }

  return data.license || data
}

// ==================== EA 文件下载 ====================

export async function downloadOrderEA(orderNo) {
  const token = localStorage.getItem('lozeno_access_token')

  if (!token) {
    throw new Error('请先登录')
  }

  const response = await fetch(
    `${API_BASE}/api/orders/${encodeURIComponent(orderNo)}/download`,
    {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: 'application/octet-stream'
      }
    }
  )

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))

    throw new Error(
      data.detail ||
      data.message ||
      `下载失败（HTTP ${response.status}）`
    )
  }

  const blob = await response.blob()
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')

  link.href = url
  link.download = `LOZENO-EA-${orderNo}.ex5`

  document.body.appendChild(link)
  link.click()
  link.remove()

  window.setTimeout(() => {
    URL.revokeObjectURL(url)
  }, 1000)
}
