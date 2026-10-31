import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Aviso, Encabezado, Tabla } from '../../components/ui'
import { botonPrimario, botonSecundario, vacio } from '../../components/estilos'
import { mensajeDeError } from '../../services/auth'
import { casosApi, type Caso } from '../../services/casos'

const SEXO = { femenino: 'Femenino', masculino: 'Masculino', otro: 'Otro' } as const

export default function MisCasos() {
  const [casos, setCasos] = useState<Caso[]>([])
  const [siguiente, setSiguiente] = useState<string | null>(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // despuesDe = null pide la primera página; con un id, agrega la siguiente al final
  const cargar = async (despuesDe: string | null) => {
    setCargando(true)
    setError(null)
    try {
      const pagina = await casosApi.listar(despuesDe)
      setCasos((anteriores) => (despuesDe ? [...anteriores, ...pagina.casos] : pagina.casos))
      setSiguiente(pagina.siguiente)
    } catch (e) {
      setError(mensajeDeError(e))
    } finally {
      setCargando(false)
    }
  }

  useEffect(() => {
    cargar(null)
  }, [])

  return (
    <div className="space-y-6">
      <Encabezado titulo="Mis casos" bajada="Los casos que cargaste, sin datos que identifiquen a nadie.">
        <Link to="/casos/nuevo" className={botonPrimario}>+ Nuevo caso</Link>
      </Encabezado>

      {error && <Aviso tipo="error">{error}</Aviso>}

      {!cargando && !error && casos.length === 0 && (
        <p className={vacio}>
          Todavía no creaste casos.
        </p>
      )}

      {casos.length > 0 && (
        <Tabla nombre="Casos" filas={casos} clave={(c) => c.id} enlace={(c) => `/casos/${c.id}`}
          columnas={[
            { titulo: 'Caso', celda: (c) => c.alias },
            { titulo: 'Edad', celda: (c) => (c.edad !== null ? `${c.edad} años` : '—'), mono: true },
            { titulo: 'Sexo', celda: (c) => (c.sexo ? SEXO[c.sexo] : '—') },
            { titulo: 'Creado', celda: (c) => new Date(c.creado_en).toLocaleDateString('es-AR') },
          ]} />
      )}

      {siguiente && (
        <div className="text-center">
          <button onClick={() => cargar(siguiente)} disabled={cargando} className={botonSecundario}>
            {cargando ? 'Cargando…' : 'Cargar más'}
          </button>
        </div>
      )}
    </div>
  )
}
