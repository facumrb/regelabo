import React, { useState } from 'react'
import Plot from 'react-plotly.js'

export default function PlotsPanel({ result }) {
  const [waveMode, setWaveMode] = useState('all') // 'total' | 'separate' | 'all'

  if (!result) {
    return (
      <div className="glass-panel rounded-2xl p-12 text-center border border-dashed border-slate-800 space-y-3">
        <div className="w-12 h-12 mx-auto rounded-full bg-slate-800/80 flex items-center justify-center text-slate-400">
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
          </svg>
        </div>
        <h3 className="text-base font-semibold text-slate-300">Sin simulación activa</h3>
        <p className="text-xs text-slate-500 max-w-sm mx-auto">
          Configurá los parámetros en el panel izquierdo y hacé clic en "Ejecutar Simulación Biológica" para visualizar el espectro de Fourier y las ondas ABR.
        </p>
      </div>
    )
  }

  const { fft_spectrum, abr_waves, harmonics } = result

  // ---- Configuración Gráfico 1: FFT Spectrum ----
  const fftData = [
    {
      x: fft_spectrum.frequencies,
      y: fft_spectrum.amplitudes,
      type: 'scatter',
      mode: 'lines',
      name: 'Espectro FFT',
      line: { color: '#38bdf8', width: 2 },
      fill: 'tozeroy',
      fillcolor: 'rgba(56, 189, 248, 0.08)',
      hoverinfo: 'x+y',
      hovertemplate: '%{x:.1f} Hz: %{y:.4f} µV<extra></extra>',
    },
    {
      x: harmonics.map(h => h.frequency_hz),
      y: harmonics.map(h => h.amplitude_uv),
      type: 'scatter',
      mode: 'markers+text',
      name: 'Armónicos clave',
      text: harmonics.map(h => `H${h.harmonic_order} (${h.amplitude_uv.toFixed(3)} µV)`),
      textposition: 'top center',
      textfont: { size: 10, color: '#f8fafc' },
      marker: {
        color: '#f43f5e',
        size: 9,
        symbol: 'circle',
        line: { color: '#ffffff', width: 1.5 }
      },
      hoverinfo: 'text'
    }
  ]

  const fftLayout = {
    title: {
      text: '<b>Espectro FFT del EFR (Armónicos de Sincronización)</b>',
      font: { color: '#f1f5f9', size: 14 }
    },
    autosize: true,
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'rgba(17, 24, 39, 0.6)',
    font: { color: '#94a3b8', family: 'Inter, sans-serif' },
    xaxis: {
      title: 'Frecuencia (Hz)',
      range: [0, 600],
      gridcolor: 'rgba(255, 255, 255, 0.06)',
      zerolinecolor: 'rgba(255, 255, 255, 0.1)',
    },
    yaxis: {
      title: 'Amplitud (µV)',
      gridcolor: 'rgba(255, 255, 255, 0.06)',
      zerolinecolor: 'rgba(255, 255, 255, 0.1)',
    },
    margin: { l: 50, r: 25, t: 45, b: 45 },
    showlegend: true,
    legend: {
      x: 0.75,
      y: 0.95,
      bgcolor: 'rgba(15, 23, 42, 0.8)',
      bordercolor: 'rgba(255, 255, 255, 0.1)',
      borderwidth: 1
    }
  }

  // ---- Configuración Gráfico 2: Ondas ABR ----
  const timeMs = abr_waves.time_ms
  const abrTraces = []

  if (waveMode === 'all' || waveMode === 'total') {
    abrTraces.push({
      x: timeMs,
      y: abr_waves.efr_wave,
      type: 'scatter',
      mode: 'lines',
      name: 'EFR Total (W1+W3+W5)',
      line: { color: '#38bdf8', width: 2 },
      hovertemplate: '%{x:.2f} ms: %{y:.4f} µV<extra></extra>',
    })
  }

  if (waveMode === 'all' || waveMode === 'separate') {
    abrTraces.push(
      {
        x: timeMs,
        y: abr_waves.w1,
        type: 'scatter',
        mode: 'lines',
        name: 'Onda I (Nervio AN)',
        line: { color: '#10b981', width: 1.5, dash: 'dot' },
        hovertemplate: '%{x:.2f} ms: %{y:.4f} µV<extra></extra>',
      },
      {
        x: timeMs,
        y: abr_waves.w3,
        type: 'scatter',
        mode: 'lines',
        name: 'Onda III (Núcleo CN)',
        line: { color: '#f59e0b', width: 1.5, dash: 'dash' },
        hovertemplate: '%{x:.2f} ms: %{y:.4f} µV<extra></extra>',
      },
      {
        x: timeMs,
        y: abr_waves.w5,
        type: 'scatter',
        mode: 'lines',
        name: 'Onda V (Colículo IC)',
        line: { color: '#c084fc', width: 1.5 },
        hovertemplate: '%{x:.2f} ms: %{y:.4f} µV<extra></extra>',
      }
    )
  }

  const abrLayout = {
    title: {
      text: '<b>Respuesta en el Dominio Temporal (Ondas ABR & EFR)</b>',
      font: { color: '#f1f5f9', size: 14 }
    },
    autosize: true,
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'rgba(17, 24, 39, 0.6)',
    font: { color: '#94a3b8', family: 'Inter, sans-serif' },
    xaxis: {
      title: 'Tiempo (ms)',
      range: [0, 50], // Primeros 50 ms para inspección fina
      gridcolor: 'rgba(255, 255, 255, 0.06)',
      zerolinecolor: 'rgba(255, 255, 255, 0.1)',
    },
    yaxis: {
      title: 'Amplitud (µV)',
      gridcolor: 'rgba(255, 255, 255, 0.06)',
      zerolinecolor: 'rgba(255, 255, 255, 0.1)',
    },
    margin: { l: 50, r: 25, t: 45, b: 45 },
    showlegend: true,
    legend: {
      x: 0.7,
      y: 0.95,
      bgcolor: 'rgba(15, 23, 42, 0.8)',
      bordercolor: 'rgba(255, 255, 255, 0.1)',
      borderwidth: 1
    }
  }

  return (
    <div className="space-y-6">
      
      {/* Gráfico 1: FFT */}
      <div className="glass-panel rounded-2xl p-5 shadow-xl">
        <div className="w-full h-80">
          <Plot
            data={fftData}
            layout={fftLayout}
            config={{ responsive: true, displayModeBar: true, displaylogo: false }}
            style={{ width: '100%', height: '100%' }}
          />
        </div>
      </div>

      {/* Gráfico 2: Formas de onda ABR con selector de trazas */}
      <div className="glass-panel rounded-2xl p-5 shadow-xl space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-2">
          <span className="text-xs text-slate-400 font-medium">
            Descomposición de Componentes Neurales
          </span>
          <div className="flex space-x-1.5 bg-dark-800 p-1 rounded-lg border border-slate-800">
            <button
              onClick={() => setWaveMode('all')}
              className={`px-2.5 py-1 text-xs rounded-md transition ${
                waveMode === 'all' ? 'bg-cyan-500/20 text-cyan-300 font-semibold' : 'text-slate-400 hover:text-white'
              }`}
            >
              Todas las ondas
            </button>
            <button
              onClick={() => setWaveMode('total')}
              className={`px-2.5 py-1 text-xs rounded-md transition ${
                waveMode === 'total' ? 'bg-cyan-500/20 text-cyan-300 font-semibold' : 'text-slate-400 hover:text-white'
              }`}
            >
              EFR Total
            </button>
            <button
              onClick={() => setWaveMode('separate')}
              className={`px-2.5 py-1 text-xs rounded-md transition ${
                waveMode === 'separate' ? 'bg-cyan-500/20 text-cyan-300 font-semibold' : 'text-slate-400 hover:text-white'
              }`}
            >
              W1 / W3 / W5
            </button>
          </div>
        </div>

        <div className="w-full h-80">
          <Plot
            data={abrTraces}
            layout={abrLayout}
            config={{ responsive: true, displayModeBar: true, displaylogo: false }}
            style={{ width: '100%', height: '100%' }}
          />
        </div>
      </div>

    </div>
  )
}
