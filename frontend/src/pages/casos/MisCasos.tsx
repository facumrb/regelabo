import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Aviso } from '../../components/ui'
import { botonPrimario, botonSecundario } from '../../components/estilos'
import { mensajeDeError } from '../../services/auth'
import { casosApi, resumenDelCaso, type Caso } from '../../services/casos'

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
    <div className="max-w-3xl mx-auto space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-white">Mis casos</h2>
        <Link to="/casos/nuevo" className={botonPrimario}>+ Nuevo caso</Link>
      </div>

      {error && <Aviso tipo="error">{error}</Aviso>}

      {!cargando && !error && casos.length === 0 && (
        <p className="text-sm text-slate-400 text-center py-10 border border-dashed border-slate-800 rounded-2xl">
          Todavía no creaste casos.
        </p>
      )}

      {casos.length > 0 && (
        <ul className="divide-y divide-slate-800 border border-slate-800 rounded-2xl bg-dark-800/80 overflow-hidden">
          {casos.map((caso) => (
            <li key={caso.id}>
              <Link to={`/casos/${caso.id}`}
                className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 px-4 py-3 hover:bg-slate-800/50 transition">
                <span className="text-sm font-semibold text-white">{caso.alias}</span>
                <span className="text-xs text-slate-400">{resumenDelCaso(caso)}</span>
              </Link>
            </li>
          ))}
        </ul>
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
