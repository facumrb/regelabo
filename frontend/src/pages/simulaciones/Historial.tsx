import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Aviso } from '../../components/ui'
import { botonSecundario, entrada } from '../../components/estilos'
import { mensajeDeError } from '../../services/auth'
import { casosApi, type Caso } from '../../services/casos'
import {
  COLOR_ESTADO, ETIQUETA_ESTADO, formatearFecha, resumenDeParametros, simulacionesApi,
} from '../../services/simulaciones'
import type { Simulacion } from '../../services/tiposSimulacion'

/** Todas las simulaciones del usuario, de la más nueva a la más vieja, de a 20 (igual que Mis casos). */
export default function Historial() {
  const [simulaciones, setSimulaciones] = useState<Simulacion[]>([])
  const [siguiente, setSiguiente] = useState<string | null>(null)
  const [casos, setCasos] = useState<Caso[]>([])
  const [casoId, setCasoId] = useState('') // '' = todos
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // despuesDe = null pide la primera página; con un id, agrega la siguiente al final
  const cargar = async (despuesDe: string | null, filtro: string) => {
    setCargando(true)
    setError(null)
    try {
      const pagina = await simulacionesApi.listar(despuesDe, filtro || null)
      setSimulaciones((anteriores) => (despuesDe ? [...anteriores, ...pagina.simulaciones] : pagina.simulaciones))
      setSiguiente(pagina.siguiente)
    } catch (e) {
      setError(mensajeDeError(e))
    } finally {
      setCargando(false)
    }
  }

  useEffect(() => {
    casosApi.listar(null, 100).then((pagina) => setCasos(pagina.casos)).catch(() => setCasos([]))
  }, [])

  useEffect(() => {
    cargar(null, casoId)
  }, [casoId])

  const aliasDelCaso = (id: string | null) => casos.find((c) => c.id === id)?.alias

  return (
    <div className="max-w-4xl mx-auto space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <h2 className="text-xl font-bold text-white">Historial de simulaciones</h2>
        <div className="flex items-center space-x-2">
          <select className={`${entrada} sm:w-56`} value={casoId} onChange={(e) => setCasoId(e.target.value)}>
            <option value="">Todos los casos</option>
            {casos.map((c) => (
              <option key={c.id} value={c.id}>{c.alias}</option>
            ))}
          </select>
          <Link to="/" className={botonSecundario}>Nueva simulación</Link>
        </div>
      </div>

      {error && <Aviso tipo="error">{error}</Aviso>}

      {!cargando && !error && simulaciones.length === 0 && (
        <p className="text-sm text-slate-400 text-center py-10 border border-dashed border-slate-800 rounded-2xl">
          {casoId ? 'Este caso todavía no tiene simulaciones.' : 'Todavía no hiciste simulaciones.'}
        </p>
      )}

      {simulaciones.length > 0 && (
        <ul className="divide-y divide-slate-800 border border-slate-800 rounded-2xl bg-dark-800/80 overflow-hidden">
          {simulaciones.map((s) => (
            <li key={s.id}>
              <Link to={`/simulaciones/${s.id}`}
                className="flex flex-col gap-1.5 px-4 py-3 hover:bg-slate-800/50 transition">
                <div className="flex items-center justify-between gap-3">
                  <span className="text-sm font-semibold text-white truncate">{resumenDeParametros(s.parametros)}</span>
                  <span className={`shrink-0 text-xs px-2.5 py-0.5 rounded-full border font-medium ${COLOR_ESTADO[s.estado]}`}>
                    {ETIQUETA_ESTADO[s.estado]}
                  </span>
                </div>
                <div className="text-xs text-slate-400 flex flex-wrap gap-x-3">
                  <span>{formatearFecha(s.creado_en)}</span>
                  {s.caso_id && <span>Caso: {aliasDelCaso(s.caso_id) ?? '…'}</span>}
                  {s.reutilizada && <span>Resultado reutilizado</span>}
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}

      {siguiente && (
        <div className="text-center">
          <button onClick={() => cargar(siguiente, casoId)} disabled={cargando} className={botonSecundario}>
            {cargando ? 'Cargando…' : 'Cargar más'}
          </button>
        </div>
      )}
    </div>
  )
}
