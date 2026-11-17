import { useMemo, useRef, useState } from 'react'
import Plot from 'react-plotly.js'
import Plotly from 'plotly.js/dist/plotly' // es UMD: solo trae export por defecto
import type { Data, Layout } from 'plotly.js'
import { botonTexto } from './estilos'

// En pantallas táctiles arrastrar para ampliar atrapaba el dedo y no dejaba bajar por la página: ahí se apaga
// y se ofrece verlo en pantalla completa. shortcut: se mide al cargar; si se conecta un mouse, hay que recargar.
const TACTIL = matchMedia('(pointer: coarse)').matches

/**
 * Gráfico de Plotly con el título en HTML y herramientas con texto (decisión 024): la barra de íconos de
 * Plotly, en inglés y sin rótulos, no se entendía. Con mouse, ampliar sigue siendo arrastrar sobre el gráfico.
 */
export default function Grafico({ titulo, archivo, data, layout }: {
  titulo: string; archivo: string; data: Data[]; layout: Partial<Layout>
}) {
  const [vista, setVista] = useState(0) // al cambiar, el gráfico se vuelve a crear con su vista inicial
  const grafico = useRef<HTMLElement | null>(null)
  // Plotly guarda el zoom dentro del layout que recibe: cada vista nueva parte de una copia intacta
  const layoutVista = useMemo(
    () => ({ ...structuredClone(layout), ...(TACTIL ? { dragmode: false as const } : {}) }), [layout, vista])
  const caja = useRef<HTMLDivElement>(null)

  const pantallaCompleta = async () => {
    try {
      await caja.current?.requestFullscreen()
      // Girar a horizontal donde el navegador lo permite (Android); se suelta solo al salir
      const orientacion = screen.orientation as ScreenOrientation & { lock?: (o: string) => Promise<void> }
      await orientacion.lock?.('landscape')
    } catch {
      // sin pantalla completa o sin giro: el gráfico queda como estaba
    }
  }

  return (
    <div className="space-y-2">
      <h3 className="font-semibold text-tinta">{titulo}</h3>
      <div ref={caja} className="relative w-full h-60 md:h-80 lg:h-96 [&:fullscreen]:h-full [&:fullscreen]:bg-panel [&:fullscreen]:p-2">
        <button type="button" onClick={() => document.exitFullscreen()}
          className={`${botonTexto} hidden [:fullscreen>&]:inline-flex absolute top-2 right-2 z-10 bg-panel border border-linea`}>
          Salir de pantalla completa
        </button>
        <Plot key={vista} data={data} layout={layoutVista} config={{ responsive: true, displayModeBar: false }}
          onInitialized={(_, div) => { grafico.current = div }}
          style={{ width: '100%', height: '100%' }} />
      </div>
      <div className="flex flex-wrap items-center gap-x-2 gap-y-1 print:hidden">
        <p className="mr-auto text-xs text-tenue">
          {TACTIL ? 'Tocá el gráfico para ver los valores.' : 'Arrastrá sobre el gráfico para ampliar una zona.'}
        </p>
        {TACTIL && document.fullscreenEnabled && (
          <button type="button" className={botonTexto} onClick={pantallaCompleta}>Pantalla completa</button>
        )}
        {!TACTIL && (
          <button type="button" className={botonTexto} onClick={() => setVista((v) => v + 1)}>Restablecer vista</button>
        )}
        <button type="button" className={botonTexto}
          onClick={() => grafico.current && Plotly.downloadImage(grafico.current, { format: 'png', filename: archivo })}>
          Descargar imagen
        </button>
      </div>
    </div>
  )
}
