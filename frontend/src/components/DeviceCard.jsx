import { useNavigate } from 'react-router-dom'
import DeviceIcon from './DeviceIcon.jsx'

function StatusBadge({ online }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 text-xs font-medium px-2 py-0.5 rounded-full ${
        online
          ? 'bg-emerald-500/10 text-emerald-400'
          : 'bg-gray-700/50 text-gray-500'
      }`}
    >
      <span
        className={`w-1.5 h-1.5 rounded-full ${online ? 'bg-emerald-400 animate-pulse' : 'bg-gray-500'}`}
      />
      {online ? 'Online' : 'Offline'}
    </span>
  )
}

export default function DeviceCard({ device }) {
  const navigate = useNavigate()
  const displayName = device.nickname || device.hostname || device.ip

  return (
    <button
      onClick={() => navigate(`/device/${device.id}`)}
      className="card p-4 text-left hover:border-brand-700 hover:bg-gray-800/50 transition-all group w-full"
    >
      <div className="flex items-start justify-between gap-2 mb-3">
        <div
          className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
            device.is_online
              ? 'bg-brand-900/60 text-brand-400'
              : 'bg-gray-800 text-gray-600'
          }`}
        >
          <DeviceIcon type={device.icon_type} className="w-5 h-5" />
        </div>
        <StatusBadge online={device.is_online} />
      </div>

      <div className="space-y-1">
        <p className="font-semibold text-gray-100 truncate group-hover:text-white">
          {displayName}
        </p>
        {device.nickname && device.hostname && (
          <p className="text-xs text-gray-500 truncate">{device.hostname}</p>
        )}
        <p className="text-sm font-mono text-brand-400">{device.ip}</p>
      </div>

      <div className="mt-3 pt-3 border-t border-gray-800 space-y-1">
        {device.vendor && (
          <p className="text-xs text-gray-500 truncate">{device.vendor}</p>
        )}
        {device.mac && (
          <p className="text-xs font-mono text-gray-600 truncate">{device.mac}</p>
        )}
        {device.ports?.length > 0 && (
          <p className="text-xs text-gray-600">
            {device.ports.filter(p => p.state === 'open').length} open port
            {device.ports.filter(p => p.state === 'open').length !== 1 ? 's' : ''}
          </p>
        )}
      </div>
    </button>
  )
}
