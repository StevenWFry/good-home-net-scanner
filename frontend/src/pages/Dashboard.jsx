import { useState, useEffect, useCallback } from 'react'
import { api } from '../lib/api.js'
import { useWebSocket } from '../lib/useWebSocket.js'
import DeviceGrid from '../components/DeviceGrid.jsx'
import ScanButton from '../components/ScanButton.jsx'
import ScanProgress from '../components/ScanProgress.jsx'

export default function Dashboard() {
  const [devices, setDevices] = useState([])
  const [scanState, setScanState] = useState(null)
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('')

  const scanning = scanState?.status === 'running'

  const loadDevices = useCallback(async () => {
    try {
      const data = await api.getDevices()
      setDevices(data)
    } catch (err) {
      console.error('Failed to load devices:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  // Load devices on mount and poll for initial scan status
  useEffect(() => {
    loadDevices()
    api.getScanStatus().then(setScanState).catch(() => {})
  }, [loadDevices])

  // Reload devices when scan finishes
  useEffect(() => {
    if (scanState?.status === 'done') {
      loadDevices()
    }
  }, [scanState?.status, loadDevices])

  // WebSocket for live progress
  useWebSocket(useCallback((msg) => {
    setScanState(msg)
  }, []))

  const filteredDevices = filter
    ? devices.filter(d =>
        [d.ip, d.hostname, d.vendor, d.mac, d.nickname]
          .filter(Boolean)
          .some(v => v.toLowerCase().includes(filter.toLowerCase()))
      )
    : devices

  const onlineCount = devices.filter(d => d.is_online).length

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-950/80 backdrop-blur sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="text-lg font-bold text-white">🏠 Home Network</span>
            {!loading && (
              <span className="text-xs text-gray-500 bg-gray-800 px-2 py-0.5 rounded-full">
                {onlineCount} online
              </span>
            )}
          </div>

          <div className="flex items-center gap-3">
            {/* Search */}
            <div className="relative hidden sm:block">
              <input
                type="text"
                placeholder="Filter devices…"
                value={filter}
                onChange={e => setFilter(e.target.value)}
                className="bg-gray-800 border border-gray-700 rounded-lg pl-8 pr-3 py-1.5 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-brand-600 w-48"
              />
              <svg
                className="absolute left-2.5 top-2 w-3.5 h-3.5 text-gray-600"
                viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
              >
                <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
              </svg>
            </div>

            <ScanButton scanning={scanning} onScanStart={() => {}} />
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-6 space-y-4">
        {/* Progress bar */}
        {scanState && scanState.status !== 'idle' && (
          <ScanProgress scanState={scanState} />
        )}

        {/* Mobile filter */}
        <div className="sm:hidden">
          <input
            type="text"
            placeholder="Filter devices…"
            value={filter}
            onChange={e => setFilter(e.target.value)}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-brand-600"
          />
        </div>

        {loading ? (
          <div className="text-center py-20 text-gray-600">
            <div className="inline-block w-8 h-8 border-2 border-brand-600 border-t-transparent rounded-full animate-spin mb-4"/>
            <p>Loading…</p>
          </div>
        ) : (
          <DeviceGrid devices={filteredDevices} />
        )}
      </main>
    </div>
  )
}
