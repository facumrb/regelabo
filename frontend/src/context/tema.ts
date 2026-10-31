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
