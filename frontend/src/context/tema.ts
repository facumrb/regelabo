import { useSyncExternalStore } from 'react'

// Tema claro/oscuro (decisión 024). index.html lo fija antes de pintar; acá se cambia y se avisa a quien dibuja.
export type Tema = 'claro' | 'oscuro'

const raiz = document.documentElement
const oyentes = new Set<() => void>()
const avisar = () => oyentes.forEach((oyente) => oyente())

function elegido(): string | null {
  try {
    return localStorage.getItem('tema')
  } catch {
    return null // modo privado o almacenamiento bloqueado: sigue al sistema
  }
}

export function cambiarTema(tema: Tema) {
  raiz.dataset.tema = tema
  try {
    localStorage.setItem('tema', tema)
  } catch {
    // sin almacenamiento, el cambio dura hasta recargar
  }
  avisar()
}

// Mientras el usuario no elija uno, acompaña los cambios del sistema
matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
  if (elegido()) return
  raiz.dataset.tema = e.matches ? 'oscuro' : 'claro'
  avisar()
})

export function useTema(): Tema {
  return useSyncExternalStore(
    (oyente) => {
      oyentes.add(oyente)
      return () => oyentes.delete(oyente)
    },
    () => (raiz.dataset.tema === 'oscuro' ? 'oscuro' : 'claro'),
  )
}

/**
 * Imprime en tema claro aunque se use el oscuro: Plotly dibuja con colores fijos y en papel blanco no se
 * leerían. No cambia la preferencia guardada.
 */
export async function imprimirEnClaro() {
  const anterior = raiz.dataset.tema
  if (anterior === 'oscuro') {
    raiz.dataset.tema = 'claro'
    avisar()
    await new Promise((listo) => setTimeout(listo, 400)) // que los gráficos se vuelvan a dibujar
  }
  window.print() // en los navegadores de escritorio, espera a que se cierre el diálogo
  if (anterior === 'oscuro') {
    raiz.dataset.tema = anterior
    avisar()
  }
}
