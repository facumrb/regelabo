import { useEffect, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { Aviso, Encabezado, EstadoChip, Pestanas } from '../../components/ui'
import { botonPrimario, botonSecundario, entrada, panel, vacio } from '../../components/estilos'
import { mensajeDeError } from '../../services/auth'
import { casosApi, type Caso } from '../../services/casos'
import {
  formatearFecha, simulacionesApi,
} from '../../services/simulaciones'
import EtiquetaPerfil from '../../components/EtiquetaPerfil'
import type { Simulacion } from '../../services/tiposSimulacion'
import { enlaceSuperponer, MAXIMO, MINIMO } from './Superponer'
import ListaComparativas from './ListaComparativas'

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
  const [parametros, setParametros] = useSearchParams()
  const pestana = parametros.get('ver') === 'comparativas' ? 'comparativas' : 'simulaciones'
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
  const caso = (s: Simulacion) => (s.caso_id ? aliasDelCaso(s.caso_id) ?? '…' : '—')
  const estimulo = ({ parametros: p }: Simulacion) => `${p.carrier_freq} Hz @ ${p.spl_level} dB · fm ${p.f_mod} Hz`
  const fibras = ({ parametros: p }: Simulacion) => `nH ${p.nH} / nM ${p.nM} / nL ${p.nL}`

  // Casilla para superponer; la fila entera lleva al detalle, así que el clic en la casilla no sigue de largo
  const casilla = (s: Simulacion) => {
    const marcada = elegidas.includes(s.id)
    const deshabilitada = s.estado !== 'completada' || (!marcada && elegidas.length >= MAXIMO)
    return (
      <label onClick={(e) => e.stopPropagation()}
        className={`grid place-items-center min-w-[44px] min-h-[44px] ${deshabilitada ? 'opacity-50' : 'cursor-pointer'}`}>
        <input type="checkbox" className="w-5 h-5 accent-[var(--acento)]" checked={marcada} disabled={deshabilitada}
          onChange={() => alternar(s.id)} />
        <span className="sr-only">
          {s.estado === 'completada' ? 'Elegir para superponer' : 'Sin terminar: no se puede superponer'}
        </span>
      </label>
    )
  }

  return (
    <div className="space-y-6">
      <Encabezado titulo="Historial de simulaciones" bajada="Todas tus simulaciones, de la más nueva a la más vieja.">
        <Link to="/simular" className={botonPrimario}>Nueva simulación</Link>
      </Encabezado>
      <Pestanas nombre="Qué ver" valor={pestana}
        opciones={[['simulaciones', 'Simulaciones'], ['comparativas', 'Comparativas']]}
        onCambio={(v) => setParametros(v === 'comparativas' ? { ver: v } : {}, { replace: true })} />
      {pestana === 'comparativas' ? <ListaComparativas /> : <>
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
        <>
          {/* Celular: una fila compacta por simulación, con la casilla de superponer a la izquierda */}
          <ul className="sm:hidden space-y-2" aria-label="Simulaciones">
            {simulaciones.map((s) => (
              <li key={s.id} className={`${panel} grid grid-cols-[44px_1fr] items-center py-2.5 pl-1 pr-4`}>
                {casilla(s)}
                <Link to={`/simulaciones/${s.id}`} className="min-w-0 block">
                  <span className="flex items-start justify-between gap-2">
                    <b className="font-medium text-tinta truncate">
                      <EtiquetaPerfil nombre={s.parametros.poles_profile} parte="perfil" />
                    </b>
                    <EstadoChip estado={s.estado} />
                  </span>
                  <span className="block text-sm text-tenue truncate">
                    <EtiquetaPerfil nombre={s.parametros.poles_profile} parte="tipo" /> · {caso(s)}
                  </span>
                  <span className="block font-mono text-xs text-tenue">{estimulo(s)}</span>
                  <span className="block text-xs text-tenue">
                    <span className="font-mono">{fibras(s)}</span> · {formatearFecha(s.creado_en)}
                    {s.reutilizada && ' · Resultado reutilizado'}
                  </span>
                </Link>
              </li>
            ))}
          </ul>

          {/* Tablet y PC: 6 columnas; el tipo va bajo el perfil y las fibras bajo el estímulo (8 no entraban) */}
          <table className="hidden sm:table w-full border-collapse" aria-label="Simulaciones">
            <thead>
              <tr>
                {['Superponer', 'Perfil auditivo', 'Caso', 'Estímulo', 'Estado', 'Pedida'].map((t, i) => (
                  <th key={t} scope="col"
                    className={`text-left text-xs font-medium uppercase tracking-wider text-tenue px-3 pb-3 ${i === 0 ? 'w-12' : ''}`}>
                    {i === 0 ? <span className="sr-only">{t}</span> : t}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {simulaciones.map((s) => (
                <tr key={s.id} onClick={() => navigate(`/simulaciones/${s.id}`)}
                  className="cursor-pointer hover:bg-acento-suave transition [&>td]:px-3 [&>td]:py-3 [&>td]:border-t [&>td]:border-linea [&>td]:align-top text-sm text-tinta">
                  <td className="!py-1">{casilla(s)}</td>
                  <td>
                    <Link to={`/simulaciones/${s.id}`} onClick={(e) => e.stopPropagation()} className="font-medium text-tinta hover:underline">
                      <EtiquetaPerfil nombre={s.parametros.poles_profile} parte="perfil" />
                    </Link>
                    <span className="block text-xs text-tenue">
                      <EtiquetaPerfil nombre={s.parametros.poles_profile} parte="tipo" />
                    </span>
                  </td>
                  <td>{caso(s)}</td>
                  <td className="font-mono">
                    {estimulo(s)}
                    <span className="block text-xs text-tenue">{fibras(s)}</span>
                  </td>
                  <td><EstadoChip estado={s.estado} /></td>
                  <td>
                    {formatearFecha(s.creado_en)}
                    {s.reutilizada && <span className="block text-xs text-tenue">Resultado reutilizado</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}

      {elegidas.length > 0 && (
        <div role="status"
          className={`sticky bottom-[calc(64px+env(safe-area-inset-bottom))] lg:bottom-4 z-10 flex flex-wrap items-center gap-3 px-4 py-3 rounded-xl border border-acento bg-panel shadow-lg`}>
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
      </>}
    </div>
  )
}
