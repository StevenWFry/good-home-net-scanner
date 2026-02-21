import DeviceCard from './DeviceCard.jsx'

export default function DeviceGrid({ devices }) {
  if (!devices || devices.length === 0) {
    return (
      <div className="text-center py-20 text-gray-600">
        <p className="text-4xl mb-4">📡</p>
        <p className="text-lg font-medium text-gray-500">No devices found yet</p>
        <p className="text-sm mt-1">Click Scan to discover devices on your network</p>
      </div>
    )
  }

  const online = devices.filter(d => d.is_online)
  const offline = devices.filter(d => !d.is_online)

  return (
    <div className="space-y-6">
      {online.length > 0 && (
        <section>
          <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
            Online — {online.length}
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
            {online.map(d => <DeviceCard key={d.id} device={d} />)}
          </div>
        </section>
      )}
      {offline.length > 0 && (
        <section>
          <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
            Offline — {offline.length}
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3 opacity-60">
            {offline.map(d => <DeviceCard key={d.id} device={d} />)}
          </div>
        </section>
      )}
    </div>
  )
}
