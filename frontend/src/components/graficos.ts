import { useMemo } from 'react'
import type { Layout } from 'plotly.js'
import { useTema } from '../context/tema'

// Plotly no lee variables CSS: se leen los colores del tema actual y se vuelven a leer al cambiarlo
export interface ColoresGrafico {
  tinta: string
  tenue: string
  linea: string
  panel: string
  acento: string
  c2: string
  c3: string
  /** Colores de las curvas, en orden fijo: cada entidad conserva el suyo */
  series: string[]
}

// Segunda pista además del color: en tema claro algunas series tienen poco contraste con el fondo
export const TRAZOS = ['solid', 'dash', 'dot', 'dashdot', 'longdash', 'longdashdot'] as const

function leer(): ColoresGrafico {
  const estilo = getComputedStyle(document.documentElement)
  const v = (nombre: string) => estilo.getPropertyValue(nombre).trim()
  return {
    tinta: v('--tinta'), tenue: v('--tenue'), linea: v('--linea'), panel: v('--panel'),
    acento: v('--acento'), c2: v('--c2'), c3: v('--c3'),
    series: [1, 2, 3, 4, 5, 6].map((n) => v(`--s${n}`)),
  }
}

export function useColoresGrafico(): ColoresGrafico {
  const tema = useTema()
  return useMemo(leer, [tema])
}

/** Fondo transparente, texto y grilla del tema; cada gráfico agrega sus ejes y márgenes. */
export function layoutBase(c: ColoresGrafico, extra: Partial<Layout> = {}): Partial<Layout> {
  const eje = { gridcolor: c.linea, zerolinecolor: c.linea, linecolor: c.linea }
  return {
    autosize: true,
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    font: { color: c.tenue, family: 'Inter, sans-serif', size: 12 },
    hoverlabel: { bgcolor: c.panel, bordercolor: c.linea, font: { color: c.tinta } },
    // la leyenda va debajo del título del eje X: quien la use necesita margen inferior (~90 px)
    legend: { orientation: 'h', yanchor: 'top', y: -0.2, bgcolor: 'transparent' },
    ...extra,
    xaxis: { ...eje, ...extra.xaxis },
    yaxis: { ...eje, ...extra.yaxis },
  }
}

/** Título de gráfico con el color del texto. */
export const titulo = (c: ColoresGrafico, texto: string) => ({ text: texto, font: { color: c.tinta, size: 14 } })
