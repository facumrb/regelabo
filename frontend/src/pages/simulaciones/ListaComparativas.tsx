import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Aviso, Tabla } from '../../components/ui'
import { botonSecundario, vacio } from '../../components/estilos'
import { mensajeDeError } from '../../services/auth'
import { casosApi, type Caso } from '../../services/casos'
import { comparativasApi, enlaceComparativa, type Comparativa } from '../../services/comparativas'
import { formatearFecha } from '../../services/simulaciones'

/** Comparativas guardadas (decisión 025): todas, o solo las de un caso en su ficha. */
export default function ListaComparativas({ casoId }: { casoId?: string }) {
  const [comparativas, setComparativas] = useState<Comparativa[]>([])
  const [siguiente, setSiguiente] = useState<string | null>(null)
  const [casos, setCasos] = useState<Caso[]>([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const cargar = async (despuesDe: string | null) => {
    setCargando(true)
    setError(null)
    try {
      const pagina = await comparativasApi.listar(despuesDe, casoId)
      setComparativas((anteriores) => (despuesDe ? [...anteriores, ...pagina.comparativas] : pagina.comparativas))
      setSiguiente(pagina.siguiente)
    } catch (e) {
      setError(mensajeDeError(e))
    } finally {
      setCargando(false)
    }
  }

  useEffect(() => {
    cargar(null)
    if (!casoId) casosApi.listar(null, 100).then((p) => setCasos(p.casos)).catch(() => setCasos([]))
  }, [casoId])

  const alias = (id: string | null) => (id ? casos.find((c) => c.id === id)?.alias ?? '…' : '—')

  return (
    <div className="space-y-4">
      {error && <Aviso tipo="error">{error}</Aviso>}
      {!cargando && !error && comparativas.length === 0 && (
        <p className={vacio}>
          Todavía no guardaste comparativas. Elegí de 2 a 4 simulaciones en el Historial, superponelas y tocá
          "Guardar comparativa".
        </p>
      )}
      {comparativas.length > 0 && (
        <Tabla nombre="Comparativas" filas={comparativas} clave={(c) => c.id} enlace={(c) => enlaceComparativa(c.id)}
          columnas={[
            { titulo: 'Título', celda: (c) => c.titulo },
            ...(casoId ? [] : [{ titulo: 'Caso', celda: (c: Comparativa) => alias(c.caso_id) }]),
            { titulo: 'Simulaciones', mono: true, celda: (c) => c.simulacion_ids.length },
            { titulo: 'Guardada', celda: (c) => formatearFecha(c.creado_en) },
          ]} />
      )}
      {siguiente && (
        <div className="text-center">
          <button onClick={() => cargar(siguiente)} disabled={cargando} className={botonSecundario}>
            {cargando ? 'Cargando…' : 'Cargar más'}
          </button>
        </div>
      )}
      {casoId && comparativas.length > 0 && (
        <p className="text-sm text-tenue">
          Para armar otra, elegí simulaciones en el <Link to="/simulaciones" className="text-acento hover:underline">Historial</Link>.
        </p>
      )}
    </div>
  )
}
