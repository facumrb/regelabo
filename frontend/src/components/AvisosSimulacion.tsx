import { useEffect, useRef, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useSimulacionesEnCurso } from '../context/SimulacionesEnCurso'
import type { Simulacion } from '../services/tiposSimulacion'
import { panel } from './estilos'

const segundosDesde = (fecha: string) => Math.max(0, Math.round((Date.now() - new Date(fecha).getTime()) / 1000))

function textoEnCurso(s: Simulacion) {
  if (s.estado === 'en_cola') return `En cola${s.posicion ? ` · lugar ${s.posicion}` : ''}`
  // shortcut: cuenta con el reloj del navegador; si difiere mucho del servidor, el número se desfasa
  return `Simulando… ${segundosDesde(s.iniciada_en ?? s.creado_en)} s`
}

/** Indicador de la barra (decisión 024): qué está corriendo o qué terminó, sin cambiar de pantalla. */
export function IndicadorSimulaciones() {
  const { enCurso, terminadas, marcarTodasVistas } = useSimulacionesEnCurso()
  const [, setTic] = useState(0)

  // Los segundos de "Simulando…" se actualizan solos
  useEffect(() => {
    if (enCurso.length === 0) return
    const intervalo = setInterval(() => setTic((t) => t + 1), 1000)
    return () => clearInterval(intervalo)
  }, [enCurso.length])

  const clase = 'hidden md:inline-flex items-center gap-2 min-h-[36px] px-3 rounded-lg border border-linea bg-panel text-xs text-tinta hover:border-tenue'
  if (enCurso.length > 0) {
    const una = enCurso.length === 1
    return (
      <Link to={una ? `/simulaciones/${enCurso[0].id}` : '/simulaciones'} className={clase}>
        <span className="w-2 h-2 rounded-full bg-acento animate-pulse" aria-hidden="true" />
        {una ? textoEnCurso(enCurso[0]) : `${enCurso.length} simulaciones en curso`}
      </Link>
    )
  }
  if (terminadas.length > 0) {
    const una = terminadas.length === 1
    const fallo = terminadas.every((s) => s.estado === 'error')
    return (
      <Link to={una ? `/simulaciones/${terminadas[0].id}` : '/simulaciones'} className={clase}
        onClick={una ? undefined : marcarTodasVistas}>
        {fallo ? '⚠ No se pudo completar' : una ? '✓ Resultado listo' : `✓ ${terminadas.length} resultados listos`}
      </Link>
    )
  }
  return null
}

/**
 * Aviso discreto cuando termina una simulación y no se la está mirando: no mueve el foco ni cambia de
 * pantalla, y se va solo a los 8 s.
 */
export function AvisoSimulacionTerminada() {
  const { terminadas, esperada } = useSimulacionesEnCurso()
  const { pathname } = useLocation()
  const [aviso, setAviso] = useState<Simulacion | null>(null)
  const vistas = useRef(new Set<string>())

  useEffect(() => {
    const nueva = terminadas.find((s) => !vistas.current.has(s.id))
    terminadas.forEach((s) => vistas.current.add(s.id))
    if (!nueva) return
    // Si se la espera en Simular o ya se mira su detalle, la pantalla misma lo muestra
    const mirandola = (nueva.id === esperada && pathname === '/simular') || pathname === `/simulaciones/${nueva.id}`
    if (!mirandola) setAviso(nueva)
  }, [terminadas, esperada, pathname])

  useEffect(() => {
    if (!aviso) return
    const temporizador = setTimeout(() => setAviso(null), 8000)
    return () => clearTimeout(temporizador)
  }, [aviso])

  return (
    <div role="status" className="fixed z-50 right-4 left-4 sm:left-auto bottom-[calc(72px+env(safe-area-inset-bottom))] md:bottom-6">
      {aviso && (
        <div className={`${panel} aparecer shadow-xl px-4 py-2 flex items-center gap-3 text-sm text-tinta`}>
          <span>{aviso.estado === 'error' ? 'Tu simulación no se pudo completar' : 'Tu simulación terminó'}</span>
          <Link to={`/simulaciones/${aviso.id}`} onClick={() => setAviso(null)} className="inline-flex items-center min-h-[44px] font-medium text-acento hover:underline">
            {aviso.estado === 'error' ? 'Ver detalle' : 'Ver resultado'}
          </Link>
        </div>
      )}
    </div>
  )
}
