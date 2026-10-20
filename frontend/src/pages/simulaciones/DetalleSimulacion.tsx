import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import PerfilSimulado from '../../components/PerfilSimulado'
import PlotsPanel from '../../components/PlotsPanel'
import ResultsSummary from '../../components/ResultsSummary'
import { Aviso, Tarjeta } from '../../components/ui'
import { botonSecundario } from '../../components/estilos'
import { api } from '../../services/api'
import { mensajeDeError } from '../../services/auth'
import {
  COLOR_ESTADO, enCurso, ETIQUETA_ESTADO, formatearFecha, INTERVALO_CONSULTA_MS, resumenDeParametros,
  simulacionesApi,
} from '../../services/simulaciones'
import type { PerfilAuditivo, Simulacion } from '../../services/tiposSimulacion'

/** Una simulación: sus parámetros, su estado y, si terminó, los mismos gráficos del simulador. */
export default function DetalleSimulacion() {
  const { id = '' } = useParams()
  const [simulacion, setSimulacion] = useState<Simulacion | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [perfil, setPerfil] = useState<PerfilAuditivo | null>(null)
  const nombrePerfil = simulacion?.parametros.poles_profile

  // Las curvas del perfil para el aviso final; los personalizados viejos no las guardaron (404) y no se muestran
  useEffect(() => {
    setPerfil(null)
    if (!nombrePerfil) return
    let activo = true
    api.getProfile(nombrePerfil).then((p) => { if (activo) setPerfil(p) }).catch(() => {})
    return () => { activo = false }
  }, [nombrePerfil])

  // Mientras está en cola o ejecutando, se vuelve a consultar cada pocos segundos
  useEffect(() => {
    let activo = true
    let temporizador: ReturnType<typeof setTimeout> | undefined
    setSimulacion(null)
    setError(null)

    const consultar = async () => {
      try {
        const actual = await simulacionesApi.ver(id)
        if (!activo) return
        setSimulacion(actual)
        if (enCurso(actual.estado)) temporizador = setTimeout(consultar, INTERVALO_CONSULTA_MS)
      } catch (e) {
        if (activo) setError(mensajeDeError(e))
      }
    }
    consultar()

    return () => {
      activo = false
      clearTimeout(temporizador)
    }
  }, [id])

  if (error && !simulacion) {
    return (
      <Tarjeta titulo="Simulación no encontrada">
        <Aviso tipo="error">{error}</Aviso>
        <Link to="/simulaciones" className={botonSecundario}>Volver al historial</Link>
      </Tarjeta>
    )
  }
  if (!simulacion) return null

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="glass-panel rounded-2xl p-5 space-y-3">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-lg font-bold text-white">Simulación</h2>
          <span className={`text-xs px-3 py-1 rounded-full border font-medium ${COLOR_ESTADO[simulacion.estado]}`}>
            {ETIQUETA_ESTADO[simulacion.estado]}
            {simulacion.estado === 'en_cola' && simulacion.posicion ? ` (lugar ${simulacion.posicion})` : ''}
          </span>
        </div>
        {perfil && <p className="text-sm text-white">{perfil.etiqueta}</p>}
        <p className="font-mono text-sm text-cyan-300">{resumenDeParametros(simulacion.parametros)}</p>
        <div className="text-xs text-slate-400 flex flex-wrap gap-x-4 gap-y-1">
          <span>Pedida: {formatearFecha(simulacion.creado_en)}</span>
          {simulacion.iniciada_en && <span>Iniciada: {formatearFecha(simulacion.iniciada_en)}</span>}
          {simulacion.finalizada_en && <span>Terminó: {formatearFecha(simulacion.finalizada_en)}</span>}
          {simulacion.reutilizada && <span>Resultado reutilizado de una simulación idéntica</span>}
          {simulacion.caso_id && (
            <Link to={`/casos/${simulacion.caso_id}`} className="text-cyan-400 hover:underline">Ver el caso</Link>
          )}
        </div>
        {enCurso(simulacion.estado) && (
          <p className="text-xs text-slate-400">Esta página se actualiza sola cuando termine.</p>
        )}
        {simulacion.estado === 'error' && (
          <Aviso tipo="error">{simulacion.mensaje_error ?? 'La simulación no se pudo completar.'}</Aviso>
        )}
        <Link to="/simulaciones" className={botonSecundario}>← Historial</Link>
      </div>

      {simulacion.resultado && (
        <>
          {perfil && <PerfilSimulado perfil={perfil} />}
          <ResultsSummary result={simulacion.resultado} />
          <PlotsPanel result={simulacion.resultado} />
        </>
      )}
    </div>
  )
}
