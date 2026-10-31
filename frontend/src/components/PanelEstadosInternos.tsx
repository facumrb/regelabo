import { useEffect, useState } from 'react'
import type { Data, Layout } from 'plotly.js'
import { mensajeDeError } from '../services/auth'
import { simulacionesApi } from '../services/simulaciones'
import type { EstadosFibra, EstadosInternos } from '../services/tiposSimulacion'
import { panel } from './estilos'
import Grafico from './Grafico'
import { layoutBase, TRAZOS, useColoresGrafico, type ColoresGrafico } from './graficos'

// Siete figuras de estados internos del modelo (decisión 023). Las magnitudes vienen del modelo: acá solo se
// eligen canales y se dibujan. Cada figura declara canal, muestreo, ventana y unidades (nunca "diagnóstico", RN9).

const columna = (serie: number[][], j: number) => serie.map((fila) => fila[j])
const tiempoMs = (n: number, fs: number) => Array.from({ length: n }, (_, i) => (i * 1000) / fs)
// La reserva w(t) se escala por 14/60 solo para compararla visualmente con q(t)
const ESCALA_RESERVA = 14 / 60

function layout(c: ColoresGrafico, ejeY: string, extra: Partial<Layout> = {}): Partial<Layout> {
  return layoutBase(c, {
    margin: { l: 60, r: 60, t: 16, b: 100 },
    ...extra,
    xaxis: { title: { text: 'Tiempo (ms)' }, ...extra.xaxis },
    yaxis: { title: { text: ejeY }, ...extra.yaxis },
  })
}

function Figura({ numero, titulo, data, layout: l, nota }: {
  numero: number; titulo: string; data: Data[]; layout: Partial<Layout>; nota: string
}) {
  return (
    <div className={`${panel} p-3 md:p-5 space-y-2`}>
      <Grafico titulo={titulo} archivo={`estados-internos-figura-${numero}`} data={data} layout={l} />
      <p className="text-sm text-tenue">Figura {numero}. {nota}</p>
    </div>
  )
}

function Selector({ opciones, valor, onCambio }: {
  opciones: { etiqueta: string; valor: number }[]; valor: number; onCambio: (v: number) => void
}) {
  return (
    <div className="flex flex-wrap gap-1.5">
      {opciones.map((o) => (
        <button key={o.valor} onClick={() => onCambio(o.valor)} aria-pressed={valor === o.valor}
          className={`min-h-[36px] px-3 rounded-full border text-xs font-medium transition ${
            valor === o.valor ? 'bg-acento-suave border-acento text-tinta' : 'border-linea text-tenue hover:text-tinta'
          }`}>
          {o.etiqueta}
        </button>
      ))}
    </div>
  )
}

function Figuras({ estados }: { estados: EstadosInternos }) {
  const { canales, polo_shera, ihc, vesiculas, cn_ic } = estados
  const c = useColoresGrafico()
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
  // Color y trazo de la serie `n` de la paleta (orden fijo: cada curva conserva el suyo)
  const linea = (x: number[], y: number[], name: string, n: number, extra: Partial<Data> = {}): Data =>
    ({ x, y, type: 'scatter', mode: 'lines', name, line: { color: c.series[n], width: 1.5, dash: TRAZOS[n] }, ...extra } as Data)

  // El color dice el rol (excitatoria, inhibitoria, neta) y el trazo el núcleo: CN continuo, IC a guiones
  const tronco = (exc: number[][], inh: number[][], nombre: string, trazo: string): Data[] => {
    const e = columna(exc, canalCorto)
    const i = columna(inh, canalCorto)
    const estilo = (n: number, width = 1.5) => ({ line: { color: c.series[n], width, dash: trazo } })
    return [
      linea(tTronco, e, `${nombre} excitatoria`, 0, estilo(0)),
      linea(tTronco, i.map((v) => -v), `${nombre} inhibitoria (−)`, 1, estilo(1)),
      linea(tTronco, e.map((v, k) => v - i[k]), `${nombre} neta`, 2, estilo(2, 2)),
    ]
  }

  return (
    <div className="space-y-6">
      <Figura numero={1} titulo="Polo de Shera (control de ganancia OHC)"
        data={[{
          x: tShera, y: polo_shera.frecuencia_caracteristica_hz, z: zShera, type: 'heatmap', colorscale: 'Viridis',
          colorbar: { title: { text: 'Polo' } },
        } as Data]}
        layout={layout(c, 'Frecuencia característica (Hz)', {
          yaxis: { title: { text: 'Frecuencia característica (Hz)' }, type: 'log' },
        })}
        nota={`Polo de Shera por tiempo y frecuencia característica (adimensional): representa el control de ` +
          `ganancia de las OHC, no el movimiento basilar. Todos los canales · ` +
          `${muestreo(polo_shera.fs_hz, [0, Math.round(tShera.length * 1000 / polo_shera.fs_hz)])}.`} />

      <div className="space-y-2">
        <span className="text-sm text-tenue">Canal de las figuras 2 y 7</span>
        <Selector valor={canalCorto} onCambio={setCanalCorto}
          opciones={ihc.canales.map((c, i) => ({ etiqueta: `${canales[c].frecuencia_solicitada_hz} Hz`, valor: i }))} />
      </div>

      <Figura numero={2} titulo="Corrientes y potencial de la célula ciliada interna"
        data={[
          linea(tIhc, columna(ihc.imet_na, canalCorto), 'I_MET (nA)', 0),
          linea(tIhc, columna(ihc.ikf_na, canalCorto), 'I_kf (nA)', 1),
          linea(tIhc, columna(ihc.iks_na, canalCorto), 'I_ks (nA)', 2),
          linea(tIhc, columna(ihc.vm_mv, canalCorto), 'Vm (mV)', 3, { yaxis: 'y2' }),
        ]}
        layout={layout(c, 'Corriente (nA)', {
          yaxis2: { title: { text: 'Vm (mV)' }, overlaying: 'y', side: 'right', showgrid: false },
        })}
        nota={`${describir(indiceCorto)} · ${muestreo(ihc.fs_hz, ihc.ventana_ms)} · corrientes en nA, Vm en mV.`} />

      <div className="space-y-2">
        <span className="text-sm text-tenue">Canal de las figuras 3 a 6</span>
        <Selector valor={canal} onCambio={setCanal}
          opciones={canales.map((c, i) => ({ etiqueta: `${c.frecuencia_solicitada_hz} Hz`, valor: i }))} />
      </div>

      <Figura numero={3} titulo="Vesículas disponibles q(t) por tipo de fibra"
        data={fibras.map(([nombre, f], k) => linea(tVes, columna(f.q, canal), `q(t) ${nombre}`, k))}
        layout={layout(c, 'Vesículas')}
        nota={`${describir(canal)} · ${muestreo(vesiculas.fs_hz, vesiculas.ventana_ms)}. Describe la dinámica de ` +
          `una fibra representativa de cada tipo: no está ponderada por la cantidad de fibras.`} />

      {fibras.map(([nombre, f], k) => (
        <Figura key={nombre} numero={4 + k} titulo={`Estados sinápticos de las fibras ${nombre}`}
          data={[
            linea(tVes, columna(f.q, canal), 'q(t) disponibles', 0),
            linea(tVes, columna(f.w, canal).map((v) => v * ESCALA_RESERVA), 'w(t) reserva (×14/60)', 1),
            linea(tVes, columna(f.a, canal), 'A(t) fuera del período refractario', 2, { yaxis: 'y2' }),
          ]}
          layout={layout(c, 'Vesículas', {
            yaxis2: { title: { text: 'Fracción disponible' }, overlaying: 'y', side: 'right', showgrid: false },
          })}
          nota={`${describir(canal)} · ${muestreo(vesiculas.fs_hz, vesiculas.ventana_ms)}. La reserva w(t) se ` +
            `multiplica por 14/60 solo para compararla con q(t). Dinámica por fibra, no recuentos.`} />
      ))}

      <Figura numero={7} titulo="Núcleo coclear y colículo inferior"
        data={[
          ...tronco(cn_ic.cn_exc, cn_ic.cn_inh, 'CN', 'solid'),
          ...tronco(cn_ic.ic_exc, cn_ic.ic_inh, 'IC', 'dash'),
        ]}
        layout={layout(c, 'Actividad (spikes/s)')}
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
        aria-expanded={abierto}
        className={`${panel} w-full min-h-[44px] px-5 py-4 flex items-center justify-between gap-4 text-left hover:border-tenue`}>
        <span>
          <span className="block font-semibold text-tinta">Estados internos</span>
          <span className="block text-sm text-tenue">
            Siete figuras de la cadena auditiva simulada: cóclea, célula ciliada interna, sinapsis y tronco.
          </span>
        </span>
        <span className="text-tenue text-sm shrink-0">{abierto ? 'Ocultar' : 'Mostrar'}</span>
      </button>
      {abierto && error && <p role="alert" className="text-sm text-rose-700 dark:text-rose-300">{error}</p>}
      {abierto && !error && !estados && <p className="text-sm text-tenue">Cargando estados internos…</p>}
      {abierto && estados && <Figuras estados={estados} />}
    </div>
  )
}
