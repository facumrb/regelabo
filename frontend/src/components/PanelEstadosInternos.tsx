import { useEffect, useState } from 'react'
import Plot from 'react-plotly.js'
import type { Data, Layout } from 'plotly.js'
import { mensajeDeError } from '../services/auth'
import { simulacionesApi } from '../services/simulaciones'
import type { EstadosFibra, EstadosInternos } from '../services/tiposSimulacion'

// Siete figuras de estados internos del modelo (decisión 023). Las magnitudes vienen del modelo: acá solo se
// eligen canales y se dibujan. Cada figura declara canal, muestreo, ventana y unidades (nunca "diagnóstico", RN9).

const columna = (serie: number[][], j: number) => serie.map((fila) => fila[j])
const tiempoMs = (n: number, fs: number) => Array.from({ length: n }, (_, i) => (i * 1000) / fs)
// La reserva w(t) se escala por 14/60 solo para compararla visualmente con q(t)
const ESCALA_RESERVA = 14 / 60

function layout(titulo: string, ejeY: string, extra: Partial<Layout> = {}): Partial<Layout> {
  return {
    title: { text: `<b>${titulo}</b>`, font: { color: '#f1f5f9', size: 13 } },
    autosize: true,
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'rgba(17, 24, 39, 0.6)',
    font: { color: '#94a3b8', family: 'Inter, sans-serif' },
    xaxis: { title: { text: 'Tiempo (ms)' }, gridcolor: 'rgba(255, 255, 255, 0.06)' },
    yaxis: { title: { text: ejeY }, gridcolor: 'rgba(255, 255, 255, 0.06)' },
    margin: { l: 60, r: 60, t: 45, b: 45 },
    legend: { orientation: 'h', y: -0.25 },
    ...extra,
  }
}

function Figura({ numero, data, layout: l, nota }: { numero: number; data: Data[]; layout: Partial<Layout>; nota: string }) {
  return (
    <div className="glass-panel rounded-2xl p-5 shadow-xl space-y-2">
      <div className="w-full h-80">
        <Plot data={data} layout={l} config={{ responsive: true, displaylogo: false }}
          style={{ width: '100%', height: '100%' }} />
      </div>
      <p className="text-xs text-slate-500">Figura {numero}. {nota}</p>
    </div>
  )
}

function Selector({ opciones, valor, onCambio }: {
  opciones: { etiqueta: string; valor: number }[]; valor: number; onCambio: (v: number) => void
}) {
  return (
    <div className="flex space-x-1.5 bg-dark-800 p-1 rounded-lg border border-slate-800 w-fit">
      {opciones.map((o) => (
        <button key={o.valor} onClick={() => onCambio(o.valor)}
          className={`px-2.5 py-1 text-xs rounded-md transition ${
            valor === o.valor ? 'bg-cyan-500/20 text-cyan-300 font-semibold' : 'text-slate-400 hover:text-white'
          }`}>
          {o.etiqueta}
        </button>
      ))}
    </div>
  )
}

function Figuras({ estados }: { estados: EstadosInternos }) {
  const { canales, polo_shera, ihc, vesiculas, cn_ic } = estados
  const [canal, setCanal] = useState(0) // índice en `canales`, para las figuras 3 a 6
  const [canalCorto, setCanalCorto] = useState(0) // índice en `ihc.canales` / `cn_ic.canales`, figuras 2 y 7

  const describir = (i: number) =>
    `Frecuencia solicitada ${canales[i].frecuencia_solicitada_hz} Hz · ` +
    `característica efectiva ${canales[i].frecuencia_caracteristica_hz.toFixed(0)} Hz`
  const muestreo = (fs: number, ventana: number[]) =>
    `Muestreo ${fs / 1000} kHz · ventana ${ventana[0]}–${ventana[1]} ms`

  // Figura 1: polo de Shera, matriz [tiempo][canal] → heatmap con el canal en el eje vertical
  const tShera = tiempoMs(polo_shera.valores.length, polo_shera.fs_hz)
  const zShera = polo_shera.frecuencia_caracteristica_hz.map((_, j) => columna(polo_shera.valores, j))

  const tIhc = tiempoMs(ihc.imet_na.length, ihc.fs_hz)
  const tVes = tiempoMs(vesiculas.hsr.q.length, vesiculas.fs_hz)
  const tTronco = tiempoMs(cn_ic.cn_exc.length, cn_ic.fs_hz)
  const indiceCorto = ihc.canales[canalCorto]

  const fibras: [string, EstadosFibra][] = [['HSR', vesiculas.hsr], ['MSR', vesiculas.msr], ['LSR', vesiculas.lsr]]
  const linea = (x: number[], y: number[], name: string, color: string, extra: Partial<Data> = {}): Data =>
    ({ x, y, type: 'scatter', mode: 'lines', name, line: { color, width: 1.5 }, ...extra } as Data)

  const tronco = (exc: number[][], inh: number[][], nombre: string, colores: string[]): Data[] => {
    const e = columna(exc, canalCorto)
    const i = columna(inh, canalCorto)
    return [
      linea(tTronco, e, `${nombre} excitatoria`, colores[0]),
      linea(tTronco, i.map((v) => -v), `${nombre} inhibitoria (−)`, colores[1]),
      linea(tTronco, e.map((v, k) => v - i[k]), `${nombre} neta`, colores[2], { line: { color: colores[2], width: 2 } }),
    ]
  }

  return (
    <div className="space-y-6">
      <Figura numero={1}
        data={[{
          x: tShera, y: polo_shera.frecuencia_caracteristica_hz, z: zShera, type: 'heatmap', colorscale: 'Viridis',
          colorbar: { title: { text: 'Polo' } },
        } as Data]}
        layout={layout('Polo de Shera (control de ganancia OHC)', 'Frecuencia característica (Hz)', {
          yaxis: { title: { text: 'Frecuencia característica (Hz)' }, type: 'log' },
        })}
        nota={`Polo de Shera por tiempo y frecuencia característica (adimensional): representa el control de ` +
          `ganancia de las OHC, no el movimiento basilar. Todos los canales · ` +
          `${muestreo(polo_shera.fs_hz, [0, Math.round(tShera.length * 1000 / polo_shera.fs_hz)])}.`} />

      <div className="space-y-2">
        <span className="text-xs text-slate-400 font-medium">Canal de las figuras 2 y 7</span>
        <Selector valor={canalCorto} onCambio={setCanalCorto}
          opciones={ihc.canales.map((c, i) => ({ etiqueta: `${canales[c].frecuencia_solicitada_hz} Hz`, valor: i }))} />
      </div>

      <Figura numero={2}
        data={[
          linea(tIhc, columna(ihc.imet_na, canalCorto), 'I_MET (nA)', '#2196F3'),
          linea(tIhc, columna(ihc.ikf_na, canalCorto), 'I_kf (nA)', '#FF9800'),
          linea(tIhc, columna(ihc.iks_na, canalCorto), 'I_ks (nA)', '#f44336'),
          linea(tIhc, columna(ihc.vm_mv, canalCorto), 'Vm (mV)', '#e2e8f0', { yaxis: 'y2' }),
        ]}
        layout={layout('Corrientes y potencial de la célula ciliada interna', 'Corriente (nA)', {
          yaxis2: { title: { text: 'Vm (mV)' }, overlaying: 'y', side: 'right', showgrid: false },
        })}
        nota={`${describir(indiceCorto)} · ${muestreo(ihc.fs_hz, ihc.ventana_ms)} · corrientes en nA, Vm en mV.`} />

      <div className="space-y-2">
        <span className="text-xs text-slate-400 font-medium">Canal de las figuras 3 a 6</span>
        <Selector valor={canal} onCambio={setCanal}
          opciones={canales.map((c, i) => ({ etiqueta: `${c.frecuencia_solicitada_hz} Hz`, valor: i }))} />
      </div>

      <Figura numero={3}
        data={fibras.map(([nombre, f], k) => linea(tVes, columna(f.q, canal), `q(t) ${nombre}`,
          ['#22d3ee', '#a78bfa', '#f472b6'][k]))}
        layout={layout('Vesículas disponibles q(t) por tipo de fibra', 'Vesículas')}
        nota={`${describir(canal)} · ${muestreo(vesiculas.fs_hz, vesiculas.ventana_ms)}. Describe la dinámica de ` +
          `una fibra representativa de cada tipo: no está ponderada por la cantidad de fibras.`} />

      {fibras.map(([nombre, f], k) => (
        <Figura key={nombre} numero={4 + k}
          data={[
            linea(tVes, columna(f.q, canal), 'q(t) disponibles', '#22d3ee'),
            linea(tVes, columna(f.w, canal).map((v) => v * ESCALA_RESERVA), 'w(t) reserva (×14/60)', '#fbbf24',
              { line: { color: '#fbbf24', width: 1.5, dash: 'dash' } }),
            linea(tVes, columna(f.a, canal), 'A(t) fuera del período refractario', '#34d399', { yaxis: 'y2' }),
          ]}
          layout={layout(`Estados sinápticos de las fibras ${nombre}`, 'Vesículas', {
            yaxis2: { title: { text: 'Fracción disponible' }, overlaying: 'y', side: 'right', showgrid: false },
          })}
          nota={`${describir(canal)} · ${muestreo(vesiculas.fs_hz, vesiculas.ventana_ms)}. La reserva w(t) se ` +
            `multiplica por 14/60 solo para compararla con q(t). Dinámica por fibra, no recuentos.`} />
      ))}

      <Figura numero={7}
        data={[
          ...tronco(cn_ic.cn_exc, cn_ic.cn_inh, 'CN', ['#4ade80', '#fb7185', '#e2e8f0']),
          ...tronco(cn_ic.ic_exc, cn_ic.ic_inh, 'IC', ['#86efac', '#fda4af', '#94a3b8']),
        ]}
        layout={layout('Núcleo coclear y colículo inferior', 'Actividad (spikes/s)')}
        nota={`${describir(indiceCorto)} · ${muestreo(cn_ic.fs_hz, cn_ic.ventana_ms)} · actividad agregada en ` +
          `spikes/s. La respuesta neta es la excitatoria menos la inhibitoria.`} />
    </div>
  )
}

/** Panel colapsable: los datos pesan varios MB, se piden recién al abrirlo. */
export default function PanelEstadosInternos({ simulacionId }: { simulacionId: string }) {
  const [abierto, setAbierto] = useState(false)
  const [estados, setEstados] = useState<EstadosInternos | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setEstados(null)
    setError(null)
  }, [simulacionId])

  useEffect(() => {
    if (!abierto || estados || error) return
    let activo = true
    simulacionesApi.estadosInternos(simulacionId)
      .then((e) => { if (activo) setEstados(e) })
      .catch((err) => { if (activo) setError(mensajeDeError(err)) })
    return () => { activo = false }
  }, [abierto, estados, error, simulacionId])

  return (
    <div className="space-y-4">
      <button onClick={() => setAbierto(!abierto)}
        className="glass-panel w-full rounded-2xl px-5 py-4 flex items-center justify-between text-left">
        <span>
          <span className="block text-sm font-semibold text-slate-200">Estados internos</span>
          <span className="block text-xs text-slate-500">
            Siete figuras de la cadena auditiva simulada: cóclea, célula ciliada interna, sinapsis y tronco.
          </span>
        </span>
        <span className="text-slate-400 text-sm">{abierto ? 'Ocultar' : 'Mostrar'}</span>
      </button>
      {abierto && error && <p className="text-sm text-rose-300">{error}</p>}
      {abierto && !error && !estados && <p className="text-sm text-slate-400">Cargando estados internos…</p>}
      {abierto && estados && <Figuras estados={estados} />}
    </div>
  )
}
