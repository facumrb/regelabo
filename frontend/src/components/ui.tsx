import type { ReactNode } from 'react'

export function Tarjeta({ titulo, children }: { titulo: string; children: ReactNode }) {
  return (
    <div className="max-w-md mx-auto bg-dark-800/80 border border-slate-800 rounded-2xl p-6 space-y-5">
      <h2 className="text-xl font-bold text-white">{titulo}</h2>
      {children}
    </div>
  )
}

export function Campo({ etiqueta, children }: { etiqueta: string; children: ReactNode }) {
  return (
    <label className="block space-y-1.5">
      <span className="text-xs font-semibold text-slate-300">{etiqueta}</span>
      {children}
    </label>
  )
}

export function Aviso({ tipo, children }: { tipo: 'error' | 'ok'; children: ReactNode }) {
  const color =
    tipo === 'error'
      ? 'bg-rose-500/10 border-rose-500/30 text-rose-200'
      : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-200'
  return (
    <div role={tipo === 'error' ? 'alert' : 'status'} className={`px-3 py-2 rounded-lg border text-sm ${color}`}>
      {children}
    </div>
  )
}
