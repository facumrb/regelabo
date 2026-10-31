import type { ReactNode } from 'react'

// Íconos de trazo del prototipo (docs/prototipo-ui/index.html), decorativos: el texto de al lado da el significado
const TRAZOS = {
  marca: <path d="M3 12h2l2-6 3 12 3-9 2 6 2-3h4" />,
  inicio: <><path d="M3 11.5 12 4l9 7.5" /><path d="M5 10v10h14V10" /></>,
  simular: <polygon points="7 4 20 12 7 20 7 4" />,
  casos: <><circle cx="9" cy="8" r="3.5" /><path d="M2.5 20a6.5 6.5 0 0 1 13 0" /><path d="M16 4.5a3.5 3.5 0 0 1 0 7" /><path d="M18 14a6 6 0 0 1 3.5 5.5" /></>,
  historial: <><path d="M3 12a9 9 0 1 0 3-6.7" /><path d="M3 4v5h5" /><path d="M12 8v4l3 2" /></>,
  abajo: <path d="m6 9 6 6 6-6" />,
  atras: <><path d="M19 12H5" /><path d="m12 19-7-7 7-7" /></>,
  cuenta: <><circle cx="12" cy="8" r="4" /><path d="M4 21a8 8 0 0 1 16 0" /></>,
  luna: <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />,
  sol: <><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" /></>,
  salir: <><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" /><path d="m16 17 5-5-5-5" /><path d="M21 12H9" /></>,
  subir: <><path d="M12 16V4" /><path d="m7 9 5-5 5 5" /><path d="M5 20h14" /></>,
  descargar: <><path d="M12 4v12" /><path d="m7 11 5 5 5-5" /><path d="M5 20h14" /></>,
} satisfies Record<string, ReactNode>

export type NombreIcono = keyof typeof TRAZOS

export default function Icono({ nombre, tamano = 20, className }: { nombre: NombreIcono; tamano?: number; className?: string }) {
  return (
    <svg width={tamano} height={tamano} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75}
      strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" className={className}>
      {TRAZOS[nombre]}
    </svg>
  )
}
