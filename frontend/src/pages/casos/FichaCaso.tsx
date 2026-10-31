import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { Aviso, Tarjeta, Volver } from '../../components/ui'
import { botonPrimario, botonSecundario } from '../../components/estilos'
import { mensajeDeError } from '../../services/auth'
import { casosApi, resumenDelCaso, type Caso } from '../../services/casos'
import FormularioCaso from './FormularioCaso'

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

  return (
    <div className="space-y-6">
    <Volver a="/casos" texto="Mis casos" />
    <Tarjeta titulo={caso.alias}>
      <p className="text-sm text-tenue">{resumenDelCaso(caso)}</p>
      {caso.notas && <p className="text-tinta whitespace-pre-wrap">{caso.notas}</p>}
      {error && <Aviso tipo="error">{error}</Aviso>}
      <div className="flex flex-wrap justify-end gap-2">
        <div className="flex gap-2">
          <button onClick={borrar} className={`${botonSecundario} hover:!border-rose-400 hover:!text-rose-700 dark:hover:!text-rose-300`}>
            Borrar
          </button>
          <button onClick={() => setEditando(true)} className={botonPrimario}>Editar</button>
        </div>
      </div>
    </Tarjeta>
    </div>
  )
}
