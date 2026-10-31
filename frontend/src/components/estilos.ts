// Clases compartidas con los colores de la paleta (decisión 024): cambian solas con el tema
const base = 'inline-flex items-center justify-center gap-2 min-h-[44px] px-4 rounded-lg text-sm font-medium ' +
  'transition disabled:opacity-50 disabled:cursor-not-allowed'

export const botonPrimario = `${base} bg-acento text-acento-tinta border border-acento hover:brightness-110`

export const botonSecundario = `${base} bg-panel text-tinta border border-linea hover:border-tenue`

export const botonTexto = `${base} text-tenue hover:text-tinta`

export const entrada =
  'w-full min-h-[44px] px-3 py-2 rounded-lg bg-panel border border-linea text-base md:text-sm text-tinta ' +
  'placeholder:text-tenue focus:outline-none focus:ring-2 focus:ring-acento focus:border-transparent ' +
  'disabled:opacity-60'

export const panel = 'bg-panel border border-linea rounded-2xl'

/** Lista vacía o resultado pendiente. */
export const vacio = 'border border-dashed border-linea rounded-2xl p-8 text-center text-tenue'

/** Rótulo en mayúsculas chicas sobre un bloque ("1 · Caso y perfil"). */
export const etiqueta = 'text-xs font-medium uppercase tracking-wider text-tenue'

// Avisos: colores semánticos que no son de la paleta, con su versión oscura
export const avisoAtencion =
  'bg-amber-50 border-amber-300 text-amber-900 dark:bg-amber-950/40 dark:border-amber-500/30 dark:text-amber-200'
export const avisoError =
  'bg-rose-50 border-rose-300 text-rose-900 dark:bg-rose-950/40 dark:border-rose-500/30 dark:text-rose-200'
export const avisoOk =
  'bg-emerald-50 border-emerald-300 text-emerald-900 dark:bg-emerald-950/40 dark:border-emerald-500/30 dark:text-emerald-200'
