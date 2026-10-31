import { useState } from 'react'
import type { Data } from 'plotly.js'
import { panel, vacio } from './estilos'
import Grafico from './Grafico'
import { layoutBase, TRAZOS, useColoresGrafico } from './graficos'
import type { ResultadoSimulacion } from '../services/tiposSimulacion'

type Ondas = 'all' | 'total' | 'separate'

export default function PlotsPanel({ result }: { result: ResultadoSimulacion | null }) {
  const [waveMode, setWaveMode] = useState<Ondas>('all')
  const c = useColoresGrafico()

  if (!result) {
    return (
      <div className={`${vacio} space-y-2`}>
        <h3 className="font-semibold text-tinta">Sin simulación activa</h3>
        <p className="text-sm max-w-sm mx-auto">
          Configurá los parámetros en el panel izquierdo y hacé clic en "Ejecutar Simulación Biológica" para visualizar el espectro de Fourier y las ondas ABR.
        </p>
      </div>
    )
  }

  const { fft_spectrum, abr_waves, harmonics } = result
  const tiempo = '%{x:.2f} ms: %{y:.4f} µV<extra></extra>'

  // ---- Gráfico 1: espectro FFT ----
  const fftData: Data[] = [
    {
      x: fft_spectrum.frequencies,
      y: fft_spectrum.amplitudes,
      type: 'scatter',
      mode: 'lines',
      name: 'Espectro FFT',
      line: { color: c.acento, width: 2 },
      fill: 'tozeroy',
      fillcolor: `${c.acento}1a`,
      hoverinfo: 'x+y',
      hovertemplate: '%{x:.1f} Hz: %{y:.4f} µV<extra></extra>',
    },
    {
      x: harmonics.map(h => h.frequency_hz),
      y: harmonics.map(h => h.amplitude_uv),
      type: 'scatter',
      mode: 'text+markers',
      name: 'Armónicos clave',
      text: harmonics.map(h => `H${h.harmonic_order} (${h.amplitude_uv.toFixed(3)} µV)`),
      textposition: 'top center',
      textfont: { size: 10, color: c.tinta },
      marker: { color: c.c2, size: 9, symbol: 'circle', line: { color: c.panel, width: 1.5 } },
      hoverinfo: 'text',
    },
  ]

  // ---- Gráfico 2: ondas ABR ----
  const abrTraces: Data[] = []
  if (waveMode === 'all' || waveMode === 'total') {
    abrTraces.push({
      x: abr_waves.time_ms, y: abr_waves.efr_wave, type: 'scatter', mode: 'lines', name: 'EFR Total (W1+W3+W5)',
      line: { color: c.series[0], width: 2, dash: TRAZOS[0] }, hovertemplate: tiempo,
    })
  }
  if (waveMode === 'all' || waveMode === 'separate') {
    abrTraces.push(
      { x: abr_waves.time_ms, y: abr_waves.w1, type: 'scatter', mode: 'lines', name: 'Onda I (Nervio AN)',
        line: { color: c.series[1], width: 1.5, dash: TRAZOS[1] }, hovertemplate: tiempo },
      { x: abr_waves.time_ms, y: abr_waves.w3, type: 'scatter', mode: 'lines', name: 'Onda III (Núcleo CN)',
        line: { color: c.series[2], width: 1.5, dash: TRAZOS[2] }, hovertemplate: tiempo },
      { x: abr_waves.time_ms, y: abr_waves.w5, type: 'scatter', mode: 'lines', name: 'Onda V (Colículo IC)',
        line: { color: c.series[3], width: 1.5, dash: TRAZOS[3] }, hovertemplate: tiempo },
    )
  }

  const margen = { l: 52, r: 16, t: 16, b: 90 }
  const modos: [Ondas, string][] = [['all', 'Todas las ondas'], ['total', 'EFR Total'], ['separate', 'W1 / W3 / W5']]

  return (
    <div className="space-y-6">
      {/* Gráfico 1: FFT */}
      <div className={`${panel} p-3 md:p-5`}>
        <Grafico titulo="Espectro FFT del EFR (Armónicos de Sincronización)" archivo="espectro-fft-efr" data={fftData}
            layout={layoutBase(c, {
              xaxis: { title: { text: 'Frecuencia (Hz)' }, range: [0, 600] },
              yaxis: { title: { text: 'Amplitud (µV)' } },
              margin: margen,
            })} />
      </div>

      {/* Gráfico 2: formas de onda ABR con selector de trazas */}
      <div className={`${panel} p-3 md:p-5 space-y-3`}>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-linea">
          <span className="text-sm text-tenue">Descomposición de Componentes Neurales</span>
          <div className="flex flex-wrap gap-1.5" role="group" aria-label="Ondas que se muestran">
            {modos.map(([v, texto]) => (
              <button key={v} onClick={() => setWaveMode(v)} aria-pressed={waveMode === v}
                className={`min-h-[36px] px-3 rounded-full border text-xs font-medium transition ${
                  waveMode === v ? 'bg-acento-suave border-acento text-tinta' : 'border-linea text-tenue hover:text-tinta'
                }`}>
                {texto}
              </button>
            ))}
          </div>
        </div>
        <Grafico titulo="Respuesta en el Dominio Temporal (Ondas ABR & EFR)" archivo="ondas-abr-efr" data={abrTraces}
            layout={layoutBase(c, {
              xaxis: { title: { text: 'Tiempo (ms)' }, range: [0, 50] }, // primeros 50 ms para inspección fina
              yaxis: { title: { text: 'Amplitud (µV)' } },
              margin: margen,
            })} />
      </div>
    </div>
  )
}
