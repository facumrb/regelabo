import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { Aviso, Tarjeta, Volver } from '../../components/ui'
import { botonPrimario, botonSecundario } from '../../components/estilos'
import { mensajeDeError } from '../../services/auth'
import { casosApi, resumenDelCaso, type Caso } from '../../services/casos'
import FormularioCaso from './FormularioCaso'
import AudiogramasDelCaso from './AudiogramasDelCaso'
import SimulacionesDelCaso from './SimulacionesDelCaso'
import ListaComparativas from '../simulaciones/ListaComparativas'
import { etiqueta, panel } from '../../components/estilos'

/** Ver, editar y borrar un caso. Un caso ajeno o borrado llega como 404 y se muestra igual que uno inexistente. */
export default function FichaCaso() {
  const { id = '' } = useParams()
  const navigate = useNavigate()
  const [caso, setCaso] = useState<Caso | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [editando, setEditando] = useState(false)

  useEffect(() => {
    setCaso(null)
    setError(null)
    casosApi.ver(id).then(setCaso).catch((e) => setError(mensajeDeError(e)))
  }, [id])

  const borrar = async () => {
    if (!caso || !window.confirm(`¿Borrar el caso "${caso.alias}"?`)) return
    try {
      await casosApi.borrar(caso.id)
      navigate('/casos', { replace: true })
    } catch (e) {
      setError(mensajeDeError(e))
    }
  }

  if (error && !caso) {
    return (
      <Tarjeta titulo="Caso no encontrado">
        <Aviso tipo="error">{error}</Aviso>
        <Link to="/casos" className={botonSecundario}>Volver a mis casos</Link>
      </Tarjeta>
    )
  }
  if (!caso) return null

  if (editando) {
    return (
      <Tarjeta titulo="Editar caso">
        <FormularioCaso
          inicial={caso}
          alGuardar={async (datos) => {
            setCaso(await casosApi.editar(caso.id, datos))
            setEditando(false)
          }}
          alCancelar={() => setEditando(false)}
        />
      </Tarjeta>
    )
  }

  // Todos los bloques del mismo ancho, en una columna (decisión 033)
  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <Volver a="/casos" texto="Mis casos" />
      <section className={`${panel} p-6 space-y-3`}>
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h1 className="text-xl font-semibold text-tinta">{caso.alias}</h1>
            <p className="text-sm text-tenue">{resumenDelCaso(caso)}</p>
          </div>
          <div className="flex gap-2">
            <button onClick={borrar} className={`${botonSecundario} hover:!border-rose-400 hover:!text-rose-700 dark:hover:!text-rose-300`}>
              Borrar
            </button>
            <button onClick={() => setEditando(true)} className={botonPrimario}>Editar</button>
          </div>
        </div>
        {caso.notas && <p className="text-tinta whitespace-pre-wrap">{caso.notas}</p>}
        {error && <Aviso tipo="error">{error}</Aviso>}
      </section>
      <AudiogramasDelCaso casoId={caso.id} />
      <SimulacionesDelCaso casoId={caso.id} />
      <section aria-labelledby="titulo-comparativas" className="space-y-3">
        <h2 id="titulo-comparativas" className={etiqueta}>Comparativas</h2>
        <ListaComparativas casoId={caso.id} />
      </section>
    </div>
  )
}
