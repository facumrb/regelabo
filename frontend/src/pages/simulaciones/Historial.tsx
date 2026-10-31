import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Aviso, Encabezado, EstadoChip, Tabla } from '../../components/ui'
import { botonPrimario, botonSecundario, entrada, vacio } from '../../components/estilos'
import { mensajeDeError } from '../../services/auth'
import { casosApi, type Caso } from '../../services/casos'
import {
  formatearFecha, simulacionesApi,
} from '../../services/simulaciones'
import EtiquetaPerfil from '../../components/EtiquetaPerfil'
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
          ]} />
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
