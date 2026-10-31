import { useMemo, useRef, useState } from 'react'
import Plot from 'react-plotly.js'
import Plotly from 'plotly.js/dist/plotly' // es UMD: solo trae export por defecto
import type { Data, Layout } from 'plotly.js'
import { botonTexto } from './estilos'

/**
 * Gráfico de Plotly con el título en HTML y herramientas con texto (decisión 024): la barra de íconos de
 * Plotly, en inglés y sin rótulos, no se entendía. Ampliar sigue siendo arrastrar sobre el gráfico.
 */
export default function Grafico({ titulo, archivo, data, layout }: {
  titulo: string; archivo: string; data: Data[]; layout: Partial<Layout>
}) {
  const [vista, setVista] = useState(0) // al cambiar, el gráfico se vuelve a crear con su vista inicial
  const grafico = useRef<HTMLElement | null>(null)
  // Plotly guarda el zoom dentro del layout que recibe: cada vista nueva parte de una copia intacta
  const layoutVista = useMemo(() => structuredClone(layout), [layout, vista])

  return (
    <div className="space-y-2">
      <h3 className="font-semibold text-tinta">{titulo}</h3>
      <div className="w-full h-96">
        <Plot key={vista} data={data} layout={layoutVista} config={{ responsive: true, displayModeBar: false }}
          onInitialized={(_, div) => { grafico.current = div }}
          style={{ width: '100%', height: '100%' }} />
      </div>
      <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
        <p className="mr-auto text-xs text-tenue">Arrastrá sobre el gráfico para ampliar una zona.</p>
        <button type="button" className={botonTexto} onClick={() => setVista((v) => v + 1)}>Restablecer vista</button>
        <button type="button" className={botonTexto}
          onClick={() => grafico.current && Plotly.downloadImage(grafico.current, { format: 'png', filename: archivo })}>
          Descargar imagen
        </button>
      </div>
    </div>
  )
}
