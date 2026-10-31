import Icono from './Icono'
import { botonSecundario, etiqueta, panel } from './estilos'
import type { ResultadoSimulacion } from '../services/tiposSimulacion'

export default function ResultsSummary({ result }: { result: ResultadoSimulacion | null }) {
  if (!result) return null

  const efr = result.efr_value_uv
  const p = result.parameters_used

  // Clasificación clínica didáctica según valor de EFR
  let statusBadge = { label: 'Respuesta Neural Robusta (Normal)', punto: 'bg-emerald-500' }

  if (efr < 0.08) {
    statusBadge = { label: 'Sincronización Neural Severamente Degradada', punto: 'bg-rose-500' }
  } else if (efr < 0.18) {
    statusBadge = { label: 'Respuesta Atenuada (Pérdida / Sinaptopatía)', punto: 'bg-amber-500' }
  }

  const exportJSON = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(result, null, 2))
    const downloadAnchor = document.createElement('a')
    downloadAnchor.setAttribute("href", dataStr)
    downloadAnchor.setAttribute("download", `simulacion_${p?.poles_profile || 'auditiva'}.json`)
    document.body.appendChild(downloadAnchor)
    downloadAnchor.click()
    downloadAnchor.remove()
  }

  return (
    <div className={`${panel} p-5 md:p-6 space-y-6`}>
      {/* Encabezado y estado */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-linea">
        <div>
          <span className={etiqueta}>Biomarcador Cuantitativo</span>
          <h3 className="text-lg md:text-xl font-semibold text-tinta">Envelope Following Response (EFR)</h3>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <span className="inline-flex items-center gap-2 text-sm text-tinta">
            <span className={`w-2 h-2 rounded-full ${statusBadge.punto}`} aria-hidden="true" />
            {statusBadge.label}
          </span>
          <button onClick={exportJSON} className={botonSecundario} title="Descargar datos crudos en formato JSON">
            <Icono nombre="descargar" tamano={16} />JSON
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
        {/* EFR total */}
        <div className="md:col-span-2 p-4 md:p-5 rounded-xl bg-acento-suave">
          <span className="text-sm text-tenue block mb-1">Amplitud EFR Acumulada</span>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl md:text-4xl font-semibold font-mono tracking-tight text-tinta">{efr.toFixed(4)}</span>
            <span className="text-sm font-medium text-tenue">µV</span>
          </div>
          <p className="text-sm text-tenue mt-2 leading-relaxed">
            Suma de armónicos del estímulo modulado. Refleja la sincronización neural del tronco auditivo (W1+W3+W5).
          </p>
        </div>

        <div className="p-4 rounded-xl border border-linea flex flex-col justify-between gap-2">
          <span className="text-sm text-tenue">Tiempo de Cálculo</span>
          <div>
            <div className="flex items-baseline gap-1">
              <span className="text-2xl font-semibold font-mono text-tinta">{result.execution_time_seconds}</span>
              <span className="text-sm text-tenue">seg</span>
            </div>
            <span className="text-xs font-mono text-c2">Acelerado por C (tridiag.so)</span>
          </div>
        </div>

        <div className="p-4 rounded-xl border border-linea flex flex-col justify-between gap-2 min-w-0">
          <span className="text-sm text-tenue">Condición Simulada</span>
          <div className="space-y-0.5 font-mono">
            <div className="text-sm font-semibold text-tinta truncate">{p?.poles_profile}</div>
            <div className="text-xs text-tenue">{p?.carrier_freq} Hz @ {p?.spl_level} dB</div>
            <div className="text-xs text-tenue">nH: {p?.nH} | nM: {p?.nM} | nL: {p?.nL}</div>
          </div>
        </div>
      </div>

      {/* Desglose de armónicos */}
      <section className="space-y-2.5">
        <h4 className={etiqueta}>Contribución de Armónicos FFT (Frecuencia de Modulación {p?.f_mod} Hz)</h4>
        <div className="grid grid-cols-2 xl:grid-cols-4 gap-2.5">
          {result.harmonics?.map(h => (
            <div key={h.harmonic_order} className="p-3 rounded-xl border border-linea">
              <div className="flex justify-between gap-2 text-xs text-tenue">
                <span>Armónico {h.harmonic_order}</span>
                <span className="font-mono">{h.frequency_hz} Hz</span>
              </div>
              <div className="mt-0.5 font-mono font-semibold text-tinta">
                {h.amplitude_uv.toFixed(4)} <span className="text-xs font-normal text-tenue">µV</span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
