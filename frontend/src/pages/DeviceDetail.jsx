import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../lib/api.js'
import DeviceIcon from '../components/DeviceIcon.jsx'

const ICON_TYPES = ['router', 'phone', 'laptop', 'tv', 'printer', 'server', 'device']

function PortRow({ port }) {
  const isWellKnown = port.port <= 1023

  return (
    <tr className="border-b border-gray-800 hover:bg-gray-800/40 transition-colors">
      <td className="py-2.5 px-3 font-mono text-sm text-brand-400 whitespace-nowrap">
        {port.port}/{port.protocol}
      </td>
      <td className="py-2.5 px-3 text-sm text-gray-300">{port.service || '—'}</td>
      <td className="py-2.5 px-3 text-sm text-gray-500 max-w-xs truncate">{port.version || '—'}</td>
      <td className="py-2.5 px-3">
        <span className={`text-xs px-1.5 py-0.5 rounded ${
          port.state === 'open'
            ? 'bg-emerald-500/10 text-emerald-400'
            : 'bg-gray-700 text-gray-500'
        }`}>
          {port.state}
        </span>
      </td>
    </tr>
  )
}

function InfoRow({ label, value, mono = false }) {
  if (!value) return null
  return (
    <div className="flex flex-col sm:flex-row sm:items-baseline gap-0.5 sm:gap-4 py-2.5 border-b border-gray-800">
      <dt className="text-xs text-gray-500 uppercase tracking-wider sm:w-28 flex-shrink-0">{label}</dt>
      <dd className={`text-sm ${mono ? 'font-mono text-brand-400' : 'text-gray-200'}`}>{value}</dd>
    </div>
  )
}

export default function DeviceDetail() {
  const { id } = useParams()
  const navigate = useNavigate()

  const [device, setDevice] = useState(null)
  const [loading, setLoading] = useState(true)
  const [nickname, setNickname] = useState('')
  const [editingNickname, setEditingNickname] = useState(false)
  const [saving, setSaving] = useState(false)
  const [iconType, setIconType] = useState('device')

  useEffect(() => {
    api.getDevice(id)
      .then(data => {
        setDevice(data)
        setNickname(data.nickname || '')
        setIconType(data.icon_type || 'device')
      })
      .catch(() => navigate('/'))
      .finally(() => setLoading(false))
  }, [id, navigate])

  async function saveNickname() {
    setSaving(true)
    try {
      const updated = await api.patchDevice(id, { nickname: nickname || null })
      setDevice(updated)
      setEditingNickname(false)
    } finally {
      setSaving(false)
    }
  }

  async function saveIconType(newType) {
    setIconType(newType)
    try {
      const updated = await api.patchDevice(id, { icon_type: newType })
      setDevice(updated)
    } catch {
      setIconType(device.icon_type)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-brand-600 border-t-transparent rounded-full animate-spin"/>
      </div>
    )
  }

  if (!device) return null

  const displayName = device.nickname || device.hostname || device.ip
  const openPorts = device.ports?.filter(p => p.state === 'open') ?? []

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-950/80 backdrop-blur sticky top-0 z-10">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 h-14 flex items-center gap-3">
          <button onClick={() => navigate('/')} className="btn-ghost text-sm flex items-center gap-1">
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
            Back
          </button>
          <span className="text-gray-700">/</span>
          <span className="text-sm font-medium text-gray-300 truncate">{displayName}</span>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 sm:px-6 py-6 space-y-6">

        {/* Device hero */}
        <div className="card p-6 flex items-start gap-5">
          {/* Icon picker */}
          <div className="flex-shrink-0">
            <div
              className={`w-16 h-16 rounded-2xl flex items-center justify-center ${
                device.is_online ? 'bg-brand-900/60 text-brand-300' : 'bg-gray-800 text-gray-600'
              }`}
            >
              <DeviceIcon type={iconType} className="w-8 h-8" />
            </div>
          </div>

          <div className="flex-1 min-w-0 space-y-3">
            {/* Nickname editor */}
            <div>
              {editingNickname ? (
                <div className="flex items-center gap-2">
                  <input
                    autoFocus
                    value={nickname}
                    onChange={e => setNickname(e.target.value)}
                    onKeyDown={e => {
                      if (e.key === 'Enter') saveNickname()
                      if (e.key === 'Escape') setEditingNickname(false)
                    }}
                    placeholder="Enter nickname…"
                    className="bg-gray-800 border border-brand-600 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none flex-1"
                  />
                  <button onClick={saveNickname} disabled={saving} className="btn-primary text-sm py-1.5">
                    Save
                  </button>
                  <button onClick={() => setEditingNickname(false)} className="btn-ghost text-sm">
                    Cancel
                  </button>
                </div>
              ) : (
                <div className="flex items-center gap-2 group">
                  <h1 className="text-xl font-bold text-white truncate">{displayName}</h1>
                  <button
                    onClick={() => setEditingNickname(true)}
                    className="opacity-0 group-hover:opacity-100 btn-ghost p-1 transition-opacity"
                    title="Edit nickname"
                  >
                    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                    </svg>
                  </button>
                </div>
              )}
              {device.nickname && device.hostname && device.hostname !== device.nickname && (
                <p className="text-sm text-gray-500 mt-0.5">{device.hostname}</p>
              )}
            </div>

            {/* Status */}
            <div className="flex items-center gap-2 flex-wrap">
              <span className={`inline-flex items-center gap-1.5 text-xs font-medium px-2 py-1 rounded-full ${
                device.is_online ? 'bg-emerald-500/10 text-emerald-400' : 'bg-gray-700/50 text-gray-500'
              }`}>
                <span className={`w-1.5 h-1.5 rounded-full ${device.is_online ? 'bg-emerald-400' : 'bg-gray-500'}`}/>
                {device.is_online ? 'Online' : 'Offline'}
              </span>
              {openPorts.length > 0 && (
                <span className="text-xs text-gray-500 bg-gray-800 px-2 py-1 rounded-full">
                  {openPorts.length} open port{openPorts.length !== 1 ? 's' : ''}
                </span>
              )}
            </div>

            {/* Icon type picker */}
            <div className="flex items-center gap-1.5 flex-wrap">
              {ICON_TYPES.map(t => (
                <button
                  key={t}
                  onClick={() => saveIconType(t)}
                  title={t}
                  className={`p-1.5 rounded-lg transition-colors ${
                    iconType === t
                      ? 'bg-brand-800/60 text-brand-300'
                      : 'text-gray-600 hover:text-gray-400 hover:bg-gray-800'
                  }`}
                >
                  <DeviceIcon type={t} className="w-4 h-4" />
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Device info */}
        <div className="card p-5">
          <h2 className="text-sm font-semibold text-gray-400 mb-3">Device Info</h2>
          <dl>
            <InfoRow label="IP Address" value={device.ip} mono />
            <InfoRow label="MAC" value={device.mac} mono />
            <InfoRow label="Vendor" value={device.vendor} />
            <InfoRow label="Hostname" value={device.hostname} />
            <InfoRow label="OS" value={device.os} />
            <InfoRow label="First seen" value={device.first_seen ? new Date(device.first_seen).toLocaleString() : null} />
            <InfoRow label="Last seen" value={device.last_seen ? new Date(device.last_seen).toLocaleString() : null} />
          </dl>
        </div>

        {/* Ports table */}
        {device.ports?.length > 0 && (
          <div className="card overflow-hidden">
            <div className="px-5 py-4 border-b border-gray-800">
              <h2 className="text-sm font-semibold text-gray-400">
                Open Ports
                <span className="ml-2 text-xs text-gray-600 font-normal">
                  {openPorts.length} open
                </span>
              </h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-800">
                    <th className="text-left py-2 px-3 text-xs text-gray-500 font-medium">Port</th>
                    <th className="text-left py-2 px-3 text-xs text-gray-500 font-medium">Service</th>
                    <th className="text-left py-2 px-3 text-xs text-gray-500 font-medium">Version</th>
                    <th className="text-left py-2 px-3 text-xs text-gray-500 font-medium">State</th>
                  </tr>
                </thead>
                <tbody>
                  {device.ports.map(p => (
                    <PortRow key={p.id} port={p} />
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {device.ports?.length === 0 && (
          <div className="card p-6 text-center text-gray-600">
            <p className="text-sm">No open ports detected</p>
          </div>
        )}
      </main>
    </div>
  )
}
