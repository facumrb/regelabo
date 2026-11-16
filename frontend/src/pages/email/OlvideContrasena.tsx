import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { Aviso, Campo, Centrada } from '../../components/ui'
import { botonPrimario, entrada } from '../../components/estilos'
import { authApi, mensajeDeError } from '../../services/auth'

/** RN16: pide el mail para elegir una contraseña nueva. */
export default function OlvideContrasena() {
  const [email, setEmail] = useState('')
  const [respuesta, setRespuesta] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [enviando, setEnviando] = useState(false)

  const enviar = async (evento: FormEvent) => {
    evento.preventDefault()
    setError(null)
    setEnviando(true)
    try {
      setRespuesta(await authApi.olvide(email))
    } catch (e) {
      setError(mensajeDeError(e))
    } finally {
      setEnviando(false)
    }
  }

  return (
    <Centrada titulo="Recuperar contraseña" bajada="Te mandamos un enlace para elegir una contraseña nueva."
      pie={<Link to="/login" className="text-acento font-medium hover:underline">Volver a iniciar sesión</Link>}>
      {respuesta ? (
        <Aviso tipo="ok">{respuesta} Revisá también la carpeta de spam. El enlace vence en 1 hora.</Aviso>
      ) : (
        <form onSubmit={enviar} noValidate className="space-y-4">
          <Campo etiqueta="Email">
            <input className={entrada} type="email" autoComplete="username" value={email}
              onChange={(e) => setEmail(e.target.value)} />
          </Campo>
          {error && <Aviso tipo="error">{error}</Aviso>}
          <button type="submit" disabled={enviando} className={`${botonPrimario} w-full`}>
            {enviando ? 'Enviando…' : 'Enviar enlace'}
          </button>
        </form>
      )}
    </Centrada>
  )
}
