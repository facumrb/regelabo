import React from 'react'

export default function ResultsSummary({ result }) {
  if (!result) return null

  const efr = result.efr_value_uv
  
  // Clasificación clínica didáctica según valor de EFR
  let statusBadge = {
    label: 'Respuesta Neural Robusta (Normal)',
    color: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
  }

  if (efr < 0.08) {
    statusBadge = {
      label: 'Sincronización Neural Severamente Degradada',
      color: 'bg-rose-500/15 text-rose-400 border-rose-500/30'
    }
  } else if (efr < 0.18) {
    statusBadge = {
      label: 'Respuesta Atenuada (Pérdida / Sinaptopatía)',
      color: 'bg-amber-500/15 text-amber-400 border-amber-500/30'
    }
  }

  const exportJSON = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(result, null, 2))
    const downloadAnchor = document.createElement('a')
    downloadAnchor.setAttribute("href", dataStr)
    downloadAnchor.setAttribute("download", `simulacion_${result.parameters_used?.poles_profile || 'auditiva'}.json`)
    document.body.appendChild(downloadAnchor)
    downloadAnchor.click()
    downloadAnchor.remove()
  }

  return (
    <div className="glass-panel rounded-2xl p-6 shadow-xl space-y-6">
      
      {/* Encabezado y badges */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Biomarcador Cuantitativo
          </span>
          <h3 className="text-xl font-bold text-white flex items-center space-x-2">
            <span>Envelope Following Response (EFR)</span>
          </h3>
        </div>

        <div className="flex items-center space-x-2">
          <span className={`text-xs px-3 py-1 rounded-full border font-medium ${statusBadge.color}`}>
            {statusBadge.label}
          </span>
          <button
            onClick={exportJSON}
            className="text-xs px-3 py-1 rounded-lg bg-dark-800 border border-slate-700 hover:border-cyan-500/50 text-slate-300 hover:text-cyan-300 transition flex items-center space-x-1"
            title="Descargar datos crudos en formato JSON"
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            <span>JSON</span>
          </button>
        </div>
      </div>

      {/* Hero Metric: Valor de EFR */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        
        {/* Tarjeta destacada de EFR Total */}
        <div className="md:col-span-2 p-5 rounded-xl bg-gradient-to-br from-cyan-950/40 via-dark-800 to-dark-800 border border-cyan-500/20 shadow-inner">
          <span className="text-xs text-slate-400 block mb-1">Amplitud EFR Acumulada</span>
          <div className="flex items-baseline space-x-2">
            <span className="text-4xl font-extrabold font-mono text-cyan-400 tracking-tight">
              {efr.toFixed(4)}
            </span>
            <span className="text-sm font-semibold text-cyan-300">µV</span>
          </div>
          <p className="text-[11px] text-slate-400 mt-2 leading-relaxed">
            Suma de armónicos del estímulo modulado. Refleja la sincronización neural del tronco auditivo (W1+W3+W5).
          </p>
        </div>

        {/* Tarjeta de tiempo de ejecución */}
        <div className="p-4 rounded-xl bg-dark-800/80 border border-slate-800 flex flex-col justify-between">
          <span className="text-xs text-slate-400">Tiempo de Cálculo</span>
          <div>
            <div className="flex items-baseline space-x-1">
              <span className="text-2xl font-bold font-mono text-white">
                {result.execution_time_seconds}
              </span>
              <span className="text-xs text-slate-400">seg</span>
            </div>
            <span className="text-[10px] text-emerald-400 font-mono">
              Acelerado por C (tridiag.so)
            </span>
          </div>
        </div>

        {/* Tarjeta de parámetros usados */}
        <div className="p-4 rounded-xl bg-dark-800/80 border border-slate-800 flex flex-col justify-between">
          <span className="text-xs text-slate-400">Condición Simulada</span>
          <div className="space-y-0.5 text-xs font-mono">
            <div className="text-cyan-300 font-semibold truncate">
              {result.parameters_used?.poles_profile}
            </div>
            <div className="text-slate-400 text-[11px]">
              {result.parameters_used?.carrier_freq} Hz @ {result.parameters_used?.spl_level} dB
            </div>
            <div className="text-slate-500 text-[10px]">
              nH: {result.parameters_used?.nH} | nM: {result.parameters_used?.nM} | nL: {result.parameters_used?.nL}
            </div>
          </div>
        </div>

      </div>

      {/* Desglose de armónicos */}
      <div>
        <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2.5">
          Contribución de Armónicos FFT (Frecuencia de Modulación {result.parameters_used?.f_mod} Hz)
        </h4>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {result.harmonics?.map(h => (
            <div key={h.harmonic_order} className="p-3 rounded-lg bg-dark-800/60 border border-slate-800">
              <div className="flex justify-between items-center text-xs mb-1">
                <span className="text-slate-400 font-medium">Armónico {h.harmonic_order}</span>
                <span className="font-mono text-slate-500 text-[10px]">{h.frequency_hz} Hz</span>
              </div>
              <div className="text-base font-bold font-mono text-slate-200">
                {h.amplitude_uv.toFixed(4)} <span className="text-xs text-slate-500 font-normal">µV</span>
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  )
}
