import { useState, type FormEvent } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { Aviso, Campo, Centrada } from '../../components/ui'
import { botonPrimario, entrada } from '../../components/estilos'
import { useSesion } from '../../context/SesionContext'
import { authApi, mensajeDeError } from '../../services/auth'

/** Destino del enlace del mail de recuperación (RN16): /recuperar?token=... */
export default function RecuperarContrasena() {
  const [parametros] = useSearchParams()
  const { verificarSesion } = useSesion()
  const [nueva, setNueva] = useState('')
  const [repetida, setRepetida] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [listo, setListo] = useState(false)
  const [enviando, setEnviando] = useState(false)

  const enviar = async (evento: FormEvent) => {
    evento.preventDefault()
    setError(null)
    if (nueva !== repetida) {
      setError('Las contraseñas no coinciden.')
      return
    }
    setEnviando(true)
    try {
      await authApi.recuperar(parametros.get('token') ?? '', nueva)
      setListo(true)
      verificarSesion() // el backend cerró todas las sesiones: si había una abierta, se descarta
    } catch (e) {
      setError(mensajeDeError(e))
    } finally {
      setEnviando(false)
    }
  }

  return (
    <Centrada titulo="Contraseña nueva"
      pie={<Link to="/olvide" className="text-acento font-medium hover:underline">Pedir otro enlace</Link>}>
      {listo ? (
        <>
          <Aviso tipo="ok">Contraseña cambiada. Se cerraron tus sesiones abiertas.</Aviso>
          <Link to="/login" className={`${botonPrimario} w-full`}>Iniciar sesión</Link>
        </>
      ) : (
        <form onSubmit={enviar} noValidate className="space-y-4">
          <Campo etiqueta="Contraseña nueva">
            <input className={entrada} type="password" autoComplete="new-password" value={nueva}
              onChange={(e) => setNueva(e.target.value)} />
          </Campo>
          <Campo etiqueta="Repetir contraseña nueva">
            <input className={entrada} type="password" autoComplete="new-password" value={repetida}
              onChange={(e) => setRepetida(e.target.value)} />
          </Campo>
          {error && <Aviso tipo="error">{error}</Aviso>}
          <button type="submit" disabled={enviando} className={`${botonPrimario} w-full`}>
            {enviando ? 'Guardando…' : 'Guardar contraseña'}
          </button>
        </form>
      )}
    </Centrada>
  )
}
