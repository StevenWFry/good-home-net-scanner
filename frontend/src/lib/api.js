const BASE = '/api'

async function request(path, options = {}) {
  const res = await fetch(BASE + path, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText)
    throw new Error(`${res.status}: ${text}`)
  }
  return res.json()
}

export const api = {
  getDevices: () => request('/devices'),
  getDevice: (id) => request(`/devices/${id}`),
  patchDevice: (id, data) =>
    request(`/devices/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  getDeviceHistory: (id) => request(`/devices/${id}/history`),
  startScan: () => request('/scan', { method: 'POST' }),
  getScanStatus: () => request('/scan/status'),
}
