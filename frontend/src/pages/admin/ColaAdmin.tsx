import { useEffect, useState } from 'react'
import { Aviso } from '../../components/ui'
import { avisoAtencion, etiqueta, panel, vacio } from '../../components/estilos'
import { mensajeDeError } from '../../services/auth'
import { colaApi, type EstadoCola } from '../../services/admin'

const INTERVALO_COLA_MS = 10_000

/** "hace 2 min" / "hace 40 s" */
function hace(fecha: string): string {
  const segundos = Math.max(0, Math.round((Date.now() - new Date(fecha).getTime()) / 1000))
  return segundos < 60 ? `hace ${segundos} s` : `hace ${Math.floor(segundos / 60)} min`
}

function Dato({ titulo, valor, detalle }: { titulo: string; valor: string | number; detalle?: string }) {
  return (
    <div className={`${panel} p-4`}>
      <div className={etiqueta}>{titulo}</div>
      <div className="mt-1 text-2xl font-semibold text-tinta tabular-nums">{valor}</div>
      {detalle && <div className="text-xs text-tenue">{detalle}</div>}
    </div>
  )
}

/** Cola de simulaciones (decisión 028): solo lectura. Se actualiza cada 10 s con la pestaña a la vista. */
export default function ColaAdmin() {
  const [cola, setCola] = useState<EstadoCola | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const consultar = () => {
      if (document.visibilityState !== 'visible') return
      colaApi.estado().then((c) => { setCola(c); setError(null) }).catch((e) => setError(mensajeDeError(e)))
    }
    consultar()
    const intervalo = window.setInterval(consultar, INTERVALO_COLA_MS)
    document.addEventListener('visibilitychange', consultar)
    return () => {
      window.clearInterval(intervalo)
      document.removeEventListener('visibilitychange', consultar)
    }
  }, [])

  if (error) return <Aviso tipo="error">{error}</Aviso>
  if (!cola) return null

  return (
    <div className="space-y-6">
      {cola.worker_detenido && (
        <p role="alert" className={`px-4 py-3 rounded-xl border text-sm ${avisoAtencion}`}>
          <strong>El worker parece detenido:</strong> hay simulaciones esperando hace más de 2 minutos y ninguna se
          está ejecutando. Revisá que <code>worker.py</code> esté corriendo.
        </p>
      )}

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <Dato titulo="En cola" valor={cola.en_cola} detalle={`tope: ${cola.tope_cola}`} />
        <Dato titulo="Ejecutando" valor={cola.ejecutando}
          detalle={cola.worker_detenido === null ? 'cola vacía: no se sabe si el worker anda' : 'el worker anda'} />
        <Dato titulo="Ejecutadas (24 h)" valor={cola.completadas_24h}
          detalle={cola.duracion_promedio_s !== null ? `promedio ${Math.round(cola.duracion_promedio_s)} s` : undefined} />
        <Dato titulo="Desde la caché (24 h)" valor={cola.desde_cache_24h}
          detalle={cola.errores_24h ? `${cola.errores_24h} con error` : 'sin errores'} />
      </div>

      <section className="space-y-3" aria-labelledby="titulo-en-curso">
        <h2 id="titulo-en-curso" className={etiqueta}>En curso, en el orden en que las toma el worker</h2>
        {cola.en_curso.length === 0 ? (
          <p className={vacio}>No hay simulaciones en cola ni ejecutándose.</p>
        ) : (
          <ul className="space-y-2">
            {cola.en_curso.map((s) => (
              <li key={s.id} className={`${panel} px-4 py-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm`}>
                <span className="inline-flex items-center gap-2 text-tinta">
                  <span className={`w-2 h-2 rounded-full ${s.estado === 'ejecutando' ? 'bg-acento animate-pulse' : 'bg-tenue'}`}
                    aria-hidden="true" />
                  {s.estado === 'ejecutando' ? 'Ejecutando' : 'En cola'}
                </span>
                <span className="text-tenue break-all">{s.usuario_email}</span>
                <span className="ml-auto text-tenue tabular-nums">
                  {s.estado === 'ejecutando' && s.iniciada_en ? `empezó ${hace(s.iniciada_en)}` : `esperando, la pidió ${hace(s.creado_en)}`}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}
