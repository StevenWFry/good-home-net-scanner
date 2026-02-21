import { api } from '../lib/api.js'

export default function ScanButton({ scanning, onScanStart }) {
  async function handleClick() {
    try {
      await api.startScan()
      onScanStart?.()
    } catch (err) {
      console.error('Failed to start scan:', err)
    }
  }

  return (
    <button
      onClick={handleClick}
      disabled={scanning}
      className="btn-primary flex items-center gap-2"
    >
      {scanning ? (
        <>
          <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
          </svg>
          Scanning…
        </>
      ) : (
        <>
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8"/>
            <path d="m21 21-4.3-4.3"/>
          </svg>
          Scan Network
        </>
      )}
    </button>
  )
}
