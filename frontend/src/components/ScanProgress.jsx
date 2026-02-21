const PHASE_LABELS = {
  discover: 'Discovering hosts',
  vendor: 'Looking up vendors',
  portscan: 'Scanning ports',
  done: 'Scan complete',
}

export default function ScanProgress({ scanState }) {
  if (!scanState || scanState.status === 'idle') return null

  const { status, phase, current, total, device, message, error } = scanState

  const pct = total > 0 ? Math.round((current / total) * 100) : 0
  const label = PHASE_LABELS[phase] || phase || 'Scanning'

  if (status === 'error') {
    return (
      <div className="card p-4 border-red-800 bg-red-950/30">
        <p className="text-red-400 text-sm font-medium">Scan failed</p>
        <p className="text-red-500/70 text-xs mt-0.5">{error}</p>
      </div>
    )
  }

  if (status === 'done') {
    return (
      <div className="card p-4 border-emerald-800/50 bg-emerald-950/20">
        <p className="text-emerald-400 text-sm font-medium">
          ✓ {message || 'Scan complete'}
        </p>
      </div>
    )
  }

  return (
    <div className="card p-4 space-y-2">
      <div className="flex items-center justify-between text-sm">
        <span className="text-gray-300 font-medium">{label}</span>
        <span className="text-gray-500 text-xs">
          {current}/{total || '?'}
        </span>
      </div>

      <div className="w-full bg-gray-800 rounded-full h-1.5 overflow-hidden">
        <div
          className="h-full bg-brand-500 rounded-full transition-all duration-300"
          style={{ width: `${total > 0 ? pct : 30}%` }}
        />
      </div>

      {device && (
        <p className="text-xs text-gray-500 font-mono truncate">{device}</p>
      )}
    </div>
  )
}
