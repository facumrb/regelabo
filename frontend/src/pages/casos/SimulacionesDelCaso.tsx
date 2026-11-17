import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Aviso, EstadoChip, Tabla } from '../../components/ui'
import { botonPrimario, botonSecundario, etiqueta, vacio } from '../../components/estilos'
import EtiquetaPerfil from '../../components/EtiquetaPerfil'
import { mensajeDeError } from '../../services/auth'
import { formatearFecha, simulacionesApi } from '../../services/simulaciones'
import type { Simulacion } from '../../services/tiposSimulacion'
import type { EstadoNuevaSimulacion } from '../../App'

/** Simulaciones pedidas con este caso elegido, de la más nueva a la más vieja, de a 20 (como el Historial). */
export default function SimulacionesDelCaso({ casoId }: { casoId: string }) {
  const [simulaciones, setSimulaciones] = useState<Simulacion[]>([])
  const [siguiente, setSiguiente] = useState<string | null>(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const cargar = async (despuesDe: string | null) => {
    setCargando(true)
    setError(null)
    try {
      const pagina = await simulacionesApi.listar(despuesDe, casoId)
      setSimulaciones((anteriores) => (despuesDe ? [...anteriores, ...pagina.simulaciones] : pagina.simulaciones))
      setSiguiente(pagina.siguiente)
    } catch (e) {
      setError(mensajeDeError(e))
    } finally {
      setCargando(false)
    }
  }

  useEffect(() => {
    cargar(null)
  }, [casoId])

  return (
    <section aria-labelledby="titulo-simulaciones" className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 id="titulo-simulaciones" className={etiqueta}>Simulaciones</h2>
        <Link to="/simular" state={{ casoId } satisfies EstadoNuevaSimulacion} className={botonPrimario}>
          Nueva simulación
        </Link>
      </div>
      {error && <Aviso tipo="error">{error}</Aviso>}
      {!cargando && !error && simulaciones.length === 0 && (
        <p className={vacio}>Este caso todavía no tiene simulaciones.</p>
      )}
      {simulaciones.length > 0 && (
        <Tabla nombre="Simulaciones del caso" filas={simulaciones} clave={(s) => s.id} enlace={(s) => `/simulaciones/${s.id}`}
          columnas={[
            { titulo: 'Perfil auditivo', celda: (s) => <EtiquetaPerfil nombre={s.parametros.poles_profile} parte="perfil" /> },
            { titulo: 'Estímulo', mono: true,
              celda: (s) => `${s.parametros.carrier_freq} Hz @ ${s.parametros.spl_level} dB · fm ${s.parametros.f_mod} Hz` },
            { titulo: 'Estado', celda: (s) => <EstadoChip estado={s.estado} /> },
            { titulo: 'Pedida', celda: (s) => formatearFecha(s.creado_en) },
          ]} />
      )}
      {siguiente && (
        <div className="text-center">
          <button onClick={() => cargar(siguiente)} disabled={cargando} className={botonSecundario}>
            {cargando ? 'Cargando…' : 'Cargar más'}
          </button>
        </div>
      )}
    </section>
  )
}
