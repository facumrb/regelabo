import { useEffect, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { Aviso, Encabezado, EstadoChip, Tabla } from '../../components/ui'
import { botonPrimario, botonSecundario, entrada, vacio } from '../../components/estilos'
import { mensajeDeError } from '../../services/auth'
import { casosApi, type Caso } from '../../services/casos'
import {
  formatearFecha, simulacionesApi,
} from '../../services/simulaciones'
import EtiquetaPerfil from '../../components/EtiquetaPerfil'
import type { Simulacion } from '../../services/tiposSimulacion'
import { enlaceSuperponer, MAXIMO, MINIMO } from './Superponer'

/** Todas las simulaciones del usuario, de la más nueva a la más vieja, de a 20 (igual que Mis casos). */
export default function Historial() {
  const [simulaciones, setSimulaciones] = useState<Simulacion[]>([])
  const [siguiente, setSiguiente] = useState<string | null>(null)
  const [casos, setCasos] = useState<Caso[]>([])
  const [casoId, setCasoId] = useState('') // '' = todos
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()
  // "Superponer con…" desde el detalle llega como ?superponer=<id>, ya marcada (decisión 025)
  const [parametros] = useSearchParams()
  const [elegidas, setElegidas] = useState<string[]>(() => parametros.get('superponer')?.split(',').slice(0, MAXIMO) ?? [])
  const alternar = (id: string) =>
    setElegidas((actual) => (actual.includes(id) ? actual.filter((x) => x !== id) : [...actual, id]))

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
    <div className="space-y-6">
      <Encabezado titulo="Historial de simulaciones" bajada="Todas tus simulaciones, de la más nueva a la más vieja.">
        <Link to="/simular" className={botonPrimario}>Nueva simulación</Link>
      </Encabezado>
      <label className="block sm:max-w-xs">
        <span className="block text-sm text-tenue mb-1.5">Caso</span>
        <select className={entrada} value={casoId} onChange={(e) => setCasoId(e.target.value)}>
          <option value="">Todos los casos</option>
          {casos.map((c) => (
            <option key={c.id} value={c.id}>{c.alias}</option>
          ))}
        </select>
      </label>

      {error && <Aviso tipo="error">{error}</Aviso>}

      {!cargando && !error && simulaciones.length === 0 && (
        <p className={vacio}>
          {casoId ? 'Este caso todavía no tiene simulaciones.' : 'Todavía no hiciste simulaciones.'}
        </p>
      )}

      {simulaciones.length > 0 && (
        <Tabla nombre="Simulaciones" filas={simulaciones} clave={(s) => s.id} enlace={(s) => `/simulaciones/${s.id}`}
          columnas={[
            { titulo: 'Tipo de caso', celda: (s) => <EtiquetaPerfil nombre={s.parametros.poles_profile} parte="tipo" /> },
            { titulo: 'Perfil auditivo', celda: (s) => <EtiquetaPerfil nombre={s.parametros.poles_profile} parte="perfil" /> },
            { titulo: 'Caso', celda: (s) => (s.caso_id ? aliasDelCaso(s.caso_id) ?? '…' : '—') },
            { titulo: 'Estímulo', mono: true,
              celda: (s) => `${s.parametros.carrier_freq} Hz @ ${s.parametros.spl_level} dB · fm ${s.parametros.f_mod} Hz` },
            { titulo: 'Fibras', mono: true, celda: (s) => `nH ${s.parametros.nH} / nM ${s.parametros.nM} / nL ${s.parametros.nL}` },
            { titulo: 'Estado', celda: (s) => <EstadoChip estado={s.estado} /> },
            { titulo: 'Pedida', celda: (s) => <>{formatearFecha(s.creado_en)}{s.reutilizada && <span className="block text-xs text-tenue">Resultado reutilizado</span>}</> },
            { titulo: 'Superponer', celda: (s) => {
              const marcada = elegidas.includes(s.id)
              const deshabilitada = s.estado !== 'completada' || (!marcada && elegidas.length >= MAXIMO)
              return (
                // la fila entera lleva al detalle: la casilla no tiene que disparar eso
                <label onClick={(e) => e.stopPropagation()}
                  className={`inline-flex items-center gap-2 min-h-[44px] ${deshabilitada ? 'opacity-50' : 'cursor-pointer'}`}>
                  <input type="checkbox" className="w-5 h-5 accent-[var(--acento)]" checked={marcada} disabled={deshabilitada}
                    onChange={() => alternar(s.id)} />
                  <span className="text-xs text-tenue">{s.estado === 'completada' ? 'Elegir' : 'Sin terminar'}</span>
                </label>
              )
            } },
          ]} />
      )}

      {elegidas.length > 0 && (
        <div role="status"
          className={`sticky bottom-[calc(64px+env(safe-area-inset-bottom))] md:bottom-4 z-10 flex flex-wrap items-center gap-3 px-4 py-3 rounded-xl border border-acento bg-panel shadow-lg`}>
          <span className="text-sm text-tinta">
            {elegidas.length} de {MAXIMO} elegidas{elegidas.length < MINIMO && ` · elegí al menos ${MINIMO}`}
          </span>
          <button type="button" onClick={() => setElegidas([])} className="ml-auto text-sm text-tenue hover:text-tinta min-h-[44px] px-2">
            Limpiar
          </button>
          <button type="button" disabled={elegidas.length < MINIMO} onClick={() => navigate(enlaceSuperponer(elegidas))}
            className={botonPrimario}>
            Superponer
          </button>
        </div>
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
