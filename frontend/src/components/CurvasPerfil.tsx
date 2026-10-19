import Plot from 'react-plotly.js'
import type { Data, Layout } from 'plotly.js'
import type { PerfilAuditivo } from '../services/tiposSimulacion'

const hz = (f: number) => (f >= 1000 ? `${f / 1000} kHz` : `${f} Hz`)

/** Cartel corto antes de simular (Q20): null si el modelo representa todo el perfil. */
export function avisoPrevio(perfil: PerfilAuditivo): string | null {
  if (perfil.frecuencias_recortadas.length === 0) return null
  return `Este perfil supera lo que el modelo puede representar en ${perfil.frecuencias_recortadas.map(hz).join(', ')}: se simulará recortado.`
}

/** Detalle del recorte, frecuencia por frecuencia: "en 4 kHz se simulan 35 dB HL de los 60 pedidos". */
export function avisoRecorte(perfil: PerfilAuditivo): string | null {
  if (perfil.frecuencias_recortadas.length === 0) return null
  const detalle = perfil.frecuencias_recortadas.map((f) => {
    const pedida = perfil.curva_pedida.find((p) => p.frequency === f)?.hearing_loss_db
    const simulada = perfil.curva_simulada.find((p) => p.frequency === f)?.hearing_loss_db
    return `en ${hz(f)} se simulan ${simulada} dB HL de los ${pedida} pedidos`
  })
  return 'El modelo solo representa la pérdida de las células ciliadas externas, y su techo depende de la ' +
    `frecuencia: ${detalle.join('; ')}. Los resultados corresponden a la curva simulada.`
}

interface Props {
  perfil: PerfilAuditivo
  /** Alto del gráfico en px */
  alto?: number
  /** Muestra el aviso completo debajo del gráfico */
  conAviso?: boolean
}

/** Audiograma chico con la curva pedida y la que realmente se simula, superpuestas. */
export default function CurvasPerfil({ perfil, alto = 200, conAviso = false }: Props) {
  const curva = (puntos: PerfilAuditivo['curva_pedida'], nombre: string, color: string, trazo: 'solid' | 'dot') => ({
    x: puntos.map((p) => p.frequency),
    y: puntos.map((p) => p.hearing_loss_db),
    type: 'scatter' as const,
    mode: 'lines+markers' as const,
    name: nombre,
    line: { color, width: 2, dash: trazo },
    marker: { color, size: 7 },
    hovertemplate: '%{x} Hz: %{y} dB HL<extra>' + nombre + '</extra>',
  })
  const recortado = perfil.frecuencias_recortadas.length > 0
  const data: Data[] = recortado
    ? [curva(perfil.curva_pedida, 'Pedida', '#ef4444', 'dot'), curva(perfil.curva_simulada, 'Simulada', '#22d3ee', 'solid')]
    : [curva(perfil.curva_simulada, 'Pedida y simulada', '#22d3ee', 'solid')]

  const layout: Partial<Layout> = {
    autosize: true,
    height: alto,
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'rgba(17, 24, 39, 0.6)',
    font: { color: '#94a3b8', family: 'Inter, sans-serif', size: 10 },
    xaxis: {
      type: 'log',
      tickvals: [250, 500, 1000, 2000, 4000, 8000],
      ticktext: ['250', '500', '1k', '2k', '4k', '8k'],
      gridcolor: 'rgba(255, 255, 255, 0.08)',
    },
    yaxis: {
      title: { text: 'dB HL' },
      autorange: 'reversed', // como en un audiograma: 0 dB arriba
      range: [-10, 100],
      dtick: 20,
      gridcolor: 'rgba(255, 255, 255, 0.08)',
    },
    margin: { l: 40, r: 10, t: 10, b: 25 },
    showlegend: true,
    legend: { orientation: 'h', y: -0.25, font: { size: 10 } },
  }

  const aviso = conAviso ? avisoRecorte(perfil) : null
  return (
    <div className="space-y-2">
      <div role="img" aria-label={`Audiograma del perfil ${perfil.etiqueta}`}>
        <Plot
          data={data}
          layout={layout}
          config={{ responsive: true, displayModeBar: false }}
          style={{ width: '100%' }}
        />
      </div>
      {aviso && (
        <div role="status" className="p-3 rounded-lg bg-amber-950/50 border border-amber-500/40 text-amber-200 text-xs">
          ⚠ {aviso}
        </div>
      )}
    </div>
  )
}
